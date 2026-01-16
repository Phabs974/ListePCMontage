import uuid
from datetime import datetime

from pydantic import BaseModel


class OrderBase(BaseModel):
    invoice_number: str
    store: str | None = None
    client_name: str
    product_name: str
    sold_at: datetime
    prepared: bool = False
    built: bool = False
    delivered: bool = False
    status: str | None = None


class OrderCreate(OrderBase):
    pass


class OrderPatch(BaseModel):
    prepared: bool | None = None
    built: bool | None = None
    delivered: bool | None = None
    status: str | None = None


class OrderOut(OrderBase):
    id: uuid.UUID
    created_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
