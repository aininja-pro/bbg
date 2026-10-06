"""Data transformation service for unpivoting and enriching rebate data."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

from openpyxl.utils import get_column_letter
from app.utils.exceptions import TransformationError
from app.utils.text_cleaner import clean_text_field, clean_zip_postal


def normalize_column_header(name: Any) -> str:
    """Make a spreadsheet header easy to compare.

    Lowercase, trim, and treat "Single Family / Multi-unit" the same as
    "single family/multi-unit". Also folds line breaks and unusual slash
    characters, which show up when a heading is wrapped in the cell.
    """
    text = str(name)
    text = text.replace('\u00a0', ' ').replace('\n', ' ').replace('\r', ' ')
    for slash in ('\u2044', '\u2215', '\uff0f', '\\'):
        text = text.replace(slash, '/')
    text = text.lower().strip()
    text = text.replace('_', ' ')
    text = re.sub(r'\s*/\s*', '/', text)
    text = re.sub(r'\s+', ' ', text)
    return text


# Column G is the address-type column. Builders use several different headings
# for it. All of these must be recognized as address_type during import.
ADDRESS_TYPE_HEADERS = {
    'multi-unit/comm',
    'multi-unit',
    'multi unit',
    'residential',
    'residential or multi-unit',
    'single family/multi-unit',
    'single family/multi unit',
    'single-family/multi-unit',
}


def is_address_type_header(name: Any) -> bool:
    """Return True when a header is one of the known address-type labels."""
    return normalize_column_header(name) in ADDRESS_TYPE_HEADERS


# Column G (the 7th column) is the address-type column in the Usage-Reporting
# sheet. Builders rename that heading. The column is still address type.
COLUMN_G_INDEX = 6


def mark_column_g_as_address_type(headers: List[Any]) -> List[Any]:
    """Return headers with column G labeled as the address-type column."""
    renamed = list(headers)
    if len(renamed) > COLUMN_G_INDEX:
        renamed[COLUMN_G_INDEX] = 'address_type'
    return renamed


# Words that identify the home/job columns (not the product columns).
BASE_COLUMN_HINTS = [
    'date', 'jobcode', 'job code', 'job_code',
    'address', 'city', 'state', 'zip', 'postal',
    'multi-unit', 'comm', 'address_type', 'occupancy',
    'residential',
]


def make_column_names_unique(names: List[Any]) -> List[str]:
    """Give every column its own name.

    Rebate files repeat headings such as "Drywall" and "Windows". Pandas
    cannot unpivot a sheet while two columns share a name.
    """
    seen = {}
    unique = []
    for name in names:
        key = "" if name is None else str(name)
        seen[key] = seen.get(key, 0) + 1
        if seen[key] == 1:
            unique.append(key)
        else:
            unique.append(f"{key}__{seen[key]}")
    return unique


def is_base_data_column(column_name: Any) -> bool:
    """Return True when this column is home data, not a product quantity."""
    if column_name in ('_date_sort', '_product_order'):
        return True
    if is_address_type_header(column_name):
        return True
    col_lower = normalize_column_header(column_name)
    return any(hint in col_lower for hint in BASE_COLUMN_HINTS)


class DataTransformer:
    """Transforms wide-format rebate data to long format and enriches it."""

    # Standard output columns for transformed data (18 columns with new proof points)
    # Rob's requested order: pp_receipt and pp_brand_name BEFORE pp_dist_subcontractor,
    # pp_prod_purchase AFTER pp_dist_subcontractor
    OUTPUT_COLUMNS = [
        'member_name',                # 1
        'bbg_member_id',              # 2
        'confirmed_occupancy',        # 3
        'job_code',                   # 4
        'address1',                   # 5
        'city',                       # 6
        'state',                      # 7
        'zip_postal',                 # 8
        'address_type',               # 9
        'quantity',                   # 10
        'product_id',                 # 11
        'supplier_name',              # 12
        'tradenet_supplier_id',       # 13
        'pp_receipt',                 # 14 - NEW (optional, BEFORE pp_dist_subcontractor)
        'pp_brand_name',              # 15 - NEW (optional, BEFORE pp_dist_subcontractor)
        'pp_dist_subcontractor',      # 16 - Existing subcontractor field
        'pp_prod_purchase',           # 17 - NEW (optional, AFTER pp_dist_subcontractor)
        'tradenet_company_id',        # 18
    ]

    # Note: product_name and proof_point are enriched but not included in final output

    def __init__(self):
        """Initialize the data transformer."""
        self.df: Optional[pd.DataFrame] = None
        self.warnings: List[Dict[str, Any]] = []

    def extract_data_from_sheet(
        self,
        sheet: Worksheet,
        header_row: int,
        active_products: Dict[int, str],
        metadata: Dict[str, str]
    ) -> pd.DataFrame:
        """Extract data from Excel sheet starting from header row.

        Args:
            sheet: The Excel worksheet
            header_row: Row number where headers are located
            active_products: Dictionary of column index -> product ID
            metadata: Dictionary with bbg_member_id and member_name

        Returns:
            DataFrame with extracted data
        """
        # Get all data from sheet starting at header row
        data = []
        headers = []

        # Extract headers via streaming iter_rows (read_only-compatible).
        header_values = next(
            sheet.iter_rows(min_row=header_row, max_row=header_row, values_only=True),
            None,
        )
        if header_values is None:
            raise TransformationError(f"Header row {header_row} not found in sheet")
        for col_idx, value in enumerate(header_values, start=1):
            headers.append(value if value else f"Column_{col_idx}")

        # Infer names for blank headers in base columns (A–G only).
        # Product columns beyond G are handled by active_products detection.
        for i, header in enumerate(headers[:7]):
            if header and str(header).startswith('Column_'):
                col_num = int(str(header).split('_')[1])
                col_letter = get_column_letter(col_num)
                inferred_name = None

                # Infer "Address" if positioned between job code and city
                prev = str(headers[i - 1]).lower().strip() if i > 0 and headers[i - 1] else ''
                nxt = str(headers[i + 1]).lower().strip() if i < len(headers) - 1 and headers[i + 1] else ''
                if any(k in prev for k in ['job code', 'job name', 'jobcode']) and 'city' in nxt:
                    inferred_name = 'Address'
                    headers[i] = inferred_name

                inferred_suffix = f" — inferred as '{inferred_name}'" if inferred_name else " — could not infer name"
                self.warnings.append({
                    'type': 'blank_column_header',
                    'column_position': col_num,
                    'inferred_name': inferred_name,
                    'message': f"Column {col_letter} has a blank header{inferred_suffix}"
                })

        # Column G stays the address-type column even when its heading changes.
        headers = mark_column_g_as_address_type(headers)
        for warning in self.warnings:
            if warning.get('column_position') == 7 and not warning.get('inferred_name'):
                warning['inferred_name'] = 'address_type'
                warning['message'] = "Column G has a blank header — inferred as 'address_type'"

        # Extract data rows (starting after header).
        # Early-exit after a run of consecutive blank rows protects against
        # files whose sheet range is inflated down to Excel's 1,048,576-row
        # limit (common when formatting is applied to entire columns).
        BLANK_ROW_EXIT_THRESHOLD = 200
        consecutive_blank = 0
        for row in sheet.iter_rows(min_row=header_row + 1, values_only=True):
            if all(cell is None or cell == '' for cell in row):
                consecutive_blank += 1
                if consecutive_blank >= BLANK_ROW_EXIT_THRESHOLD:
                    break
                continue
            consecutive_blank = 0
            data.append(row)

        if not data:
            raise TransformationError("No data found below header row")

        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)

        return df

    def unpivot_products(
        self,
        df: pd.DataFrame,
        active_products: Dict[int, Dict[str, str]],
        metadata: Dict[str, str]
    ) -> pd.DataFrame:
        """Unpivot wide format to long format for product columns.

        Args:
            df: Wide-format DataFrame
            active_products: Dictionary of column index -> dict with product_id and distributor
            metadata: Dictionary with member info

        Returns:
            Long-format DataFrame with one row per product per transaction
        """
        # Repeated headings ("Drywall", "Windows") must be unique before unpivot.
        new_column_names = make_column_names_unique(list(df.columns))

        # Get product column names from indices (preserve Excel column order)
        product_columns = []
        product_id_map = {}
        distributor_map = {}
        product_order_map = {}  # Maps product_id to its Excel column order

        # Sort active_products by column index to preserve left-to-right order
        sorted_products = sorted(active_products.items(), key=lambda x: x[0])

        for order_num, (col_idx, product_info) in enumerate(sorted_products):
            pos = col_idx - 1  # Excel columns are 1-indexed
            if pos < len(new_column_names):
                # Include the column number so two columns with the same heading
                # and the same product id do not collapse into one name.
                unique_col_name = f"{new_column_names[pos]}_{product_info['product_id']}_{col_idx}"
                new_column_names[pos] = unique_col_name
                product_columns.append(unique_col_name)
                product_id_map[unique_col_name] = product_info['product_id']
                distributor_map[unique_col_name] = product_info.get('distributor')
                product_order_map[product_info['product_id']] = order_num

        if not product_columns:
            raise TransformationError("No product columns found to unpivot")

        df.columns = new_column_names

        # Home data is columns A–G. Column G is the address type even when the
        # heading says something new. Later columns are products, so a heading
        # like "Single Family" must not be pulled in as home data.
        base_columns = []
        for pos in range(min(7, len(df.columns))):
            name = df.columns[pos]
            if name not in product_columns:
                base_columns.append(name)
        for helper in ('_date_sort', '_product_order'):
            if helper in list(df.columns) and helper not in base_columns and helper not in product_columns:
                base_columns.append(helper)

        # Unpivot using pandas melt
        try:
            df_long = pd.melt(
                df,
                id_vars=base_columns,
                value_vars=product_columns,
                var_name='product_column',
                value_name='quantity'
            )
        except Exception as e:
            raise TransformationError(f"Failed to unpivot data: {str(e)}. Base columns: {len(base_columns)}, Product columns: {len(product_columns)}")

        # Add product ID and distributor based on column name
        df_long['product_id'] = df_long['product_column'].map(product_id_map)
        df_long['pp_dist_subcontractor'] = df_long['product_column'].map(distributor_map)

        # Add new proof point columns (empty by default, populated via rules)
        df_long['pp_receipt'] = ''
        df_long['pp_brand_name'] = ''
        df_long['pp_prod_purchase'] = ''

        # Add product order for sorting (to match Excel column order)
        df_long['_product_order'] = df_long['product_id'].map(product_order_map)

        # Add metadata
        df_long['bbg_member_id'] = metadata['bbg_member_id']
        df_long['member_name'] = metadata['member_name']

        # Filter out junk rows
        # 1. Remove rows with null/zero/empty quantity
        df_long = df_long[
            (df_long['quantity'].notna()) &
            (df_long['quantity'] != 0) &
            (df_long['quantity'] != '')
        ]

        # 2. Remove rows with non-numeric quantities (like "Hide", "Show", etc.)
        def is_valid_quantity(val):
            """Check if quantity is a valid number."""
            try:
                float(val)
                return True
            except (ValueError, TypeError):
                return False

        df_long = df_long[df_long['quantity'].apply(is_valid_quantity)]

        # 3. Remove rows with missing dates (these are usually Excel UI elements)
        # Check for either 'date' or 'confirmed_occupancy' column
        date_col = 'confirmed_occupancy' if 'confirmed_occupancy' in df_long.columns else 'date'
        if date_col in df_long.columns:
            df_long = df_long[df_long[date_col].notna()]

        # Drop the temporary product_column
        df_long = df_long.drop(columns=['product_column'])

        return df_long

    def convert_excel_dates(self, df: pd.DataFrame, date_column: str = 'Date') -> pd.DataFrame:
        """Convert Excel serial dates to MM/DD/YYYY format.

        Args:
            df: DataFrame with date column
            date_column: Name of the date column

        Returns:
            DataFrame with converted dates
        """
        if date_column not in df.columns:
            return df  # No date column to convert

        def convert_date(val):
            """Convert various date formats to M/D/YY string (no leading zeros)."""
            if pd.isna(val) or val == '':
                return None

            try:
                # If it's already a datetime
                if isinstance(val, datetime):
                    return val.strftime('%-m/%-d/%y')  # Mac/Linux: no leading zeros, 2-digit year

                # If it's an Excel serial number
                if isinstance(val, (int, float)):
                    # Excel epoch starts at 1899-12-30
                    dt = pd.Timestamp('1899-12-30') + pd.Timedelta(days=val)
                    return dt.strftime('%-m/%-d/%y')

                # Try parsing as string
                dt = pd.to_datetime(val)
                return dt.strftime('%-m/%-d/%y')

            except Exception:
                return str(val)  # Return as-is if conversion fails

        df[date_column] = df[date_column].apply(convert_date)
        return df

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected output format.

        Args:
            df: DataFrame with various column names

        Returns:
            DataFrame with standardized column names
        """
        # Mapping of common variations to standard names
        column_mapping = {
            'date': 'confirmed_occupancy',  # Date becomes confirmed_occupancy in output
            'job code': 'job_code',
            'jobcode': 'job_code',
            'job name': 'job_name',
            'jobname': 'job_name',
            'address': 'address1',
            'address 1': 'address1',
            'address1': 'address1',
            'address 2': 'address2',
            'address2': 'address2',
            'city': 'city',
            'state': 'state',
            'zip': 'zip_postal',
            'zipcode': 'zip_postal',
            'postal': 'zip_postal',
            'zip code': 'zip_postal',
            'postal code': 'zip_postal',
            'multi-unit/comm': 'address_type',
            'multi-unit': 'address_type',
            'multi unit': 'address_type',
            'residential': 'address_type',
            'residential or multi-unit': 'address_type',
            'single family/multi-unit': 'address_type',
            'single family/multi unit': 'address_type',
            'single-family/multi-unit': 'address_type',
            'qty': 'quantity',
            'quantity': 'quantity',
        }

        # Rename columns (case-insensitive, ignoring extra spaces around "/")
        new_columns = {}
        for col in df.columns:
            col_key = normalize_column_header(col)
            if col_key in column_mapping:
                new_columns[col] = column_mapping[col_key]
            elif is_address_type_header(col):
                new_columns[col] = 'address_type'

        if new_columns:
            df = df.rename(columns=new_columns)

        # Apply address_type business rule: blank = "RESIDENTIAL"
        if 'address_type' in df.columns:
            df['address_type'] = df['address_type'].apply(
                lambda x: 'RESIDENTIAL' if pd.isna(x) or x == '' else str(x).strip()
            )

        return df

    def clean_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean address and related text fields imported from spreadsheets."""
        text_columns = [
            "address1",
            "address2",
            "city",
            "state",
            "job_code",
            "job_name",
            "address_type",
        ]

        for column in text_columns:
            if column in df.columns:
                df[column] = df[column].apply(clean_text_field)

        if "zip_postal" in df.columns:
            df["zip_postal"] = df["zip_postal"].apply(clean_zip_postal)

        return df

    def add_placeholder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add any missing columns with null values.

        Args:
            df: DataFrame that may be missing some standard columns

        Returns:
            DataFrame with all standard columns
        """
        for col in self.OUTPUT_COLUMNS:
            if col not in df.columns:
                df[col] = None

        # Reorder to match standard output
        df = df[self.OUTPUT_COLUMNS]

        return df

    def transform(
        self,
        sheet: Worksheet,
        header_row: int,
        active_products: Dict[int, Dict[str, str]],
        metadata: Dict[str, str]
    ) -> pd.DataFrame:
        """Complete transformation pipeline.

        Args:
            sheet: Excel worksheet
            header_row: Row number with headers
            active_products: Product column mapping
            metadata: Member metadata

        Returns:
            Transformed DataFrame ready for enrichment
        """
        # Step 1: Extract data
        df = self.extract_data_from_sheet(sheet, header_row, active_products, metadata)

        # Step 2: Store original dates for sorting BEFORE converting to strings
        if 'Date' in df.columns:
            df['_date_sort'] = df['Date']  # Keep as datetime for sorting

        # Step 2b: Convert dates to string format
        df = self.convert_excel_dates(df)

        # Step 3: Standardize column names (Date → confirmed_occupancy)
        df = self.standardize_columns(df)

        # Step 3b: Clean address and related text fields
        df = self.clean_text_fields(df)

        # Step 4: Unpivot products
        df = self.unpivot_products(df, active_products, metadata)

        # Step 5: Add missing columns
        df = self.add_placeholder_columns(df)

        # Step 6: Sort rows to match expected output format
        # Group by address (date + job_code) then by Excel column order

        # Convert confirmed_occupancy back to datetime for proper sorting
        if 'confirmed_occupancy' in df.columns:
            df['_date_sort_temp'] = pd.to_datetime(df['confirmed_occupancy'], format='%m/%d/%y', errors='coerce')

        sort_columns = []
        if '_date_sort_temp' in df.columns:
            sort_columns.append('_date_sort_temp')
        if 'job_code' in df.columns:
            sort_columns.append('job_code')
        if '_product_order' in df.columns:
            sort_columns.append('_product_order')  # Use Excel column order

        if sort_columns:
            df = df.sort_values(by=sort_columns).reset_index(drop=True)
            # Remove temporary sorting columns
            df = df.drop(columns=['_product_order', '_date_sort', '_date_sort_temp'], errors='ignore')

        # Step 7: Format numeric fields (remove unnecessary decimals)
        # Convert zip_postal to int and then to string to avoid .0 in CSV output
        if 'zip_postal' in df.columns:
            def safe_zip_convert(x):
                if pd.notna(x) and str(x).strip() not in ('', 'nan'):
                    try:
                        # Convert to int first, then to string to preserve without decimals
                        return str(int(float(x)))
                    except (ValueError, TypeError) as e:
                        print(f"WARNING: Could not convert zip_postal to int: {repr(x)} (type: {type(x).__name__}) - Error: {e}")
                return x

            df['zip_postal'] = df['zip_postal'].apply(safe_zip_convert)

        # Convert quantity to int (remove .0)
        if 'quantity' in df.columns:
            def safe_int_convert(x):
                if pd.notna(x) and str(x).strip() != '':
                    try:
                        float_val = float(x)
                        if float_val == int(float_val):
                            return int(float_val)
                    except (ValueError, TypeError) as e:
                        # Log the problematic value for debugging
                        print(f"WARNING: Could not convert quantity value to int: {repr(x)} (type: {type(x).__name__}) - Error: {e}")
                return x

            df['quantity'] = df['quantity'].apply(safe_int_convert)

        self.df = df
        return df

    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert DataFrame to list of dictionaries.

        Returns:
            List of row dictionaries
        """
        if self.df is None:
            return []

        return self.df.to_dict('records')

    def to_csv(self, output_path: str) -> None:
        """Export DataFrame to CSV file.

        Args:
            output_path: Path to output CSV file
        """
        if self.df is None:
            raise TransformationError("No data to export. Run transform() first.")

        self.df.to_csv(output_path, index=False)
