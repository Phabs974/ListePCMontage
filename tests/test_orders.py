from datetime import datetime, timezone

from app.core.security import create_access_token


def test_create_order(client, vendor_user):
    token = create_access_token(str(vendor_user.id))
    payload = {
        "invoice_number": "INV-001",
        "store": "DREAM STATION SAINT PIERRE",
        "client_name": "Mme Jane Doe",
        "product_name": "PC GAMER Raijin",
        "sold_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/orders", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["invoice_number"] == "INV-001"
