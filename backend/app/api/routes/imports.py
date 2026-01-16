from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.invoice_parser import InvoiceParseError, parse_invoice_pdf
from app.models.order import Order
from app.models.user import UserRole
from app.schemas.imports import ImportResult
from app.schemas.order import OrderOut

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/invoice", response_model=ImportResult)
def import_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImportResult:
    if current_user.role not in {UserRole.ADMIN, UserRole.VENDOR}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF required")

    try:
        data = parse_invoice_pdf(file.file.read())
    except InvoiceParseError as exc:
        return ImportResult(status="error", errors={"code": exc.code})

    existing = (
        db.query(Order).filter(Order.invoice_number == data["invoice_number"]).first()
    )
    if existing:
        return ImportResult(status="already_exists", order=OrderOut.model_validate(existing))

    order = Order(
        invoice_number=data["invoice_number"],
        store=data["store"],
        client_name=data["client_name"],
        product_name=data["product_name"],
        sold_at=datetime.fromisoformat(data["sold_at"]),
        created_by=current_user.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return ImportResult(status="created", order=order)
