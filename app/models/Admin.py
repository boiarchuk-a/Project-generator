from typing import List
from app.models.User import User

# --- Админ ---
class Admin(User):
    def __init__(self, id: int, email: str, password: str, username: str, role: str = 'admin'):
        super().__init__(id=id, email=email, password=password, username=username, role=role)

    def view_users(self, users: List[User]):
        print("\n Все пользователи:")
        for u in users:
            print(f" - {u.get_email}, баланс: {u.balance}, предсказаний: {len(u.predictions)}")

    def top_up_balance(self, user: User, amount: float):
        user.balance.deposit(amount)
        print(f" Баланс {user.get_email} пополнен на {amount}₽")