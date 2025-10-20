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
        self.metadata: Dict[str, Any] = {}

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

    def find_reformatter_sheet(self) -> None:
        """Locate the 'reformatter' sheet (may be hidden)."""
        if not self.workbook:
            raise ExcelProcessingError("Workbook not loaded. Call open_file() first.")

        # Try to find sheet by name (case-insensitive)
        for sheet_name in self.workbook.sheetnames:
            if 'reformatter' in sheet_name.lower():
                self.reformatter_sheet = self.workbook[sheet_name]
                return

        raise ExcelProcessingError(
            "Reformatter sheet not found. Expected a sheet with 'reformatter' in the name."
        )

    def extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from cells B6 (bbg_member_id) and B7 (member_name).

        Returns:
            Dictionary with bbg_member_id and member_name
        """
        if not self.reformatter_sheet:
            raise ExcelProcessingError("Reformatter sheet not loaded.")

        # Extract B6 and B7
        bbg_member_id = self.reformatter_sheet['B6'].value
        member_name = self.reformatter_sheet['B7'].value

        # Validate metadata exists
        if not bbg_member_id:
            raise ExcelProcessingError("Cell B6 (BBG Member ID) is empty")

        if not member_name:
            raise ExcelProcessingError("Cell B7 (Member Name) is empty")

        self.metadata = {
            'bbg_member_id': str(bbg_member_id).strip(),
            'member_name': str(member_name).strip(),
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

    def identify_active_products(self, header_row: int) -> Dict[int, str]:
        """Identify active product columns (Row 2=1) and extract product IDs (Row 7).

        Args:
            header_row: The row number where headers are located

        Returns:
            Dictionary mapping column index to product ID
        """
        if not self.reformatter_sheet:
            raise ExcelProcessingError("Reformatter sheet not loaded.")

        active_products = {}

        # Row 2 indicates active products (value = 1)
        # Row 7 contains product IDs
        row_2 = self.reformatter_sheet[2]
        row_7 = self.reformatter_sheet[7]

        for idx, (active_cell, product_cell) in enumerate(zip(row_2, row_7), start=1):
            # Check if this column is active (Row 2 = 1)
            if active_cell.value == 1:
                product_id = product_cell.value

                if product_id:
                    active_products[idx] = str(product_id).strip()

        if not active_products:
            raise ExcelProcessingError(
                "No active products found. Expected Row 2 to contain '1' for active products "
                "and Row 7 to contain product IDs."
            )

        return active_products

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
