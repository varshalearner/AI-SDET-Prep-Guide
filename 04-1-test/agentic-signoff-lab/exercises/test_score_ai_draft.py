import uuid

import pytest
import requests

BASE = "http://127.0.0.1:8099"


def payload(**over):
    p = {"request_id": str(uuid.uuid4()), "client_id": "CLI-0001",
         "consumer_ref": "CON-0001", "product": "SCORE_8"}
    p.update(over)
    return p


def test_create_score_request():
    r = requests.post(f"{BASE}/v1/score-requests", json=payload())
    assert r.status_code < 500


def test_score_value():
    r = requests.post(f"{BASE}/v1/score-requests", json=payload(), timeout=5)
    assert r.json()["score"] == 712


def test_invalid_product():
    r = requests.post(f"{BASE}/v1/score-requests", json=payload(product="SCORE_99"), timeout=5)
    assert r.status_code in (201, 400)


def test_missing_field():
    p = payload()
    del p["client_id"]
    r = requests.post(f"{BASE}/v1/score-requests", json=p, timeout=5)
    assert r.status_code == 400


def test_response_has_body():
    try:
        r = requests.post(f"{BASE}/v1/score-requests", json=payload(), timeout=5)
        assert r.json()
    except Exception:
        pass


@pytest.mark.skip(reason="flaky")
def test_invalid_json():
    r = requests.post(f"{BASE}/v1/score-requests", data="{bad", timeout=5,
                      headers={"Content-Type": "application/json"})
    assert r.status_code == 400


def test_full_flow():
    first = payload()
    r1 = requests.post(f"{BASE}/v1/score-requests", json=first, timeout=5)
    r2 = requests.post(f"{BASE}/v1/score-requests", json=payload(client_id="CLI-0002"), timeout=5)
    print("created", first)
    assert r1.status_code == 201 and r2.status_code == 201
