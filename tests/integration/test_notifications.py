import pytest

@pytest.mark.asyncio
async def test_create_immediate_notification(async_client):
    user_id = "notify-user"
    
    # Step 1: Create preferences
    pref_payload = {
        "email_enabled": True,
        "sms_enabled": True,
        "email": "notify@example.com",
        "phone_number": "+1111111111"
    }

    response = await async_client.post(f"/preferences/{user_id}", json=pref_payload)
    assert response.status_code == 200

    # Step 2: Trigger notification
    notif_payload = {
        "user_id": user_id,
        "subject": "Test Alert",
        "message": "This is a test notification"
    }

    response = await async_client.post("/notifications", json=notif_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "send_at" in data