import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import fitz


@dataclass
class InvoiceData:
    invoice_number: str
    sold_at: datetime
    store: str | None
    client_name: str
    product_name: str


def _first_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def _find_store(lines: Iterable[str]) -> str | None:
    for line in lines:
        if re.search(r"DREAM STATION", line, re.IGNORECASE):
            return line.strip()
    return None


def _find_client(lines: Iterable[str]) -> str | None:
    for line in lines:
        if re.match(r"^(M\.|Mme|Mr|Mlle)\s+", line):
            return line.strip()
    return None


def _find_product(lines: Iterable[str]) -> str | None:
    products = []
    for line in lines:
        if re.search(r"(PACK COMPLET\s+)?PC\s+GAMER", line, re.IGNORECASE):
            cleaned = re.sub(r"\s+", " ", line).strip()
            products.append(cleaned)
    for item in products:
        if any(keyword in item.lower() for keyword in ["boitier", "cpu", "carte", "ram", "ssd"]):
            continue
        return item
    return products[0] if products else None


def parse_invoice_pdf(path: str) -> tuple[InvoiceData | None, dict[str, str]]:
    with fitz.open(path) as doc:
        text = "\n".join(page.get_text("text") for page in doc)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    errors: dict[str, str] = {}

    invoice_number = _first_match(r"Facture\s+N°\s*([0-9-]+)", text)
    if not invoice_number:
        errors["invoice_number"] = "Invoice number not found"

    date_match = re.search(
        r"Date\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{4}),\s*([0-9]{2}:[0-9]{2}:[0-9]{2})",
        text,
    )
    sold_at = None
    if date_match:
        sold_at = datetime.strptime(
            f"{date_match.group(1)} {date_match.group(2)}", "%d/%m/%Y %H:%M:%S"
        )
    else:
        errors["sold_at"] = "Sold date not found"

    store = _find_store(lines)
    if not store:
        errors["store"] = "Store not found"

    client_name = _find_client(lines)
    if not client_name:
        errors["client_name"] = "Client name not found"

    product_name = _find_product(lines)
    if not product_name:
        errors["product_name"] = "Product name not found"

    if errors:
        return None, errors

    return (
        InvoiceData(
            invoice_number=invoice_number,
            sold_at=sold_at,
            store=store,
            client_name=client_name,
            product_name=product_name,
        ),
        {},
    )
