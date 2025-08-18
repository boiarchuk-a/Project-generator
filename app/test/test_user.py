from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.User import User

# ---------- POSITIVE ----------
def test_user_fixture_positive(session: Session, fixed_user: User):
    """Фикс-пользователь создан и доступен в БД."""
    db_user = session.get(User, fixed_user.id)
    assert db_user is not None
    assert db_user.email == "user@test.ru"


def test_signup_positive(client: TestClient):
    """Регистрация нового пользователя проходит успешно."""
    email = "new_user@test.ru"
    r = client.post("api/users/signup", json={"email": email, "password": "Secret123!", "name": "New"})
    assert r.status_code in (200, 201), r.text
    assert r.json().get("email") == email


# ---------- NEGATIVE ----------
def test_signup_duplicate_email_negative(client: TestClient):
    """Повторная регистрация с тем же email должна вернуть ошибку."""
    email = "dup_user@test.ru"
    r1 = client.post("api/users/signup", json={"email": email, "password": "Secret123!", "name": "Dup"})
    assert r1.status_code in (200, 201), r1.text

    r2 = client.post("api/users/signup", json={"email": email, "password": "Secret123!", "name": "Dup2"})
    assert r2.status_code in (400, 409, 422), r2.text


def test_signup_missing_fields_negative(client: TestClient):
    """Отсутствие обязательных полей → ошибка валидации."""
    r = client.post("api/users/signup", json={})
    assert r.status_code in (400, 422), r.text


def test_signup_bad_email_negative(client: TestClient):
    """Некорректный email → ошибка валидации."""
    r = client.post("api/users/signup", json={"email": "bademail", "password": "x", "name": "NoAt"})
    assert r.status_code in (400, 422), r.text


def test_signup_empty_password_negative(client: TestClient):
    """Пустой пароль → ошибка валидации."""
    r = client.post("api/users/signup", json={"email": "a@b", "password": "", "name": "EmptyPwd"})
    assert r.status_code in (400, 422), r.text
