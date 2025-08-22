from Balance import Balance
from decimal import Decimal


def test_ml_with_insufficient_balance(test_client):
    """Проверим, чтобы при недостаточном балансе запрос не принимался"""
    # В тестовом окружении баланс нулевой, поэтому никакой запрос не должен проходить
    TEST_QUERY = "Some text for testing"
    response = test_client.post("/query/execute", params={"text": TEST_QUERY})
    assert response.status_code == 400


def test_nl_with_incorrect_ml_text(test_client):
    """Проверим, чтобы запросы с некорректными текстами не принимались"""
    INCORRECT_TEXTS = [
        "", # Пустой текст
        "123", # Текст, содержащий только число
        "123abc", "123’abc", "’abc" # Некорректные составные тексты разного вида
    ]
    for incorrect_text in INCORRECT_TEXTS:
        response = test_client.post("/query/execute", params={"text": incorrect_text})
        assert response.status_code == 400


def test_ml(test_user, test_client, db_session):
    """Проверим, что нормальный запрос отравляется корректно"""
    # Чтобы запрос сработал, сначала вручную пополним баланс на заведомо большую
    # сумму, чем может пригодится
    balance = Balance(db_session)
    balance.replenish(test_user, Decimal(1_000_000))
    # Теперь сам запрос
    TEST_QUERY = "Some text for testing"
    response = test_client.post("/query/execute", params={"text": TEST_QUERY})
    assert response.status_code == 200


def test_ml_history(test_user, test_client, db_session):
    """Проверим, полученеи истории запросов"""
    # Чтобы запросы сработали, сначала вручную пополним баланс на заведомо большую
    # сумму, чем может пригодится
    balance = Balance(db_session)
    balance.replenish(test_user, Decimal(1_000_000))
    TEXTS = [
        "First query",
        "Second query",
        "Yet another query"
    ]
    # Теперь сами запросы
    for text in TEXTS:
        test_client.post("/query/execute", params={"text": text})
    # Поскольку вместо обращения к ML модели стоит "заглушка", здесь ограничимся
    # проверкой того, что количество записей в истории запросов соответствует реальному
    # количеству запросов
    history = test_client.get("/query/history")
    assert len(history.json()) == len(TEXTS)
