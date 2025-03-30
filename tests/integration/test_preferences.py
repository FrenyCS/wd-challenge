import pytest


@pytest.mark.asyncio
async def test_create_and_get_preferences(async_client):
    user_id = "integration-user"
    payload = {
        "email_enabled": True,
        "sms_enabled": False,
        "email": "real@example.com",
        "phone_number": "+9999999999",
    }

    # Create
    response = await async_client.post(f"/preferences/{user_id}", json=payload)
    assert response.status_code == 200
    assert response.json() == payload

    # Get
    response = await async_client.get(f"/preferences/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email_enabled"] is True
    assert data["sms_enabled"] is False
    assert data["email"] == payload["email"]
    assert data["phone_number"] == payload["phone_number"]
