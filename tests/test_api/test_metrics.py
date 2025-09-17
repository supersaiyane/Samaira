import pytest

@pytest.mark.asyncio
async def test_anomalies_count(client):
    resp = await client.get("/api/v1/metrics/anomalies/count")
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data

@pytest.mark.asyncio
async def test_savings_total(client):
    resp = await client.get("/api/v1/metrics/savings/total")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
