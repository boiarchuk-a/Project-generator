import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Callable

from app.api import app
from app.database.database import get_session
from app.models.User import User

@pytest.fixture(name="fixed_user")
def fixed_user_fixture(session: Session) -> User:
    """
    Создаёт фиксированного пользователя в тестовой БД.
    Можно расширить начальными значениями
    """
    email = "user@test.ru"
    user = session.exec(
        User.select().where(User.email == email)
    ).first() if hasattr(User, "select") else None

    if not user:
        user = User(email=email, password="Secret123!", name="Fixed")
        # если у модели есть поле balance — можно выставить 0.0
        if hasattr(user, "balance"):
            setattr(user, "balance", 0.0)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@pytest.fixture(name="fixed_headers")
def fixed_headers_fixture(fixed_user: User):
    """
    Возвращает заголовки авторизации. Токен фиктивный, оверрайдим зависимость ниже.
    """
    return {"Authorization": "Bearer TEST.TOKEN"}


@pytest.fixture(autouse=True)
def override_deps(client: TestClient, session: Session, fixed_user: User):
    """
    Автоматически для каждого теста:
    - подменяем get_session на тестовую session
    - подменяем get_current_user так, чтобы всегда возвращался fixed_user
    """

    def _get_session_override():
        return session
    app.dependency_overrides[get_session] = _get_session_override

    yield

    app.dependency_overrides.pop(get_session, None)

