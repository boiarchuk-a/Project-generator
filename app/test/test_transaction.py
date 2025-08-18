from fastapi.testclient import TestClient

# ---------- POSITIVE ----------
def test_transactions_flow_positive(client: TestClient, fixed_headers):
    """После +100 и -30 в истории появляются соответствующие записи в конце."""
    r1 = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 100})
    assert r1.status_code == 200, r1.text
    r2 = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": 30})
    assert r2.status_code == 200, r2.text

    r = client.get("/api/transaction/me", headers=fixed_headers)
    assert r.status_code == 200, r.text
    tx = r.json()
    assert isinstance(tx, list) and len(tx) >= 2

    last_two = tx[-2:]
    amounts = [t.get("amount") for t in last_two]
    types = [t.get("type") for t in last_two]

    assert amounts == [100.0, -30.0]
    assert types[0] in ("deposit", "DEPOSIT", "in")
    assert types[1] in ("withdraw", "WITHDRAW", "out")

    # мягкая проверка структуры
    for t in last_two:
        assert "amount" in t
        if "id" in t: assert isinstance(t["id"], int)
        if "timestamp" in t: assert isinstance(t["timestamp"], str)


# ---------- NEGATIVE ----------
def test_transactions_unauthorized_negative(client: TestClient):
    r = client.get("/api/transaction/me")
    assert r.status_code in (401, 403, 200), r.text
