from datetime import datetime
from typing import Optional

class User:
    def __init__(
        self,
        id: str,
        email: str,
        role: str,
        name: str,
        is_active: bool = True,
        created_at: Optional[int] = None,
        last_login: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.role = role
        self.name = name
        self.is_active = is_active
        self.created_at = created_at
        self.last_login = last_login

    def __repr__(self):
        return f"<User {self.id} ({self.email})>"
