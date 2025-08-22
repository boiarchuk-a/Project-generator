from fastapi.testclient import TestClient
import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
import sys

# В Dockerfile.app в PYTHONPATH добавляется текущая рабочая директория (/ml_3),
# из которой осуществляется запуск, чтобы сработали импорты к параллелльным модулям.
# Сделаем то же самое и при тестировании
sys.path.insert(0, str(Path.cwd()))

from api import app
from auth import auth_settings, create_access_token
from database.database import get_session
from mlworkerproxy import MLWorkerProxy
from models.base import Base
from Admin import Admin


@pytest.fixture(name="db_session")
def db_session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def dependencies_fixture(db_session):
    def get_session_override():
        return db_session
    app.dependency_overrides[get_session] = get_session_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(db_session):
    users_manager = Admin(db_session)
    user_data = {
        "username": "test_user",
        "password": "qwerty123",
        "email": "test_user@gmail.com",
        "fullname": "Test User",
    }
    test_user = users_manager.signup(**user_data)
    return test_user


@pytest.fixture(name="test_client")
def test_client_fixture(test_user):
    # Используем пользователя, созданного test_user_fixture, для формирования токена,
    # применяемого в дальнейших тестах
    test_client = TestClient(app)
    test_client.cookies.set(
        auth_settings.JWT_TOKEN_COOKIE_KEY,
        f"Bearer {create_access_token(test_user)}"
    )
    return test_client


@pytest.fixture(autouse=True)
def mod_ml_worker_proxy(test_client):
    # Используем monkey patching, чтобы изменить для целей тестирования поведение
    # класса MLWorkerProxy
    default_publish_to_mq = MLWorkerProxy.publish_to_mq
    def mod_publish_to_mq(self, body):
        # Функция изобразит работу реального воркера, фактически не обращаясь
        # к нему через очередь сообщений
        RUNNING, COMPLETED = 1, 2
        body = json.loads(body)
        query_log_id = body["query_log_id"]
        # Обвновим статус о том, что запрос в работе
        test_client.put(
            "/query/update",
            json={"id": query_log_id, "status": RUNNING, "result_dict": None},
        )
        # Возвратим результат (для теста - нулевой) с соответствующим статусом
        result = {
            "anger": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "neutral": 0,
            "sadness": 0,
            "surprise": 0
        }
        test_client.put(
            "/query/update",
            json={"id": query_log_id, "status": COMPLETED, "result_dict": result},
        )
    MLWorkerProxy.publish_to_mq = mod_publish_to_mq
    yield
    MLWorkerProxy.publish_to_mq = default_publish_to_mq
