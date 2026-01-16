import io
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class InvoiceParseError(Exception):
    def __init__(self, code: str, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code = code


def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        import fitz

        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as exc:  # pragma: no cover - defensive guard
            raise InvoiceParseError("PDF_TEXT_EXTRACTION_FAILED") from exc


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_invoice_pdf(pdf_bytes: bytes) -> dict:
    text = extract_pdf_text(pdf_bytes)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    invoice_match = re.search(r"Facture\s+N°\s*([0-9-]+)", text, re.MULTILINE)
    if not invoice_match:
        raise InvoiceParseError("MISSING_INVOICE_NUMBER")
    invoice_number = invoice_match.group(1).strip()

    date_match = re.search(
        r"Date\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{4}),\s*([0-9]{2}:[0-9]{2}:[0-9]{2})",
        text,
    )
    if not date_match:
        raise InvoiceParseError("MISSING_SOLD_AT")
    sold_at = datetime.strptime(
        f"{date_match.group(1)} {date_match.group(2)}", "%d/%m/%Y %H:%M:%S"
    ).isoformat()

    store = next(
        (line for line in lines if re.search(r"DREAM STATION", line, re.IGNORECASE)),
        None,
    )
    if not store:
        raise InvoiceParseError("MISSING_STORE")

    client_name = next(
        (line for line in lines if re.match(r"^(Mme|M\.|Mr|Mlle)\s+", line)),
        None,
    )
    if not client_name:
        raise InvoiceParseError("MISSING_CLIENT")

    product_candidates: list[str] = []
    seen: set[str] = set()
    component_keywords = (
        "boitier",
        "cpu",
        "carte mere",
        "carte mère",
        "ram",
        "ssd",
        "ventirad",
        "carte graphique",
        "alimentation",
    )
    for line in lines:
        if not re.search(r"(PACK COMPLET\s+)?PC\s+GAMER", line, re.IGNORECASE):
            continue
        cleaned = _normalize_space(line)
        if any(keyword in cleaned.lower() for keyword in component_keywords):
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        product_candidates.append(cleaned)

    if not product_candidates:
        raise InvoiceParseError("MISSING_PRODUCT")

    product_name = product_candidates[0]

    logger.info(
        "Invoice parse preview invoice=%s sold_at=%s store=%s client=%s product=%s",
        invoice_number,
        sold_at,
        store,
        client_name,
        product_name,
    )

    return {
        "invoice_number": invoice_number,
        "sold_at": sold_at,
        "store": store,
        "client_name": client_name,
        "product_name": product_name,
    }
