"""
Configuration and drawing history database models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    box_id = Column(String, nullable=False)
    terminals = Column(Integer, default=0)
    holes_top = Column(Integer, default=0)
    holes_bottom = Column(Integer, default=0)
    holes_left = Column(Integer, default=0)
    holes_right = Column(Integer, default=0)
    controller_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    drawing_number = Column(String, unique=True, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", foreign_keys=[user_id])
    controller = relationship("User", foreign_keys=[controller_id])
