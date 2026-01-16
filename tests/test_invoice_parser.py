from pathlib import Path

from app.invoice_parser import extract_pdf_text, parse_invoice_pdf


def test_parse_invoice_pdf_extracts_fields():
    pdf_path = Path("tests/fixtures/facture_exemple.pdf")
    data = parse_invoice_pdf(pdf_path.read_bytes())

    assert data["invoice_number"] == "02-13073-1"
    assert data["sold_at"] == "2026-01-16T10:01:41"
    assert "DREAM STATION" in data["store"]
    assert data["client_name"]
    assert "PC GAMER" in data["product_name"].upper()


def test_parse_invoice_pdf_deduplicates_pc_gamer_lines():
    pdf_path = Path("tests/fixtures/facture_exemple.pdf")
    pdf_bytes = pdf_path.read_bytes()
    data = parse_invoice_pdf(pdf_bytes)

    text = extract_pdf_text(pdf_bytes)
    assert text.count(data["product_name"]) >= 2
