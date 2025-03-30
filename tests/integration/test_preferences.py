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


@pytest.mark.asyncio
async def test_update_preferences(async_client):
    user_id = "integration-user"
    initial_payload = {
        "email_enabled": True,
        "sms_enabled": False,
        "email": "real@example.com",
        "phone_number": "+9999999999",
    }
    updated_payload = {
        "email_enabled": False,
        "sms_enabled": True,
        "email": "updated@example.com",
        "phone_number": "+1111111111",
    }

    # Create initial preferences
    response = await async_client.post(f"/preferences/{user_id}", json=initial_payload)
    assert response.status_code == 200

    # Update preferences
    response = await async_client.post(f"/preferences/{user_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json() == updated_payload

    # Get updated preferences
    response = await async_client.get(f"/preferences/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email_enabled"] is False
    assert data["sms_enabled"] is True
    assert data["email"] == updated_payload["email"]
    assert data["phone_number"] == updated_payload["phone_number"]
