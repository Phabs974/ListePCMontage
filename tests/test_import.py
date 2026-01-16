from pathlib import Path

from app.core.security import create_access_token


def test_import_invoice(client, vendor_user):
    token = create_access_token(str(vendor_user.id))
    pdf_path = Path("tests/fixtures/facture_exemple.pdf")
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/api/import/invoice",
            files={"file": ("invoice.pdf", handle, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"created", "already_exists"}
    assert data["order"]["invoice_number"] == "02-13073-1"
