"""API endpoints for rules management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.rule import RuleRepository
from app.schemas.rule import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
    RuleReorderRequest,
)

router = APIRouter(prefix="/api/rules", tags=["Rules"])


@router.get("", response_model=List[RuleResponse])
async def get_rules(
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all rules ordered by priority."""
    rules = await RuleRepository.get_all(db, enabled_only=enabled_only)
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific rule by ID."""
    rule = await RuleRepository.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID {rule_id} not found"
        )
    return rule


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: RuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new rule."""
    new_rule = await RuleRepository.create(db, rule)
    return new_rule


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    rule: RuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a rule."""
    updated_rule = await RuleRepository.update(db, rule_id, rule)
    if not updated_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID {rule_id} not found"
        )
    return updated_rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a rule."""
    deleted = await RuleRepository.delete(db, rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID {rule_id} not found"
        )
    return None


@router.post("/reorder", status_code=status.HTTP_200_OK)
async def reorder_rules(
    request: RuleReorderRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reorder rules by updating priorities."""
    await RuleRepository.reorder(db, request.rule_priorities)
    return {"message": "Rules reordered successfully"}
