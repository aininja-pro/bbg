"""Main processing pipeline that orchestrates Excel processing, transformation, and enrichment."""
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.excel_processor import ExcelProcessor
from app.services.data_transformer import DataTransformer
from app.services.data_enricher import DataEnricher
from app.repositories.settings import ColumnSettingsRepository
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

    async def process_file(self, file_path: str, include_preview: bool = True) -> Dict[str, Any]:
        """Process a single rebate Excel file through the complete pipeline.

        Args:
            file_path: Path to the .xlsm file
            include_preview: Whether to include preview data in results (default True).
                           Set to False for batch operations to reduce memory usage.

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

            # Step 5: Extract Programs-Products from this file
            file_products = self.processor.extract_programs_products()

            # Step 6: Identify active products
            active_products = self.processor.identify_active_products(header_row)

            # Step 7: Transform data (unpivot, convert dates, standardize)
            df = self.transformer.transform(
                self.processor.reformatter_sheet,
                header_row,
                active_products,
                metadata
            )

            # Step 8: Enrich with lookup tables (pass file-specific products)
            df = await self.enricher.enrich_all(df, file_products=file_products)

            # Step 8: Identify warnings
            self.warnings = self.enricher.identify_warnings(df)

            # Step 9: Select output columns based on column settings
            # Get enabled columns from database
            column_settings = await ColumnSettingsRepository.get_all(self.db)

            if column_settings:
                # Use database settings to determine which columns to include
                output_columns = []
                for col_setting in sorted(column_settings, key=lambda x: x.display_order):
                    # Include if enabled OR if it's a standard column (not custom)
                    if col_setting.enabled or not col_setting.is_custom:
                        output_columns.append(col_setting.column_name)
            else:
                # Fallback: All columns in correct order if no settings exist
                output_columns = [
                    'member_name', 'bbg_member_id', 'confirmed_occupancy', 'job_code',
                    'address1', 'city', 'state', 'zip_postal', 'address_type', 'quantity',
                    'product_id', 'supplier_name', 'tradenet_supplier_id',
                    'pp_receipt', 'pp_brand_name', 'pp_dist_subcontractor',
                    'pp_prod_purchase', 'tradenet_company_id'
                ]

            # Only keep columns that exist in the dataframe
            df = df[[col for col in output_columns if col in df.columns]]

            self.result = df

            # Limit preview to first 200 rows to reduce memory usage on large files
            preview_data = []
            if include_preview and len(df) > 0:
                preview_limit = 200
                preview_df = df.head(preview_limit)
                preview_data = preview_df.to_dict('records')

            return {
                'success': True,
                'metadata': metadata,
                'total_rows': len(df),
                'active_products': len(active_products),
                'warnings': self.warnings,
                'preview': preview_data
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
