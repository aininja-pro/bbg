"""Excel file processing service for BBG rebate files."""
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from app.utils.exceptions import ExcelProcessingError


class ExcelProcessor:
    """Processes BBG rebate Excel files (.xlsm)."""

    # Keywords to detect header row
    HEADER_KEYWORDS = [
        "date", "job code", "job name", "address", "city",
        "state", "zip", "postal", "product", "qty", "quantity"
    ]

    def __init__(self, file_path: str):
        """Initialize processor with file path.

        Args:
            file_path: Path to the .xlsm file
        """
        self.file_path = Path(file_path)
        self.workbook: Optional[openpyxl.Workbook] = None
        self.reformatter_sheet: Optional[Worksheet] = None
        self.programs_products_sheet: Optional[Worksheet] = None
        self.metadata: Dict[str, Any] = {}
        self.file_products: Dict[str, Dict[str, Any]] = {}  # Product lookup from this file

    def open_file(self) -> None:
        """Open the Excel file and validate it exists."""
        if not self.file_path.exists():
            raise ExcelProcessingError(f"File not found: {self.file_path}")

        if not self.file_path.suffix.lower() in ['.xlsm', '.xlsx']:
            raise ExcelProcessingError(f"Invalid file type: {self.file_path.suffix}. Expected .xlsm or .xlsx")

        try:
            # Load workbook with data_only=True to get calculated values
            self.workbook = openpyxl.load_workbook(
                self.file_path,
                data_only=True,
                read_only=False
            )
        except Exception as e:
            raise ExcelProcessingError(f"Failed to open Excel file: {str(e)}")

    def find_usage_reporting_sheet(self) -> None:
        """Locate the 'Usage-Reporting' sheet with the actual data."""
        if not self.workbook:
            raise ExcelProcessingError("Workbook not loaded. Call open_file() first.")

        # Try to find Usage-Reporting sheet (case-insensitive)
        for sheet_name in self.workbook.sheetnames:
            sheet_lower = sheet_name.lower()
            if 'usage' in sheet_lower and 'report' in sheet_lower:
                self.reformatter_sheet = self.workbook[sheet_name]
                return

        raise ExcelProcessingError(
            "Usage-Reporting sheet not found. Expected a sheet with 'usage' and 'report' in the name."
        )

    def extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from cells B6 (bbg_member_id) and B7 (member_name).

        Supports both OLD and NEW formats:
        - NEW: B6 has member ID, B7 has member name
        - OLD: B6 is blank, B7 has member name (ID must be looked up)

        Returns:
            Dictionary with bbg_member_id and member_name (ID may be None for old format)
        """
        if not self.reformatter_sheet:
            raise ExcelProcessingError("Usage-Reporting sheet not loaded.")

        # Extract B6 and B7
        bbg_member_id = self.reformatter_sheet['B6'].value
        member_name = self.reformatter_sheet['B7'].value

        # Validate member name exists (required in both formats)
        if not member_name:
            raise ExcelProcessingError("Cell B7 (Member Name) is empty")

        # Handle OLD format: B6 is blank, need to lookup ID by name later
        if not bbg_member_id:
            # Old format - store as None, will be looked up during enrichment
            self.metadata = {
                'bbg_member_id': None,
                'member_name': str(member_name).strip(),
                'format': 'OLD'  # Flag for old format
            }
        else:
            # New format - has ID in B6
            self.metadata = {
                'bbg_member_id': str(bbg_member_id).strip(),
                'member_name': str(member_name).strip(),
                'format': 'NEW'
            }

        return self.metadata

    def detect_header_row(self, max_rows: int = 20) -> int:
        """Auto-detect the header row by searching for keywords.

        Args:
            max_rows: Maximum number of rows to search

        Returns:
            Row number (1-indexed) where headers are found
        """
        if not self.reformatter_sheet:
            raise ExcelProcessingError("Reformatter sheet not loaded.")

        # Search first N rows for header keywords
        for row_num in range(1, max_rows + 1):
            row_values = []
            for cell in self.reformatter_sheet[row_num]:
                if cell.value:
                    row_values.append(str(cell.value).lower())

            # Check if this row contains header keywords
            matches = sum(
                1 for keyword in self.HEADER_KEYWORDS
                if any(keyword in val for val in row_values)
            )

            # If we find at least 3 keyword matches, assume this is the header row
            if matches >= 3:
                return row_num

        raise ExcelProcessingError(
            f"Header row not found in first {max_rows} rows. "
            f"Expected keywords: {', '.join(self.HEADER_KEYWORDS[:5])}"
        )

    def identify_active_products(self, header_row: int) -> Dict[int, Dict[str, str]]:
        """Identify active product columns and extract product IDs and distributor info.

        Args:
            header_row: The row number where headers are located

        Returns:
            Dictionary mapping column index to dict with product_id and distributor
        """
        if not self.reformatter_sheet:
            raise ExcelProcessingError("Usage-Reporting sheet not loaded.")

        active_products = {}

        # Row 2 indicates active products (value = 1)
        # Row 5 contains distributor/subcontractor names
        # Row 7 contains product IDs
        row_2 = self.reformatter_sheet[2]
        row_5 = self.reformatter_sheet[5]
        row_7 = self.reformatter_sheet[7]

        # Iterate through all columns
        max_col = self.reformatter_sheet.max_column
        for col_idx in range(1, max_col + 1):
            active_flag = row_2[col_idx - 1].value if col_idx <= len(row_2) else None
            distributor = row_5[col_idx - 1].value if col_idx <= len(row_5) else None
            product_id = row_7[col_idx - 1].value if col_idx <= len(row_7) else None

            # Check if this column is active (Row 2 = 1) AND has a product ID in Row 7
            if active_flag == 1 and product_id:
                # Validate it's a real product ID (numeric)
                try:
                    if isinstance(product_id, (int, float)):
                        pid_str = str(int(product_id))
                    elif str(product_id).isdigit():
                        pid_str = str(product_id).strip()
                    else:
                        continue  # Skip non-numeric product IDs

                    # Store product info with distributor
                    active_products[col_idx] = {
                        'product_id': pid_str,
                        'distributor': str(distributor).strip() if distributor else None
                    }
                except:
                    pass  # Skip invalid entries

        if not active_products:
            raise ExcelProcessingError(
                "No active products found. Expected Row 2 = 1 for active columns and numeric product IDs in Row 7."
            )

        return active_products

    def extract_programs_products(self) -> Dict[str, Dict[str, Any]]:
        """Extract Programs-Products data from the Excel file.

        Returns:
            Dictionary mapping product_id to product info (program, name, proof_point)
        """
        if not self.workbook:
            raise ExcelProcessingError("Workbook not loaded.")

        # Find Programs-Products sheet
        programs_sheet = None
        for sheet_name in self.workbook.sheetnames:
            if 'program' in sheet_name.lower() and 'product' in sheet_name.lower():
                programs_sheet = self.workbook[sheet_name]
                break

        if not programs_sheet:
            # If no Programs-Products sheet, return empty dict
            return {}

        self.programs_products_sheet = programs_sheet
        products = {}

        # Read using cell references directly (more reliable than iter_rows)
        # Row 1 = headers, Row 2+ = data
        max_row = programs_sheet.max_row

        for row_num in range(2, max_row + 1):  # Start at row 2 (skip headers)
            program = programs_sheet.cell(row_num, 1).value  # Column A
            product_id = programs_sheet.cell(row_num, 2).value  # Column B
            product_name = programs_sheet.cell(row_num, 3).value  # Column C
            proof_point = programs_sheet.cell(row_num, 4).value  # Column D

            # Skip empty rows
            if not product_id or not product_name:
                continue

            # Skip header rows that might be repeated (Program="Product ID" is a header)
            if str(program).strip() == 'Product ID' or str(program).strip() == 'Program':
                continue

            # Convert product_id to string
            if isinstance(product_id, (int, float)):
                product_id_str = str(int(product_id))
            else:
                product_id_str = str(product_id).strip()


            products[product_id_str] = {
                'program_name': str(program).strip() if program else None,
                'product_name': str(product_name).strip() if product_name else None,
                'proof_point': str(proof_point).strip() if proof_point and str(proof_point) != 'None' else None,
            }

        self.file_products = products
        return products

    def get_column_letter(self, col_idx: int) -> str:
        """Convert column index to Excel column letter (e.g., 1 -> A, 27 -> AA).

        Args:
            col_idx: Column index (1-indexed)

        Returns:
            Excel column letter
        """
        return openpyxl.utils.get_column_letter(col_idx)

    def close(self) -> None:
        """Close the workbook and release resources."""
        if self.workbook:
            self.workbook.close()
            self.workbook = None
            self.reformatter_sheet = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.close()
