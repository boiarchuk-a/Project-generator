from app.models.User import User
from app.models.Prediction import Prediction
from app.models.TitleModel import TitleModel

# --- Сервис генерации заголовков ---
class TitleService:
    def __init__(self, model: TitleModel):
        self.model = model

    def generate(self, user: User, text: str) -> Prediction:
        if user.balance.get_balance() < 10:
            raise ValueError("Недостаточно средств на балансе (нужно минимум 10₽)")

        user.balance.withdraw(10)
        title = self.model.generate_title(text)
        prediction = Prediction(input_text=text, generated_title=title)
        user.add_prediction(prediction)
        return prediction
