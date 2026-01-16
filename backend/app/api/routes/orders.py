from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.order import Order
from app.models.user import UserRole
from app.schemas.order import OrderCreate, OrderOut, OrderPatch

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders(
    view: str = Query("all", pattern="^(all|to_prepare|to_build|to_deliver|done)$"),
    q: str | None = None,
    from_date: datetime | None = Query(None, alias="from"),
    to_date: datetime | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[OrderOut]:
    query = db.query(Order)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Order.invoice_number.ilike(like),
                Order.client_name.ilike(like),
                Order.product_name.ilike(like),
                Order.store.ilike(like),
            )
        )

    if from_date:
        query = query.filter(Order.sold_at >= from_date)
    if to_date:
        query = query.filter(Order.sold_at <= to_date)

    if view == "to_prepare":
        query = query.filter(
            and_(Order.prepared.is_(False), or_(Order.status.is_(None), Order.status != "DEJA DONNER"))
        )
    elif view == "to_build":
        query = query.filter(
            and_(
                Order.prepared.is_(True),
                Order.built.is_(False),
                or_(Order.status.is_(None), Order.status != "DEJA DONNER"),
            )
        )
    elif view == "to_deliver":
        query = query.filter(and_(Order.built.is_(True), Order.delivered.is_(False)))
    elif view == "done":
        query = query.filter(Order.delivered.is_(True))

    return query.order_by(Order.sold_at.desc()).all()


@router.post("", response_model=OrderOut)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> OrderOut:
    if current_user.role not in {UserRole.ADMIN, UserRole.VENDOR}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    existing = db.query(Order).filter(Order.invoice_number == payload.invoice_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice already exists")

    order = Order(**payload.model_dump(), created_by=current_user.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}", response_model=OrderOut)
def patch_order(
    order_id: str,
    payload: OrderPatch,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> OrderOut:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    updates = payload.model_dump(exclude_unset=True)

    if current_user.role == UserRole.VENDOR:
        if "built" in updates:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify built")
    elif current_user.role == UserRole.BUILDER:
        forbidden_fields = {"prepared", "delivered", "status"}
        if forbidden_fields.intersection(updates):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden fields")
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    for key, value in updates.items():
        setattr(order, key, value)

    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}")
def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"status": "deleted"}
