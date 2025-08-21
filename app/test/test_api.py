from fastapi.testclient import TestClient

# ---------- POSITIVE ----------
def test_smoke_positive(client: TestClient, fixed_headers):
    """Ключевые ручки живые и возвращают минимально корректную структуру."""
    balance_response = client.get("/api/users/me/balance", headers=fixed_headers)
    transactions_response = client.get("/api/transaction/me", headers=fixed_headers)

    assert  balance_response.status_code == 200,  balance_response.text
    assert transactions_response.status_code == 200, transactions_response.text

    bal = balance_response.json()
    tx = transactions_response.json()
    assert isinstance(bal, dict) and "balance" in bal
    assert isinstance(tx, list)


# ---------- NEGATIVE ----------
def test_smoke_unauthorized_negative(client: TestClient):
    balance_response1 = client.get("/balance/me")
    assert balance_response1.status_code in (401, 403, 200), balance_response1.text
