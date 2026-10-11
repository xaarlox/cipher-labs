import re

from cipher_labs.core.alphabets import find_alphabet

DEFAULT_WIDTH = 10


def is_letter(char: str) -> bool:
    return find_alphabet(char) is not None


class PoemKeyValidator:
    @staticmethod
    def validate_width(width) -> int:
        if isinstance(width, bool):
            raise ValueError("Ширина вірша має бути цілим числом.")
        try:
            width = int(width)
        except (TypeError, ValueError):
            raise ValueError(f"Некоректна ширина '{width}'. Потрібне ціле число.") from None
        if not 1 <= width <= 99:
            raise ValueError("Ширина вірша має бути від 1 до 99.")
        return width

    @classmethod
    def validate(cls, poem, width=DEFAULT_WIDTH) -> list[str]:
        if not isinstance(poem, str):
            raise TypeError("Вірш має бути рядком.")
        width = cls.validate_width(width)

        rows = []
        for line in poem.splitlines():
            letters = "".join(c for c in line.lower() if is_letter(c))[:width]
            if letters:
                rows.append(letters)

        if not rows:
            raise ValueError("Вірш має містити хоча б один рядок з літерами (ukr/eng).")
        if len(rows) > 99:
            raise ValueError("Вірш занадто довгий: максимум 99 рядків.")
        return rows


class BookTextValidator:
    @staticmethod
    def validate(text) -> list[str]:
        if not isinstance(text, str):
            raise TypeError("Текст-ключ має бути рядком.")
        words = [w for w in re.findall(r"[^\W\d_]+", text.lower()) if is_letter(w[0])]
        if not words:
            raise ValueError("Текст-ключ не містить жодного слова.")
        return words
