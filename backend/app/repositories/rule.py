"""Repository layer for rules operations."""
from typing import List, Optional
from sqlalchemy import select, delete, update, nulls_last
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import Rule
from app.schemas.rule import RuleCreate, RuleUpdate


class RuleRepository:
    """Repository for Rule operations."""

    @staticmethod
    async def get_all(db: AsyncSession, enabled_only: bool = False) -> List[Rule]:
        """Get all rules ordered by group then priority.

        Args:
            db: Database session
            enabled_only: If True, only return enabled rules
        """
        # Order by group (nulls last to put ungrouped at end), then priority within each group
        query = select(Rule).order_by(
            nulls_last(Rule.group),
            Rule.priority,
            Rule.id
        )

        if enabled_only:
            query = query.where(Rule.enabled == True)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, rule_id: int) -> Optional[Rule]:
        """Get a rule by ID."""
        result = await db.execute(
            select(Rule).where(Rule.id == rule_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, rule: RuleCreate) -> Rule:
        """Create a new rule."""
        db_rule = Rule(**rule.model_dump())
        db.add(db_rule)
        await db.flush()
        await db.refresh(db_rule)
        return db_rule

    @staticmethod
    async def update(
        db: AsyncSession, rule_id: int, rule: RuleUpdate
    ) -> Optional[Rule]:
        """Update a rule."""
        db_rule = await RuleRepository.get_by_id(db, rule_id)
        if not db_rule:
            return None

        update_data = rule.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)

        await db.flush()
        await db.refresh(db_rule)
        return db_rule

    @staticmethod
    async def delete(db: AsyncSession, rule_id: int) -> bool:
        """Delete a rule."""
        result = await db.execute(
            delete(Rule).where(Rule.id == rule_id)
        )
        return result.rowcount > 0

    @staticmethod
    async def reorder(db: AsyncSession, rule_priorities: dict[int, int]) -> bool:
        """Update priorities for multiple rules.

        Args:
            rule_priorities: Dict mapping rule_id to new priority
        """
        for rule_id, new_priority in rule_priorities.items():
            await db.execute(
                update(Rule)
                .where(Rule.id == rule_id)
                .values(priority=new_priority)
            )
        await db.flush()
        return True
