"""The wall shows its doors, their size and their state."""
from datetime import timedelta

import pytest
from sqlalchemy import select

from lockerline.models import Door
from tests.conftest import drop


def test_seed_loads_48_doors(client):
    r = client.get("/towers/A/doors")
    assert r.status_code == 200
    body = r.json()
    assert body["tower"] == "A"
    assert body["free"] == 48
    assert len(body["doors"]) == 48


def test_restart_is_idempotent(app, client):
    r = client.get("/towers/A/doors")
    assert r.status_code == 200
    assert r.json()["free"] == 48


def test_filters(client):
    r = client.get("/towers/A/doors?size=S")
    assert r.status_code == 200
    assert len(r.json()["doors"]) == 20

    r = client.get("/towers/A/doors?size=M")
    assert r.status_code == 200
    assert len(r.json()["doors"]) == 20

    r = client.get("/towers/A/doors?size=L")
    assert r.status_code == 200
    assert len(r.json()["doors"]) == 8

    r = client.get("/towers/A/doors?state=free")
    assert r.status_code == 200
    assert len(r.json()["doors"]) == 48

    r = client.get("/towers/A/doors?state=holding")
    assert r.status_code == 200
    assert len(r.json()["doors"]) == 0


def test_free_counts_the_filtered_doors(client):
    """ac_user: 'I filter to large, I see exactly 8 doors and the count says how many of those are free'."""
    drop(client, "L", "302")
    assert client.get("/towers/A/doors").json()["free"] == 47
    large = client.get("/towers/A/doors?size=L").json()
    assert len(large["doors"]) == 8 and large["free"] == 7
    assert client.get("/towers/A/doors?size=S").json()["free"] == 20
    holding = client.get("/towers/A/doors?state=holding").json()
    assert len(holding["doors"]) == 1 and holding["free"] == 0


def test_holding_door_shows_parcel_and_dwell(client, clock):
    d = drop(client)
    clock.advance(hours=3, minutes=30)
    body = client.get("/towers/A/doors?state=holding").json()
    assert len(body["doors"]) == 1
    door = body["doors"][0]
    assert door == {"no": d["door"], "size": "M", "state": "holding", "parcel_id": d["parcel_id"], "dwell_seconds": 12600}


def test_unknown_door_and_tower(client):
    r = client.get("/towers/A/doors/D99")
    assert r.status_code == 404
    assert r.json()["type"] == "/errors/no-such-door"

    r = client.get("/towers/Z/doors")
    assert r.status_code == 404
    assert r.json()["type"] == "/errors/no-such-tower"


def test_one_door(client, clock):
    d = drop(client, "S", "104")
    clock.advance(hours=3, minutes=30)
    body = client.get(f"/towers/A/doors/{d['door']}").json()
    assert body == {"no": d["door"], "size": "S", "state": "holding", "parcel_id": d["parcel_id"], "flat": "104", "dwell_seconds": 12600}
    assert client.get("/towers/A/doors/D02").json() == {"no": "D02", "size": "S", "state": "free"}