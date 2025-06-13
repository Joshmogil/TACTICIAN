from fastapi.testclient import TestClient
from app.main import app


def test_snapshot_endpoint():
    client = TestClient(app)
    resp = client.get("/users/test_user/snapshot")
    assert resp.status_code == 200
    data = resp.json()
    assert "recovery" in data
    assert "recommended_movements" in data
    assert isinstance(data["recommended_movements"], list)
