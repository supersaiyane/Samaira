import pytest

# Uses seed_data fixture from conftest.py
@pytest.mark.anyio
async def test_list_accounts(client, seed_data):
    """Test GET /api/v1/accounts returns seeded data"""
    resp = await client.get("/api/v1/accounts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(acc["account_name"] == "TestAccount" for acc in data)


@pytest.mark.anyio
async def test_create_account(client):
    """Test POST /api/v1/accounts"""
    payload = {
        "cloud_provider": "AWS",
        "account_number": "222222222222",
        "account_name": "NewAccount"
    }
    resp = await client.post("/api/v1/accounts", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["account_name"] == "NewAccount"


@pytest.mark.anyio
async def test_invalid_account(client):
    """Test POST /api/v1/accounts with missing fields fails"""
    payload = {"cloud_provider": "AWS"}
    resp = await client.post("/api/v1/accounts", json=payload)
    assert resp.status_code == 422  # FastAPI validation error
