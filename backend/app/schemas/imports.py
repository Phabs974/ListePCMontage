from pydantic import BaseModel

from app.schemas.order import OrderOut


class ImportResult(BaseModel):
    status: str
    order: OrderOut | None = None
    errors: dict[str, str] | None = None
