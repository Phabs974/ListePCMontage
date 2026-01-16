import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    role: UserRole | None = None
    password: str | None = None


class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
