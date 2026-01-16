import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Uuid
from sqlalchemy.sql import func

from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    store = Column(String, nullable=True)
    client_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    sold_at = Column(DateTime(timezone=True), nullable=False)
    prepared = Column(Boolean, nullable=False, server_default="false")
    built = Column(Boolean, nullable=False, server_default="false")
    delivered = Column(Boolean, nullable=False, server_default="false")
    status = Column(String, nullable=True)
    created_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
