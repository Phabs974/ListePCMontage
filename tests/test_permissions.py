from datetime import datetime, timezone

from app.core.security import create_access_token


def test_permissions_vendor_builder(client, vendor_user, builder_user):
    vendor_token = create_access_token(str(vendor_user.id))
    builder_token = create_access_token(str(builder_user.id))

    payload = {
        "invoice_number": "INV-002",
        "store": "DREAM STATION SAINT PIERRE",
        "client_name": "Mme Jane Doe",
        "product_name": "PC GAMER Raijin",
        "sold_at": datetime.now(timezone.utc).isoformat(),
    }

    response = client.post("/api/orders", json=payload, headers={"Authorization": f"Bearer {vendor_token}"})
    order_id = response.json()["id"]

    response = client.patch(
        f"/api/orders/{order_id}",
        json={"built": True},
        headers={"Authorization": f"Bearer {vendor_token}"},
    )
    assert response.status_code == 403

    response = client.patch(
        f"/api/orders/{order_id}",
        json={"built": True},
        headers={"Authorization": f"Bearer {builder_token}"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/api/orders/{order_id}",
        json={"prepared": True},
        headers={"Authorization": f"Bearer {builder_token}"},
    )
    assert response.status_code == 403
