from dataclasses import dataclass, field
from datetime import datetime

# --- Предсказание заголовка ---
@dataclass
class Prediction:
    """Класс, представляющий результат работы модели - генерация заголовка по введенному тексту"""

    id: int
    input_text: str
    user_id: int
    generated_title: str
