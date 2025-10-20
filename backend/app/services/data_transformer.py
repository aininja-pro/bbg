"""Data transformation service for unpivoting and enriching rebate data."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

from app.utils.exceptions import TransformationError


class DataTransformer:
    """Transforms wide-format rebate data to long format and enriches it."""

    # Standard output columns for transformed data
    OUTPUT_COLUMNS = [
        'bbg_member_id',
        'member_name',
        'tradenet_company_id',
        'date',
        'job_code',
        'job_name',
        'address1',
        'address2',
        'city',
        'state',
        'zip_postal',
        'confirmed_occupancy',
        'address_type',
        'product_id',
        'product_name',
        'quantity',
        'tradenet_supplier_id',
        'supplier_name',
        'proof_point',
    ]

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
        active_products: Dict[int, str],
        metadata: Dict[str, str]
    ) -> pd.DataFrame:
        """Unpivot wide format to long format for product columns.

        Args:
            df: Wide-format DataFrame
            active_products: Dictionary of column index -> product ID
            metadata: Dictionary with member info

        Returns:
            Long-format DataFrame with one row per product per transaction
        """
        # Get product column names from indices
        product_columns = []
        product_id_map = {}

        for col_idx, product_id in active_products.items():
            if col_idx - 1 < len(df.columns):
                col_name = df.columns[col_idx - 1]  # Convert 1-indexed to 0-indexed
                product_columns.append(col_name)
                product_id_map[col_name] = product_id

        if not product_columns:
            raise TransformationError("No product columns found to unpivot")

        # Expected base column names (case-insensitive matching)
        expected_base_columns = [
            'date', 'jobcode', 'job code', 'job_code',
            'address', 'city', 'state', 'zip', 'postal',
            'multi-unit', 'comm', 'address_type', 'occupancy'
        ]

        # Select only the base columns that exist in the DataFrame
        base_columns = []
        for col in df.columns:
            if col not in product_columns and col is not None:
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

        # Add product ID based on column name
        df_long['product_id'] = df_long['product_column'].map(product_id_map)

        # Add metadata
        df_long['bbg_member_id'] = metadata['bbg_member_id']
        df_long['member_name'] = metadata['member_name']

        # Remove rows with null/zero quantity
        df_long = df_long[
            (df_long['quantity'].notna()) &
            (df_long['quantity'] != 0) &
            (df_long['quantity'] != '')
        ]

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
            """Convert various date formats to MM/DD/YYYY string."""
            if pd.isna(val) or val == '':
                return None

            try:
                # If it's already a datetime
                if isinstance(val, datetime):
                    return val.strftime('%m/%d/%Y')

                # If it's an Excel serial number
                if isinstance(val, (int, float)):
                    # Excel epoch starts at 1899-12-30
                    dt = pd.Timestamp('1899-12-30') + pd.Timedelta(days=val)
                    return dt.strftime('%m/%d/%Y')

                # Try parsing as string
                dt = pd.to_datetime(val)
                return dt.strftime('%m/%d/%Y')

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
            'date': 'date',
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
            'qty': 'quantity',
            'quantity': 'quantity',
            'occupancy': 'confirmed_occupancy',
            'confirmed occupancy': 'confirmed_occupancy',
        }

        # Rename columns (case-insensitive)
        new_columns = {}
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in column_mapping:
                new_columns[col] = column_mapping[col_lower]

        if new_columns:
            df = df.rename(columns=new_columns)

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
        active_products: Dict[int, str],
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

        # Step 2: Standardize column names
        df = self.standardize_columns(df)

        # Step 3: Convert dates
        df = self.convert_excel_dates(df)

        # Step 4: Unpivot products
        df = self.unpivot_products(df, active_products, metadata)

        # Step 5: Add missing columns
        df = self.add_placeholder_columns(df)

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
