"""Migration service to convert existing rules to nested condition format."""
import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.rule import Rule

logger = logging.getLogger(__name__)


def convert_to_nested_format(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a rule config to the new nested condition format.

    Args:
        config: Original rule configuration

    Returns:
        Updated config with nested condition format
    """
    condition = config.get('condition', {})

    # Skip if already in nested format
    if condition.get('type') == 'group':
        return config

    # Convert legacy format (supplier_name_equals, product_id_contains)
    if 'supplier_name_equals' in condition:
        new_condition = {
            'type': 'group',
            'logic': 'AND',
            'children': [
                {
                    'type': 'condition',
                    'field': 'supplier_name',
                    'operator': 'equals',
                    'value': condition['supplier_name_equals']
                }
            ]
        }

        # Add product_id_contains if present
        if 'product_id_contains' in condition:
            new_condition['children'].append({
                'type': 'condition',
                'field': 'product_id',
                'operator': 'contains',
                'value': condition['product_id_contains']
            })

        config['condition'] = new_condition
        return config

    # Convert legacy product_id_contains only
    if 'product_id_contains' in condition:
        new_condition = {
            'type': 'group',
            'logic': 'AND',
            'children': [
                {
                    'type': 'condition',
                    'field': 'product_id',
                    'operator': 'contains',
                    'value': condition['product_id_contains']
                }
            ]
        }
        config['condition'] = new_condition
        return config

    # Convert current flat format (logic + rules)
    if 'logic' in condition and 'rules' in condition:
        logic = condition.get('logic', 'AND')
        rules = condition.get('rules', [])

        new_condition = {
            'type': 'group',
            'logic': logic,
            'children': []
        }

        for rule in rules:
            new_condition['children'].append({
                'type': 'condition',
                'field': rule.get('field'),
                'operator': rule.get('operator'),
                'value': rule.get('value')
            })

        config['condition'] = new_condition
        return config

    # Return unchanged if no conversion needed
    return config


async def migrate_rules_to_nested_format(db: AsyncSession) -> Dict[str, Any]:
    """Migrate all existing rules to the nested condition format.

    Args:
        db: Database session

    Returns:
        Migration results with counts and details
    """
    results = {
        'total': 0,
        'migrated': 0,
        'skipped': 0,
        'errors': 0,
        'details': []
    }

    # Get all rules
    result = await db.execute(select(Rule))
    rules = result.scalars().all()
    results['total'] = len(rules)

    for rule in rules:
        try:
            original_config = rule.config.copy() if rule.config else {}
            original_condition = original_config.get('condition', {})

            # Check if already migrated
            if original_condition.get('type') == 'group':
                results['skipped'] += 1
                results['details'].append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'status': 'skipped',
                    'reason': 'Already in nested format'
                })
                continue

            # Convert to nested format
            new_config = convert_to_nested_format(original_config)

            # Check if conversion happened
            if new_config['condition'].get('type') == 'group':
                rule.config = new_config
                results['migrated'] += 1

                logger.info(f"Migrated rule '{rule.name}' (ID: {rule.id}) to nested format")
                results['details'].append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'status': 'migrated',
                    'before': original_condition,
                    'after': new_config['condition']
                })
            else:
                results['skipped'] += 1
                results['details'].append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'status': 'skipped',
                    'reason': 'No conversion needed or unknown format'
                })

        except Exception as e:
            results['errors'] += 1
            logger.error(f"Error migrating rule '{rule.name}' (ID: {rule.id}): {str(e)}")
            results['details'].append({
                'rule_id': rule.id,
                'rule_name': rule.name,
                'status': 'error',
                'error': str(e)
            })

    # Commit changes
    if results['migrated'] > 0:
        await db.commit()
        logger.info(f"Rule migration complete: {results['migrated']} migrated, {results['skipped']} skipped, {results['errors']} errors")
    else:
        logger.info("No rules needed migration")

    return results


async def run_migration(db: AsyncSession) -> None:
    """Run the rule migration at startup.

    Args:
        db: Database session
    """
    logger.info("Checking for rules that need migration to nested format...")
    results = await migrate_rules_to_nested_format(db)

    if results['migrated'] > 0:
        logger.info(f"Successfully migrated {results['migrated']} rules to nested condition format")
        for detail in results['details']:
            if detail['status'] == 'migrated':
                logger.info(f"  - {detail['rule_name']}: converted to nested format")
    elif results['total'] > 0:
        logger.info(f"All {results['total']} rules already in nested format or no conversion needed")
