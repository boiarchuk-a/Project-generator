from fastapi import Request
from typing import Optional, List

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List[str] = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

    async def is_valid(self):
        # Проверка логина (почта)
        if not self.username:
            self.errors.append("Email is required")
        elif "@" not in self.username or "." not in self.username:
            self.errors.append("Invalid email format")

        # Проверка пароля
        if not self.password:
            self.errors.append("Password is required")
        elif len(self.password) < 6:
            self.errors.append("Password must be at least 6 characters")

        return not self.errors
