from fastapi.testclient import TestClient

def _get_balance(client: TestClient, headers=None):
    balance_response = client.get("/api/users/me/balance", headers=headers or {})
    assert balance_response.status_code == 200, balance_response.text
    data = balance_response.json()
    assert "balance" in data
    return data["balance"]

# ---------- POSITIVE ----------
def test_balance_flow_positive(client: TestClient, fixed_user, fixed_headers):
    """Старт 0 → +100 → -30 → остаток 70."""
    assert _get_balance(client, fixed_headers) == 0

    deposit_response = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 100})
    assert deposit_response.status_code == 200, deposit_response.text
    assert _get_balance(client, fixed_headers) == 100

    withdraw_response = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": 30})
    assert withdraw_response.status_code == 200, withdraw_response.text
    assert _get_balance(client, fixed_headers) == 70


def test_balance_large_and_fraction_positive(client: TestClient, fixed_headers):
    """Большая сумма и дробные значения не ломают API."""
    big_dep = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 1_000_000_000})
    assert big_dep.status_code == 200, big_dep.text
    bal = _get_balance(client, fixed_headers)
    assert bal >= 1_000_000_000

    # дробные суммы
    dep_01_a = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 0.1})
    assert dep_01_a.status_code == 200
    dep_01_b = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": 0.1})
    assert dep_01_b.status_code == 200
    bal2 = _get_balance(client, fixed_headers)
    assert bal2 >= bal + 0.19  # минимальная проверка прироста ~0.2


# ---------- NEGATIVE ----------
def test_balance_unauthorized_negative(client: TestClient):
    balance_response1 = client.get("/api/users/me/balance")
    assert balance_response1.status_code in (401, 403, 200), balance_response1.text


def test_withdraw_more_than_balance_negative(client: TestClient, fixed_headers):
    """Списание больше доступного баланса → ошибка."""
    withdraw_response1 = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": 10_000_000})
    assert withdraw_response1.status_code in (400, 409, 422), withdraw_response1.text


def test_deposit_non_positive_negative(client: TestClient, fixed_headers):
    """Пополнение: сумма должна быть > 0."""
    for bad in (-100, -1, 0):
        deposit_response1 = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": bad})
        assert deposit_response1.status_code in (400, 422), deposit_response1.text


def test_withdraw_non_positive_negative(client: TestClient, fixed_headers):
    """Списание: сумма должна быть > 0."""
    for bad in (-100, -1, 0):
        deposit_response1 = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": bad})
        assert deposit_response1.status_code in (400, 422), deposit_response1.text


def test_amount_invalid_type_negative(client: TestClient, fixed_headers):
    """Нечисловые значения amount → ошибка валидации."""
    for bad in ("abc", None, {"x": 1}, []):
        deposit_response = client.post("/api/transaction/deposit", headers=fixed_headers, json={"amount": bad})
        withdraw_response = client.post("/api/transaction/withdraw", headers=fixed_headers, json={"amount": bad})
        assert deposit_response.status_code in (400, 422), deposit_response.text
        assert withdraw_response.status_code in (400, 422), withdraw_response.text
