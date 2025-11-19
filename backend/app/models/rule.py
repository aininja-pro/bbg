"""Rules engine model for business logic transformations."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from app.database import Base


class Rule(Base):
    """Business rules for data transformation."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    group = Column(String(100), nullable=True, index=True)  # For organizing rules by category
    rule_type = Column(
        String(50),
        nullable=False,
        # Types: search_replace, if_then_update, if_then_set, row_filter, concatenate
    )
    priority = Column(Integer, nullable=False, default=0, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    config = Column(JSON, nullable=False)
    # config structure varies by rule_type:
    # search_replace: {"column": "state", "find": "CA", "replace": "California"}
    # if_then_update: {"condition_column": "state", "condition_value": "TX", "update_column": "region", "update_value": "Southwest"}
    # if_then_set: {"condition": {"column": "qty", "operator": ">", "value": 100}, "set_column": "bulk", "set_value": true}
    # row_filter: {"column": "status", "operator": "==", "value": "active"}
    # concatenate: {"columns": ["address1", "city", "state"], "separator": ", ", "target_column": "full_address"}

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Rule(id={self.id}, name={self.name}, type={self.rule_type})>"
