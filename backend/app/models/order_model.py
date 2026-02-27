"""
Order SQLAlchemy model
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    box_id = Column(String, nullable=False)
    terminals = Column(Integer, nullable=False, default=0)
    holes_top = Column(Integer, nullable=False, default=0)
    holes_bottom = Column(Integer, nullable=False, default=0)
    holes_left = Column(Integer, nullable=False, default=0)
    holes_right = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
