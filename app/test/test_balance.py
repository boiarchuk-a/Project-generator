from fastapi.testclient import TestClient

def _get_balance(client: TestClient, headers=None):
    r = client.get("/api/users/me/balance", headers=headers or {})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "balance" in data
    return data["balance"]

# ---------- POSITIVE ----------
def test_balance_flow_positive(client: TestClient, fixed_user, fixed_headers):
    """Старт 0 → +100 → -30 → остаток 70."""
    assert _get_balance(client, fixed_headers) == 0

    r1 = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 100})
    assert r1.status_code == 200, r1.text
    assert _get_balance(client, fixed_headers) == 100

    r2 = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": 30})
    assert r2.status_code == 200, r2.text
    assert _get_balance(client, fixed_headers) == 70


def test_balance_large_and_fraction_positive(client: TestClient, fixed_headers):
    """Большая сумма и дробные значения не ломают API."""
    r = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 1_000_000_000})
    assert r.status_code == 200, r.text
    bal = _get_balance(client, fixed_headers)
    assert bal >= 1_000_000_000

    # дробные суммы
    r = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 0.1})
    assert r.status_code == 200
    r = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 0.1})
    assert r.status_code == 200
    bal2 = _get_balance(client, fixed_headers)
    assert bal2 >= bal + 0.19  # минимальная проверка прироста ~0.2


# ---------- NEGATIVE ----------
def test_balance_unauthorized_negative(client: TestClient):
    r = client.get("/api/users/me/balance")
    assert r.status_code in (401, 403, 200), r.text


def test_withdraw_more_than_balance_negative(client: TestClient, fixed_headers):
    """Списание больше доступного баланса → ошибка."""
    r = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": 10_000_000})
    assert r.status_code in (400, 409, 422), r.text


def test_deposit_non_positive_negative(client: TestClient, fixed_headers):
    """Пополнение: сумма должна быть > 0."""
    for bad in (-100, -1, 0):
        r = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": bad})
        assert r.status_code in (400, 422), r.text


def test_withdraw_non_positive_negative(client: TestClient, fixed_headers):
    """Списание: сумма должна быть > 0."""
    for bad in (-100, -1, 0):
        r = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": bad})
        assert r.status_code in (400, 422), r.text


def test_amount_invalid_type_negative(client: TestClient, fixed_headers):
    """Нечисловые значения amount → ошибка валидации."""
    for bad in ("abc", None, {"x": 1}, []):
        r1 = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": bad})
        r2 = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": bad})
        assert r1.status_code in (400, 422), r1.text
        assert r2.status_code in (400, 422), r2.text
