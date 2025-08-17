from dataclasses import dataclass, field
from datetime import datetime

# --- Предсказание заголовка ---
@dataclass
class Prediction:
    id: int
    input_text: str
    user_id: int
    generated_title: str
    timestamp: datetime = field(default_factory=datetime.now)

    def preview(self, max_len: int = 30) -> str:
        """Вернуть обрезанную версию текста"""
        return self.input_text[:max_len] + "..."

    def to_dict(self) -> dict:
        """Преобразовать в словарь для логирования/сохранения"""
        return {
            "input": self.input_text,
            "title": self.generated_title,
            "timestamp": self.timestamp.isoformat()
        }

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.generated_title}"