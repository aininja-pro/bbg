"""Data enrichment service using lookup tables."""
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.lookup import TradeNetMember, Supplier, ProgramProduct
from app.utils.exceptions import LookupError


class DataEnricher:
    """Enriches transformed data with lookup table information."""

    def __init__(self, db: AsyncSession):
        """Initialize enricher with database session.

        Args:
            db: Async database session
        """
        self.db = db
        self.members_cache: Dict[str, TradeNetMember] = {}
        self.suppliers_cache: Dict[str, Supplier] = {}
        self.products_cache: Dict[str, ProgramProduct] = {}

    async def load_lookups(self) -> None:
        """Pre-load all lookup tables into memory for fast access."""
        # Load members
        result = await self.db.execute(select(TradeNetMember))
        members = result.scalars().all()
        self.members_cache = {m.bbg_member_id: m for m in members}

        # Load suppliers
        result = await self.db.execute(select(Supplier))
        suppliers = result.scalars().all()
        self.suppliers_cache = {s.tradenet_supplier_id: s for s in suppliers}

        # Load products
        result = await self.db.execute(select(ProgramProduct))
        products = result.scalars().all()
        self.products_cache = {p.product_id: p for p in products}

    async def enrich_member_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich with TradeNet Member information.

        Args:
            df: DataFrame with bbg_member_id column

        Returns:
            DataFrame with added tradenet_company_id
        """
        if not self.members_cache:
            await self.load_lookups()

        def get_tradenet_id(bbg_id):
            """Lookup tradenet company ID by BBG member ID."""
            if not bbg_id:
                return None

            member = self.members_cache.get(str(bbg_id))
            return member.tradenet_company_id if member else None

        df['tradenet_company_id'] = df['bbg_member_id'].apply(get_tradenet_id)

        return df

    async def enrich_supplier_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich with Supplier information.

        Args:
            df: DataFrame with tradenet_supplier_id column

        Returns:
            DataFrame with added supplier_name
        """
        if not self.suppliers_cache:
            await self.load_lookups()

        def get_supplier_name(supplier_id):
            """Lookup supplier name by tradenet supplier ID."""
            if not supplier_id:
                return None

            supplier = self.suppliers_cache.get(str(supplier_id))
            return supplier.supplier_name if supplier else None

        # For now, tradenet_supplier_id might not be in the data yet
        # This will be populated when we integrate with supplier data from files
        if 'tradenet_supplier_id' in df.columns:
            df['supplier_name'] = df['tradenet_supplier_id'].apply(get_supplier_name)
        else:
            df['supplier_name'] = None
            df['tradenet_supplier_id'] = None

        return df

    def apply_supplier_rules(self, product_id: str, default_supplier: str) -> str:
        """Apply business rules for supplier name overrides.

        Args:
            product_id: The product ID
            default_supplier: Default supplier name from Programs-Products Column A

        Returns:
            Final supplier name after applying rules
        """
        # Special rule: "Day & Night Heating & Cooling" is Carrier
        if default_supplier == "Day & Night Heating & Cooling":
            return "Carrier"

        # Rule 1: Product 5534 → Air Vent
        if '5534' in product_id:
            return 'Air Vent'

        # Rule 2: Product 5531 → CertainTeed
        if '5531' in product_id:
            return 'CertainTeed'

        # Rule 3: Product 5406 → Air Vent
        if '5406' in product_id:
            return 'Air Vent'

        # Rule 4: Product 5407 → CertainTeed
        if '5407' in product_id:
            return 'CertainTeed'

        # Rule 5: Product 5255 → Heatilator (Hearth & Home)
        if '5255' in product_id:
            return 'Heatilator (Hearth & Home)'

        # Rule 7: Product 5270 → Leading Edge
        if '5270' in product_id:
            return 'Leading Edge'

        # Rule 8: Product 5350 → Leading Edge
        if '5350' in product_id:
            return 'Leading Edge'

        # Default: Use program name from Programs-Products Column A (98% of cases)
        return default_supplier

    async def enrich_product_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich with Program & Product information, including supplier mapping.

        Args:
            df: DataFrame with product_id column

        Returns:
            DataFrame with added product_name, proof_point, and supplier info
        """
        if not self.products_cache:
            await self.load_lookups()

        def get_product_info(product_id):
            """Lookup product details and supplier by product ID."""
            if not product_id:
                return None, None, None

            product = self.products_cache.get(str(product_id))
            if product:
                # Get supplier name from Program (Column A) - 98% of cases
                supplier_name = product.program_name

                # Apply business rule overrides (2% of cases)
                supplier_name = self.apply_supplier_rules(str(product_id), supplier_name)

                return product.product_name, product.proof_point, supplier_name
            return None, None, None

        # Apply lookup
        product_info = df['product_id'].apply(get_product_info)
        df['product_name'] = product_info.apply(lambda x: x[0] if x else None)
        df['proof_point'] = product_info.apply(lambda x: x[1] if x else None)
        df['_supplier_name_from_program'] = product_info.apply(lambda x: x[2] if x else None)

        return df

    async def match_supplier_from_name(self, df: pd.DataFrame) -> pd.DataFrame:
        """Match supplier name to TradeNet Supplier Directory to get tradenet_supplier_id.

        Args:
            df: DataFrame with _supplier_name_from_program column

        Returns:
            DataFrame with supplier_name and tradenet_supplier_id populated
        """
        if not self.suppliers_cache:
            await self.load_lookups()

        # Create reverse lookup: supplier_name → tradenet_supplier_id
        supplier_name_to_id = {}
        for supplier_id, supplier in self.suppliers_cache.items():
            # Store both the full name and variations
            supplier_name_to_id[supplier.supplier_name] = supplier_id

        def lookup_supplier_id(supplier_name):
            """Find tradenet_supplier_id by matching supplier name."""
            if not supplier_name:
                return None, None

            # Try exact match first
            if supplier_name in supplier_name_to_id:
                supplier_id = supplier_name_to_id[supplier_name]
                return supplier_name, supplier_id

            # Try fuzzy match (case-insensitive, partial match)
            supplier_lower = supplier_name.lower().strip()
            for full_name, supplier_id in supplier_name_to_id.items():
                if supplier_lower in full_name.lower() or full_name.lower() in supplier_lower:
                    return full_name, supplier_id

            # No match found - return original name with no ID
            return supplier_name, None

        # Apply lookup
        if '_supplier_name_from_program' in df.columns:
            supplier_info = df['_supplier_name_from_program'].apply(lookup_supplier_id)
            df['supplier_name'] = supplier_info.apply(lambda x: x[0] if x else None)
            df['tradenet_supplier_id'] = supplier_info.apply(lambda x: x[1] if x else None)

            # Drop temporary column
            df = df.drop(columns=['_supplier_name_from_program'], errors='ignore')

        return df

    async def enrich_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run all enrichment steps.

        Args:
            df: Transformed DataFrame

        Returns:
            Fully enriched DataFrame
        """
        # Load all lookups once
        await self.load_lookups()

        # Enrich in sequence
        df = await self.enrich_member_info(df)
        df = await self.enrich_supplier_info(df)
        df = await self.enrich_product_info(df)

        # Match supplier name to TradeNet directory
        df = await self.match_supplier_from_name(df)

        return df

    def identify_warnings(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify data quality warnings (missing lookups, validation issues).

        Args:
            df: Enriched DataFrame

        Returns:
            List of warning dictionaries
        """
        warnings = []

        # Check for missing member lookups
        missing_members = df[df['tradenet_company_id'].isna()]
        if not missing_members.empty:
            warnings.append({
                'type': 'missing_member_lookup',
                'count': len(missing_members),
                'message': f"{len(missing_members)} rows with missing member lookup"
            })

        # Check for missing product lookups
        missing_products = df[df['product_name'].isna()]
        if not missing_products.empty:
            warnings.append({
                'type': 'missing_product_lookup',
                'count': len(missing_products),
                'message': f"{len(missing_products)} rows with missing product lookup"
            })

        # Check for missing dates
        date_col = 'confirmed_occupancy' if 'confirmed_occupancy' in df.columns else 'date'
        if date_col in df.columns:
            missing_dates = df[df[date_col].isna()]
            if not missing_dates.empty:
                warnings.append({
                    'type': 'missing_date',
                    'count': len(missing_dates),
                    'message': f"{len(missing_dates)} rows with missing dates"
                })

        return warnings
