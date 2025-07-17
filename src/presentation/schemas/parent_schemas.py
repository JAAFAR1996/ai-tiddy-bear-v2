from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class ChildProfileCreateSchema(BaseModel):
    name: str
    age: int
    parent_id: UUID

class ChildProfileUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

class ChildProfileResponseSchema(BaseModel):
    id: UUID
    name: str
    age: int
    parent_id: UUID
    
    class Config:
        from_attributes = True