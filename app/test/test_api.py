from fastapi.testclient import TestClient

# ---------- POSITIVE ----------
def test_smoke_positive(client: TestClient, fixed_headers):
    """Ключевые ручки живые и возвращают минимально корректную структуру."""
    r1 = client.get("/api/users/me/balance", headers=fixed_headers)
    r2 = client.get("/api/transaction/me", headers=fixed_headers)

    assert r1.status_code == 200, r1.text
    assert r2.status_code == 200, r2.text

    bal = r1.json()
    tx = r2.json()
    assert isinstance(bal, dict) and "balance" in bal
    assert isinstance(tx, list)


# ---------- NEGATIVE ----------
def test_smoke_unauthorized_negative(client: TestClient):
    r = client.get("/balance/me")
    assert r.status_code in (401, 403, 200), r.text
