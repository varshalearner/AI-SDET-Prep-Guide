import os
import uuid

import pytest
import requests

BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8099")
URL = f"{BASE}/v1/score-requests"


def payload(**over):
    p = {"request_id": str(uuid.uuid4()), "client_id": "CLI-0001",
         "consumer_ref": "CON-0001", "product": "SCORE_8"}
    p.update(over)
    return p


def test_score_requests_valid_returns_201_with_score_in_range():
    p = payload()
    r = requests.post(URL, json=p, timeout=5)
    assert r.status_code == 201
    body = r.json()
    assert body["request_id"] == p["request_id"]
    assert body["status"] == "ACCEPTED"
    assert isinstance(body["score"], int) and 300 <= body["score"] <= 850


def test_score_requests_invalid_product_returns_400():
    r = requests.post(URL, json=payload(product="SCORE_99"), timeout=5)
    assert r.status_code == 400


@pytest.mark.parametrize("field", ["request_id", "client_id", "consumer_ref", "product"])
def test_score_requests_missing_field_returns_400(field):
    p = payload()
    del p[field]
    r = requests.post(URL, json=p, timeout=5)
    assert r.status_code == 400
    assert r.json()["field"] == field


def test_score_requests_smoke():
    r = requests.post(URL, json=payload(), timeout=5)
    assert r.status_code < 500
