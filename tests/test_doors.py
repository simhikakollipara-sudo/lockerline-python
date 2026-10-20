"""48 doors seeded once, filters, derived state, both refusals."""
from fastapi.testclient import TestClient
from lockerline.app import create_app
from lockerline.settings import Settings


def test_wall_and_restart(tmp_path):
    # Use a file-based sqlite database in tmp_path so it persists across two app starts
    db_file = tmp_path / "test.db"
    settings = Settings(database_url=f"sqlite:///{db_file}")

    # First start
    app1 = create_app(settings)
    with TestClient(app1) as client:
        res = client.get("/towers/A/doors")
        assert res.status_code == 200
        data = res.json()
        assert len(data["doors"]) == 48
        assert data["free"] == 48

    # Second start on the exact same database (idempotency check)
    app2 = create_app(settings)
    with TestClient(app2) as client:
        res = client.get("/towers/A/doors")
        assert res.status_code == 200
        data = res.json()
        assert len(data["doors"]) == 48
        assert data["free"] == 48


def test_filters_and_errors(tmp_path):
    db_file = tmp_path / "test2.db"
    settings = Settings(database_url=f"sqlite:///{db_file}")
    app = create_app(settings)

    with TestClient(app) as client:
        # Size filter Large
        res = client.get("/towers/A/doors?size=L")
        assert res.status_code == 200
        assert len(res.json()["doors"]) == 8

        # Invalid size filter returns 400
        res = client.get("/towers/A/doors?size=XL")
        assert res.status_code == 400

        # Non-existent tower returns 404
        res = client.get("/towers/Z/doors")
        assert res.status_code == 404