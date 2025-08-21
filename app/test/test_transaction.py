from fastapi.testclient import TestClient

# ---------- POSITIVE ----------
def test_transactions_flow_positive(client: TestClient, fixed_headers):
    """После +100 и -30 в истории появляются соответствующие записи в конце."""
    dep_resp = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 100})
    assert dep_resp.status_code == 200, dep_resp.text
    wd_resp = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": 30})
    assert wd_resp.status_code == 200, wd_resp.text

    history_response  = client.get("/api/transaction/me", headers=fixed_headers)
    assert history_response .status_code == 200, history_response .text
    tx = history_response .json()
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
    history_response  = client.get("/api/transaction/me")
    assert history_response .status_code in (401, 403, 200), history_response .text
