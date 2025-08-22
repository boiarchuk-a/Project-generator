from decimal import Decimal
import re

class IncorrectML(Exception):
    """Исключение для некорректного текста запроса"""


class ML:
    """Класс, представляющий запрос пользователя - задачу для ML модели 
    по генерации заголовков на основе текста."""

    @property
    def text(self) -> str:
        """Исходный текст, для которого будет сгенерирован заголовок"""
        return self.__text

    @property
    def price(self) -> Decimal:
        """Цена выполнения запроса (определяется по количеству символов в тексте)"""
        return self.__price

    def __count_complexity(self, text):
        """Оценивает сложность текста на основе количества символов и предложений"""
        # Убираем лишние пробелы и переносы строк
        cleaned_text = re.sub(r'\s+', ' ', text.strip())

        # Считаем количество символов (без пробелов)
        char_count = len(re.sub(r'\s', '', cleaned_text))

        # Считаем количество предложений (по точкам, восклицательным и вопросительным знакам)
        sentence_count = len(re.findall(r'[.!?]+', cleaned_text))
        if sentence_count == 0:
            sentence_count = 1  # Минимум одно предложение

        # Сложность = символы * коэффициент сложности предложений
        complexity = char_count * (1 + sentence_count * 0.1)
        return max(complexity, 1)  # Минимум 1

    def __repr__(self):
        return f"Query(text='{self.__text[:50]}...')" if len(self.__text) > 50 else f"Query(text='{self.__text}')"

    def __init__(self, text):
        """Принимает текст, состоящий хотя бы из 10 символов (без учета пробелов).
        Если текст не соответствует данному критерию, выбрасывается исключение ValueError"""
        CHAR_PRICE = Decimal(0.5)  # Цена за единицу сложности
        MIN_TEXT_LENGTH = 10  # Минимальное количество символов

        self.__text = text.strip()

        # Проверяем, что текст не пустой
        if not self.__text:
            raise IncorrectQuery("Текст не может быть пустым")

        # Проверяем минимальную длину текста (без пробелов)
        text_without_spaces = re.sub(r'\s', '', self.__text)
        if len(text_without_spaces) < MIN_TEXT_LENGTH:
            raise IncorrectQuery(f"Текст должен содержать хотя бы {MIN_TEXT_LENGTH} символов (без учета пробелов)")

        # Проверяем, что текст содержит осмысленный контент (не только спецсимволы/цифры)
        meaningful_chars = re.findall(r'[a-zA-Zа-яА-Я]', self.__text)
        if len(meaningful_chars) < 5:  # Хотя бы 5 букв
            raise IncorrectQuery("Текст должен содержать осмысленное содержание")

        # Рассчитываем цену на основе сложности текста
        complexity = self.__count_complexity(self.__text)
        self.__price = Decimal(complexity * float(CHAR_PRICE)).quantize(Decimal('0.01'))

        # Устанавливаем минимальную и максимальную цену
        MIN_PRICE = Decimal('5.00')
        MAX_PRICE = Decimal('500.00')
        self.__price = max(min(self.__price, MAX_PRICE), MIN_PRICE)

    def get_text_stats(self) -> dict:
        """Возвращает статистику текста для отладки"""
        cleaned_text = re.sub(r'\s+', ' ', self.__text.strip())
        return {
            'total_chars': len(self.__text),
            'chars_without_spaces': len(re.sub(r'\s', '', self.__text)),
            'word_count': len(cleaned_text.split()),
            'sentence_count': len(re.findall(r'[.!?]+', cleaned_text)) or 1,
            'complexity_score': self.__count_complexity(self.__text),
            'price': float(self.__price)
        }