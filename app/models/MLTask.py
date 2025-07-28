from datetime import datetime
from dataclasses import dataclass

# --- Модель задачи для ML ---
@dataclass
class MLTask:
    id: int
    input_text: str
    created_at: datetime
    status: str = "NEW"

    def mark_as_processed(self):
        self.status = "processed"

    def preview_input(self, length: int = 20) -> str:
        return self.input_text[:length] + "..." if len(self.input_text) > length else self.input_text