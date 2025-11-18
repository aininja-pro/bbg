"""Data enrichment service using lookup tables."""
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.lookup import TradeNetMember, Supplier, ProgramProduct
from app.models.rule import Rule
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
        self.supplier_rules: List[Rule] = []

    async def load_lookups(self) -> None:
        """Pre-load all lookup tables and rules into memory for fast access."""
        # Load members
        result = await self.db.execute(select(TradeNetMember))
        members = result.scalars().all()
        self.members_cache = {m.bbg_member_id: m for m in members}

        # Load ALL enabled rules (both old and new formats), ordered by priority
        result = await self.db.execute(
            select(Rule)
            .where(Rule.enabled == True)
            .order_by(Rule.priority)
        )
        self.supplier_rules = list(result.scalars().all())

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

        Handles both OLD and NEW formats:
        - NEW: bbg_member_id is provided, just lookup tradenet_company_id
        - OLD: bbg_member_id is None, lookup by member_name first

        Args:
            df: DataFrame with bbg_member_id and member_name columns

        Returns:
            DataFrame with added tradenet_company_id and filled bbg_member_id
        """
        if not self.members_cache:
            await self.load_lookups()

        # Create reverse lookup: member_name → member
        name_to_member = {}
        for bbg_id, member in self.members_cache.items():
            name_to_member[member.member_name] = member

        def get_member_info(row):
            """Lookup member info by ID or name."""
            bbg_id = row['bbg_member_id']
            member_name = row['member_name']

            # If bbg_id exists (NEW format), use it
            if bbg_id:
                member = self.members_cache.get(str(bbg_id))
                if member:
                    return member.tradenet_company_id, bbg_id
                return None, bbg_id

            # If bbg_id is None (OLD format), lookup by name
            if member_name:
                member = name_to_member.get(member_name)
                if member:
                    return member.tradenet_company_id, member.bbg_member_id

            return None, None

        # Apply lookup
        member_info = df.apply(get_member_info, axis=1)
        df['tradenet_company_id'] = member_info.apply(lambda x: x[0])
        # Fill in bbg_member_id for OLD format files
        df['bbg_member_id'] = member_info.apply(lambda x: x[1])

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

    def _evaluate_operator(self, field_value: Any, operator: str, compare_value: Any) -> bool:
        """Evaluate a single operator condition.

        Args:
            field_value: The actual field value from the row
            operator: The comparison operator
            compare_value: The value to compare against

        Returns:
            True if condition matches, False otherwise
        """
        try:
            # Handle None/empty values
            if field_value is None:
                field_value = ""

            field_str = str(field_value).strip()

            # Text operators
            if operator == "equals":
                return field_str == str(compare_value)
            elif operator == "not_equals":
                return field_str != str(compare_value)
            elif operator == "contains":
                return str(compare_value) in field_str
            elif operator == "not_contains":
                return str(compare_value) not in field_str
            elif operator == "starts_with":
                return field_str.startswith(str(compare_value))
            elif operator == "ends_with":
                return field_str.endswith(str(compare_value))
            elif operator == "is_empty":
                return field_str == ""
            elif operator == "is_not_empty":
                return field_str != ""

            # Numeric operators
            elif operator in ["greater_than", "less_than", "greater_or_equal", "less_or_equal"]:
                try:
                    field_num = float(field_value)
                    compare_num = float(compare_value)
                    if operator == "greater_than":
                        return field_num > compare_num
                    elif operator == "less_than":
                        return field_num < compare_num
                    elif operator == "greater_or_equal":
                        return field_num >= compare_num
                    elif operator == "less_or_equal":
                        return field_num <= compare_num
                except (ValueError, TypeError):
                    return False

            # List operators
            elif operator == "in":
                return field_value in compare_value  # compare_value should be a list
            elif operator == "not_in":
                return field_value not in compare_value

            return False
        except Exception:
            return False

    def _evaluate_condition(self, row_data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Evaluate a condition (supports old, current, and nested formats).

        Args:
            row_data: Dictionary with field values for current row
            condition: Condition configuration

        Returns:
            True if condition matches, False otherwise
        """
        # OLD FORMAT: Check legacy supplier_name_equals
        if 'supplier_name_equals' in condition:
            supplier_name = row_data.get('supplier_name', '')
            return supplier_name == condition['supplier_name_equals']

        # OLD FORMAT: Check legacy product_id_contains
        if 'product_id_contains' in condition:
            product_id = str(row_data.get('product_id', ''))
            return condition['product_id_contains'] in product_id

        # NESTED FORMAT: type-based recursive evaluation
        condition_type = condition.get('type')

        if condition_type == 'group':
            logic = condition.get('logic', 'AND')
            children = condition.get('children', [])

            if not children:
                return False

            results = []
            for child in children:
                # Recursive call handles both conditions and nested groups
                result = self._evaluate_condition(row_data, child)
                results.append(result)

            if logic == 'AND':
                return all(results)
            elif logic == 'OR':
                return any(results)
            return False

        elif condition_type == 'condition':
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            field_value = row_data.get(field)
            return self._evaluate_operator(field_value, operator, value)

        # CURRENT FLAT FORMAT: Flexible conditions with AND/OR logic
        # Kept for backward compatibility during migration
        if 'logic' in condition and 'rules' in condition:
            logic = condition.get('logic', 'AND')
            rules = condition.get('rules', [])

            results = []
            for rule_condition in rules:
                field = rule_condition.get('field')
                operator = rule_condition.get('operator')
                value = rule_condition.get('value')

                field_value = row_data.get(field)
                result = self._evaluate_operator(field_value, operator, value)
                results.append(result)

            # Apply logic
            if logic == 'AND':
                return all(results) if results else False
            elif logic == 'OR':
                return any(results) if results else False

        return False

    def apply_supplier_rules(self, product_id: str, default_supplier: str) -> str:
        """Apply business rules for supplier name overrides from database.

        LEGACY METHOD: Maintained for backwards compatibility.
        Only handles supplier_name field transformations.

        Args:
            product_id: The product ID
            default_supplier: Default supplier name from Programs-Products Column A

        Returns:
            Final supplier name after applying enabled rules
        """
        row_data = {
            'product_id': product_id,
            'supplier_name': default_supplier
        }

        supplier_name = default_supplier

        # Apply each enabled rule in priority order
        for rule in self.supplier_rules:
            # Only process supplier_override and if_then_else rules that target supplier_name
            if rule.rule_type not in ['supplier_override', 'if_then_else']:
                continue

            config = rule.config
            condition = config.get('condition', {})

            # Check if rule condition matches
            if self._evaluate_condition(row_data, condition):
                # OLD FORMAT: set_supplier
                if 'set_supplier' in config:
                    supplier_name = config['set_supplier']
                    break

                # NEW FORMAT: then_action
                then_action = config.get('then_action', {})
                if then_action.get('field') == 'supplier_name':
                    supplier_name = then_action.get('value', supplier_name)
                    break
            else:
                # ELSE action (NEW FORMAT only)
                else_action = config.get('else_action', {})
                if else_action and else_action.get('field') == 'supplier_name':
                    value = else_action.get('value', supplier_name)
                    # Handle $(field_name) references
                    if value and value.startswith('$(') and value.endswith(')'):
                        # Keep original value (e.g., $(supplier_name))
                        pass
                    else:
                        supplier_name = value

        return supplier_name

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
                # Handle both database objects and file dicts
                if isinstance(product, dict):
                    # File-based product (dict)
                    product_name = product.get('product_name')
                    proof_point = product.get('proof_point')
                    supplier_name = product.get('program_name')  # Program = Supplier in 98% of cases
                else:
                    # Database product (object)
                    product_name = product.product_name
                    proof_point = product.proof_point
                    supplier_name = product.program_name

                # Apply business rule overrides (2% of cases)
                supplier_name = self.apply_supplier_rules(str(product_id), supplier_name)

                return product_name, proof_point, supplier_name
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

        def normalize_name(name):
            """Normalize supplier name for comparison by removing special chars and extra spaces."""
            import re
            # Convert to lowercase, remove special characters, collapse multiple spaces
            normalized = re.sub(r'[^a-z0-9]+', ' ', name.lower())
            return normalized.strip()

        def get_keywords(name):
            """Extract significant keywords from supplier name (ignore common words)."""
            normalized = normalize_name(name)
            # Filter out common words that don't help with matching
            common_words = {'the', 'and', 'or', 'inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co', 'supply', 'group'}
            words = [w for w in normalized.split() if w not in common_words and len(w) >= 2]
            return set(words)

        def lookup_supplier_id(supplier_name):
            """Find tradenet_supplier_id by matching supplier name."""
            if not supplier_name:
                return None, None

            # Try exact match first
            if supplier_name in supplier_name_to_id:
                supplier_id = supplier_name_to_id[supplier_name]
                return supplier_name, supplier_id

            # Try fuzzy match with normalized names
            supplier_normalized = normalize_name(supplier_name)

            for full_name, supplier_id in supplier_name_to_id.items():
                db_normalized = normalize_name(full_name)

                # Check if normalized names match exactly
                if supplier_normalized == db_normalized:
                    return full_name, supplier_id

                # Check if one is contained in the other (at least 4 chars to avoid false positives)
                if len(supplier_normalized) >= 4 and len(db_normalized) >= 4:
                    if supplier_normalized in db_normalized or db_normalized in supplier_normalized:
                        return full_name, supplier_id

                # Check if significant keywords match (for cases like "Beacon Supply/QXO" vs "Beacon/QXO")
                supplier_keywords = get_keywords(supplier_name)
                db_keywords = get_keywords(full_name)

                # If all DB keywords are present in supplier keywords (or vice versa), it's a match
                if db_keywords and supplier_keywords:
                    if db_keywords.issubset(supplier_keywords) or supplier_keywords.issubset(db_keywords):
                        return full_name, supplier_id

            # No match found - return original name with no ID
            return supplier_name, None

        # Apply lookup
        if '_supplier_name_from_program' in df.columns:
            # First pass: lookup from the _supplier_name_from_program column
            supplier_info = df['_supplier_name_from_program'].apply(lookup_supplier_id)
            df['supplier_name'] = supplier_info.apply(lambda x: x[0] if x else None)
            df['tradenet_supplier_id'] = supplier_info.apply(lambda x: x[1] if x else None)

            # Drop temporary column
            df = df.drop(columns=['_supplier_name_from_program'], errors='ignore')
        elif 'supplier_name' in df.columns:
            # Second pass (after rules): re-lookup tradenet_supplier_id from updated supplier_name
            supplier_info = df['supplier_name'].apply(lookup_supplier_id)
            df['supplier_name'] = supplier_info.apply(lambda x: x[0] if x else None)
            df['tradenet_supplier_id'] = supplier_info.apply(lambda x: x[1] if x else None)

        return df

    def apply_flexible_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply flexible IF-THEN-ELSE rules to the entire DataFrame.

        This runs AFTER all enrichment is complete, so all fields are available.
        Applies rules in priority order to each row.

        Args:
            df: Fully enriched DataFrame

        Returns:
            DataFrame with rules applied
        """
        # Apply each enabled rule in priority order
        for rule in self.supplier_rules:
            # Only process if_then_else rules (new format)
            if rule.rule_type != 'if_then_else':
                continue

            config = rule.config
            condition = config.get('condition', {})
            then_actions = config.get('then_actions', [])  # NEW: Multiple actions
            then_action = config.get('then_action', {})  # OLD: Single action (backward compatible)
            else_action = config.get('else_action', {})

            # Support both single action (old) and multiple actions (new)
            if then_actions:
                actions_list = then_actions
            elif then_action:
                actions_list = [then_action]
            else:
                continue  # Skip if no actions

            # Apply rule to each row
            for idx, row in df.iterrows():
                row_data = row.to_dict()

                # Evaluate condition once per row
                condition_met = self._evaluate_condition(row_data, condition)

                if condition_met:
                    # Apply ALL actions in sequence
                    for action in actions_list:
                        action_type = action.get('type', 'set_value')

                        if action_type == 'move_column':
                            # Move data from source column to target column
                            source_field = action.get('source_field')
                            target_field = action.get('target_field')
                            clear_source = action.get('clear_source', True)

                            if source_field and target_field:
                                source_value = df.at[idx, source_field]
                                df.at[idx, target_field] = source_value

                                # Clear source if requested
                                if clear_source:
                                    df.at[idx, source_field] = ''

                        else:
                            # Set field to value
                            target_field = action.get('field')
                            value = action.get('value')

                            if target_field and value is not None:
                                df.at[idx, target_field] = value

                else:
                    # Condition didn't match - apply ELSE action if exists
                    if else_action:
                        target_field = else_action.get('field')
                        else_value = else_action.get('value')
                        # Handle $(field_name) references - keep original value
                        if target_field and else_value and not (else_value.startswith('$(') and else_value.endswith(')')):
                            df.at[idx, target_field] = else_value

        return df

    async def enrich_all(self, df: pd.DataFrame, file_products: Dict[str, Dict[str, Any]] = None) -> pd.DataFrame:
        """Run all enrichment steps.

        Args:
            df: Transformed DataFrame
            file_products: Optional dict of products from the uploaded file

        Returns:
            Fully enriched DataFrame
        """
        # Load all lookups once
        await self.load_lookups()

        # Use file products if provided, otherwise use database products
        if file_products:
            # Override products_cache with file-specific products
            self.products_cache = file_products

        # Enrich in sequence
        df = await self.enrich_member_info(df)
        df = await self.enrich_supplier_info(df)
        df = await self.enrich_product_info(df)

        # Match supplier name to TradeNet directory
        df = await self.match_supplier_from_name(df)

        # Apply flexible rules AFTER all enrichment (so all fields are available)
        df = self.apply_flexible_rules(df)

        # Re-match supplier IDs after rules may have changed supplier_name
        # This ensures tradenet_supplier_id matches the updated supplier_name
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
