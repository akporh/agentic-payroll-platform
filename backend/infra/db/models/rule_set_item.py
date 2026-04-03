from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class RuleSetItem(Base):
    """One rule within a published rule set.

    Content (rule_definition_json) is copied at publish time and never
    modified. All historical rates are preserved via accumulated rows.
    """
    __tablename__ = "rule_set_item"

    rule_set_id          = Column(UUID(as_uuid=True), ForeignKey("rule_set.rule_set_id"), primary_key=True)
    rule_name            = Column(Text, nullable=False, primary_key=True)
    rule_definition_json = Column(JSONB, nullable=False)
    rule_type            = Column(Text, nullable=True)
