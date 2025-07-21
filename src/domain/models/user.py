# src/domain/models/user.py
from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    roles: list[str]
