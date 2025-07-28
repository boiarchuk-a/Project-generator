
# --- Класс баланса ---
class Balance:
    def __init__(self, amount: float = 0.0):
        self.__amount = amount

    def deposit(self, value: float):
        if value < 0:
            raise ValueError("Сумма должна быть положительной")
        self.__amount += value

    def withdraw(self, value: float):
        if value > self.__amount:
            raise ValueError("Недостаточно средств")
        self.__amount -= value

    def get_balance(self) -> float:
        return self.__amount

    def __str__(self):
        return f"{self.__amount:.2f} ₽"
