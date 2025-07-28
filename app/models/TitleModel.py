
# --- Модель заголовка (заглушка) ---
class TitleModel:
    def generate_title(self, text: str) -> str:
        """Основной метод генерации заголовка"""
        raise NotImplementedError("Нужно переопределить метод")

    def evaluate_quality(self, title: str) -> str:
        """Простая эвристика для оценки качества заголовка"""
        if len(title) < 10:
            return f"Слишком короткий ({len(title)} символов)"
        elif len(title) > 50:
            return f"Слишком длинный ({len(title)} символов)"
        else:
            return "Хороший"

    def format_title(self, title: str) -> str:
        """Приводит заголовок к формату: первая буква заглавная, без точки"""
        return title.capitalize().strip('.!?')

class SimpleModel(TitleModel):
    def generate_title(self, text: str) -> str:
        return f"[Simple] {text[:30]}..."

class FancyModel(TitleModel):
    def generate_title(self, text: str) -> str:
        return f"[Fancy✨] {text.upper()[:40]}!"
