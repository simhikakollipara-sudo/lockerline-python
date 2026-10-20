"""Every test gets its own SQLite file, a fixed clock it can move, and the seed files from the repo."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from lockerline.app import create_app
from lockerline.settings import Settings


@pytest.fixture
def app(tmp_path):
    db_file = tmp_path / "test.db"
    settings = Settings(
        database_url=f"sqlite:///{db_file}",
        seed_dir=str(Path(__file__).parent.parent / "seed"),
    )
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db(app):
    """A fresh session factory for looking at rows the API wrote."""
    return app.state.sessionmaker


def drop(client, size="M", flat="302"):
    r = client.post("/drops", json={"size_class": size, "flat": flat})
    assert r.status_code == 201, r.text
    return r.json()


def fill(client, size, flat="302"):
    """Take every free door of one size."""
    while True:
        r = client.post("/drops", json={"size_class": size, "flat": flat})
        if r.status_code == 409:
            return
        assert r.status_code == 201, r.text