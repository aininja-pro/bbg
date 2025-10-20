"""Pydantic schemas for rules engine."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class RuleType(str, Enum):
    """Supported rule types."""
    SEARCH_REPLACE = "search_replace"
    IF_THEN_UPDATE = "if_then_update"
    IF_THEN_SET = "if_then_set"
    ROW_FILTER = "row_filter"
    CONCATENATE = "concatenate"


class RuleBase(BaseModel):
    """Base schema for Rule."""
    name: str = Field(..., max_length=255)
    rule_type: RuleType
    priority: int = Field(default=0, ge=0)
    enabled: bool = Field(default=True)
    config: Dict[str, Any] = Field(...)


class RuleCreate(RuleBase):
    """Schema for creating a Rule."""
    pass


class RuleUpdate(BaseModel):
    """Schema for updating a Rule."""
    name: Optional[str] = Field(None, max_length=255)
    rule_type: Optional[RuleType] = None
    priority: Optional[int] = Field(None, ge=0)
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class RuleResponse(RuleBase):
    """Schema for Rule response."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleReorderRequest(BaseModel):
    """Schema for reordering rules."""
    rule_priorities: Dict[int, int] = Field(
        ...,
        description="Mapping of rule_id to new priority"
    )
