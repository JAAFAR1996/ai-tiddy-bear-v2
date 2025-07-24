"""Base SQLAlchemy configuration for all models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
