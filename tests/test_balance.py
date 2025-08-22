from Balance import Balance
from decimal import Decimal


def test_balance_check(test_user, test_client, db_session):
    """Проверим, что получение баланса работает корректно"""
    AMOUNT = Decimal(10_000)
    balance = Balance(db_session)
    balance.replenish(test_user, AMOUNT)
    response = test_client.get("/balance")
    # Значение типа Decimal сериализуется pydantic в строку, содержащую кавычки.
    # Так как в данном эндпоинте не используется JSON, убираем их вручную
    assert Decimal(response.text[1:-1]) == AMOUNT


def test_balance_replenish(test_user, test_client, db_session):
    """Проверим, что пополнение баланса работает корректно"""
    # Для проверки сделаем несколько пополнений и в конце проверим итоговый баланс
    balance = Balance(db_session)
    AMOUNTS = [1000, 500, 750]
    for amount in AMOUNTS:
        test_client.post("/balance/replenish", params={"amount": amount})
    assert balance[test_user] == sum(AMOUNTS)


def test_balance_history(test_user, test_client, db_session):
    """Проверим, что получение истории транзакций"""
    # Для проверки вручную занесем несколько транзакций и сравним их с тем,
    # что выдает api
    balance = Balance(db_session)
    AMOUNTS = [1000, 500, -1500]
    for amount in AMOUNTS:
        if amount > 0:
            balance.replenish(test_user, Decimal(amount))
        else:
            balance.pay(test_user, Decimal(amount)*(-1))
    response = test_client.get("/balance/history")
    for transaction, amount in zip(response.json(), AMOUNTS):
        assert Decimal(transaction["amount"]) == amount
    # Также проверим итоговый баланс
    assert balance[test_user] == sum(AMOUNTS)
