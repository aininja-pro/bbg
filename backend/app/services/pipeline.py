"""Main processing pipeline that orchestrates Excel processing, transformation, and enrichment."""
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.excel_processor import ExcelProcessor
from app.services.data_transformer import DataTransformer
from app.services.data_enricher import DataEnricher
from app.utils.exceptions import ExcelProcessingError


class ProcessingPipeline:
    """Orchestrates the complete rebate file processing pipeline."""

    def __init__(self, db: AsyncSession):
        """Initialize pipeline with database session.

        Args:
            db: Async database session for lookups
        """
        self.db = db
        self.processor: Optional[ExcelProcessor] = None
        self.transformer = DataTransformer()
        self.enricher = DataEnricher(db)
        self.result: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.warnings: List[Dict[str, Any]] = []

    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single rebate Excel file through the complete pipeline.

        Args:
            file_path: Path to the .xlsm file

        Returns:
            Dictionary with processing results and metadata
        """
        try:
            # Step 1: Open and validate Excel file
            self.processor = ExcelProcessor(file_path)
            self.processor.open_file()

            # Step 2: Find Usage-Reporting sheet
            self.processor.find_usage_reporting_sheet()

            # Step 3: Extract metadata (B6, B7)
            metadata = self.processor.extract_metadata()
            self.metadata = metadata

            # Step 4: Detect header row
            header_row = self.processor.detect_header_row()

            # Step 5: Identify active products
            active_products = self.processor.identify_active_products(header_row)

            # Step 6: Transform data (unpivot, convert dates, standardize)
            df = self.transformer.transform(
                self.processor.reformatter_sheet,
                header_row,
                active_products,
                metadata
            )

            # Step 7: Enrich with lookup tables
            df = await self.enricher.enrich_all(df)

            # Step 8: Identify warnings
            self.warnings = self.enricher.identify_warnings(df)

            # Step 9: Select only the required output columns (remove extras like product_name, proof_point)
            output_columns = [
                'member_name', 'bbg_member_id', 'confirmed_occupancy', 'job_code',
                'address1', 'city', 'state', 'zip_postal', 'address_type', 'quantity',
                'product_id', 'supplier_name', 'tradenet_supplier_id',
                'pp_dist_subcontractor', 'tradenet_company_id'
            ]
            # Only keep columns that exist
            df = df[[col for col in output_columns if col in df.columns]]

            self.result = df

            return {
                'success': True,
                'metadata': metadata,
                'total_rows': len(df),
                'active_products': len(active_products),
                'warnings': self.warnings,
                'preview': df.head(10).to_dict('records') if len(df) > 0 else []
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

        finally:
            if self.processor:
                self.processor.close()

    def get_dataframe(self) -> pd.DataFrame:
        """Get the processed DataFrame.

        Returns:
            Processed and enriched DataFrame
        """
        if self.result is None:
            raise ExcelProcessingError("No data processed yet. Call process_file() first.")

        return self.result

    def export_csv(self, output_path: str) -> None:
        """Export processed data to CSV.

        Args:
            output_path: Path for output CSV file
        """
        if self.result is None:
            raise ExcelProcessingError("No data to export. Call process_file() first.")

        self.result.to_csv(output_path, index=False)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the processing results.

        Returns:
            Summary dictionary
        """
        if self.result is None:
            return {'status': 'not_processed'}

        date_col = 'confirmed_occupancy' if 'confirmed_occupancy' in self.result.columns else 'date'

        return {
            'status': 'completed',
            'member_id': self.metadata.get('bbg_member_id'),
            'member_name': self.metadata.get('member_name'),
            'total_rows': len(self.result),
            'unique_products': self.result['product_id'].nunique() if 'product_id' in self.result.columns else 0,
            'date_range': {
                'start': self.result[date_col].min() if date_col in self.result.columns else None,
                'end': self.result[date_col].max() if date_col in self.result.columns else None,
            },
            'warnings_count': len(self.warnings),
            'warnings': self.warnings
        }
