"""Data transformation service for unpivoting and enriching rebate data."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

from app.utils.exceptions import TransformationError


class DataTransformer:
    """Transforms wide-format rebate data to long format and enriches it."""

    # Standard output columns for transformed data (exact client format - 15 columns)
    OUTPUT_COLUMNS = [
        'member_name',
        'bbg_member_id',
        'confirmed_occupancy',
        'job_code',
        'address1',
        'city',
        'state',
        'zip_postal',
        'address_type',
        'quantity',
        'product_id',
        'supplier_name',
        'tradenet_supplier_id',
        'pp_dist_subcontractor',
        'tradenet_company_id',
    ]

    # Note: product_name and proof_point are enriched but not included in final output

    def __init__(self):
        """Initialize the data transformer."""
        self.df: Optional[pd.DataFrame] = None

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

        # Extract headers
        for cell in sheet[header_row]:
            headers.append(cell.value if cell.value else f"Column_{cell.column}")

        # Extract data rows (starting after header)
        for row in sheet.iter_rows(min_row=header_row + 1, values_only=True):
            # Skip empty rows
            if all(cell is None or cell == '' for cell in row):
                continue

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
        # Get product column names from indices (preserve Excel column order)
        product_columns = []
        product_id_map = {}
        distributor_map = {}
        product_order_map = {}  # Maps product_id to its Excel column order

        # Sort active_products by column index to preserve left-to-right order
        sorted_products = sorted(active_products.items(), key=lambda x: x[0])

        for order_num, (col_idx, product_info) in enumerate(sorted_products):
            if col_idx - 1 < len(df.columns):
                col_name = df.columns[col_idx - 1]  # Convert 1-indexed to 0-indexed
                product_columns.append(col_name)
                product_id_map[col_name] = product_info['product_id']
                distributor_map[col_name] = product_info.get('distributor')
                # Store the Excel column order for sorting
                product_order_map[product_info['product_id']] = order_num

        if not product_columns:
            raise TransformationError("No product columns found to unpivot")

        # Expected base column names (case-insensitive matching)
        expected_base_columns = [
            'date', 'jobcode', 'job code', 'job_code',
            'address', 'city', 'state', 'zip', 'postal',
            'multi-unit', 'comm', 'address_type', 'occupancy',
            '_date_sort', '_product_order'  # Include sorting columns
        ]

        # Select only the base columns that exist in the DataFrame
        base_columns = []
        for col in df.columns:
            if col not in product_columns and col is not None:
                # Always include sorting columns
                if col in ['_date_sort', '_product_order']:
                    base_columns.append(col)
                    continue

                # Check if this column name matches expected base columns
                col_lower = str(col).lower().strip()
                if any(expected in col_lower for expected in expected_base_columns):
                    base_columns.append(col)

        # If we didn't find enough base columns, just take the first N columns that aren't products
        if len(base_columns) < 5:
            # Fallback: take first 10 non-product columns
            base_columns = []
            for col in df.columns[:20]:  # Check first 20 columns
                if col not in product_columns and col is not None and str(col).strip():
                    base_columns.append(col)
                if len(base_columns) >= 10:
                    break

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
            'postal': 'zip_postal',
            'zip code': 'zip_postal',
            'postal code': 'zip_postal',
            'multi-unit/comm': 'address_type',
            'multi-unit': 'address_type',
            'qty': 'quantity',
            'quantity': 'quantity',
        }

        # Rename columns (case-insensitive)
        new_columns = {}
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in column_mapping:
                new_columns[col] = column_mapping[col_lower]

        if new_columns:
            df = df.rename(columns=new_columns)

        # Apply address_type business rule: blank = "RESIDENTIAL"
        if 'address_type' in df.columns:
            df['address_type'] = df['address_type'].apply(
                lambda x: 'RESIDENTIAL' if pd.isna(x) or x == '' else str(x).strip()
            )

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
