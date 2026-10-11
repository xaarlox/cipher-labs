import random
import re

from cipher_labs.core.base import BaseCipher
from cipher_labs.core.common_validators import DataValidator
from .validators import DEFAULT_WIDTH, PoemKeyValidator, BookTextValidator, is_letter

SPACE_TOKEN = "_"

_POSITION_RE = re.compile(r"^(\d+)\s*/\s*(\d+)$")


def _split_tokens(code: str) -> list[str]:
    if not isinstance(code, str):
        raise TypeError(f"Очікувався рядок, отримано {type(code).__name__}.")
    tokens = [t.strip() for t in code.split(",") if t.strip()]
    if not tokens:
        raise ValueError("Шифрограма порожня.")
    return tokens


class PoemCipher(BaseCipher):
    def __init__(self, width: int = DEFAULT_WIDTH, rng: random.Random | None = None):
        self.width = PoemKeyValidator.validate_width(width)
        self._rng = rng or random.Random()

    @staticmethod
    def _build_index(rows: list[str]) -> dict[str, list[tuple[int, int]]]:
        index: dict[str, list[tuple[int, int]]] = {}
        for r, row in enumerate(rows, start=1):
            for c, char in enumerate(row, start=1):
                index.setdefault(char, []).append((r, c))
        return index

    def encrypt(self, data: str, key: str) -> str:
        text = DataValidator.validate_text(data)
        rows = PoemKeyValidator.validate(key, self.width)
        index = self._build_index(rows)

        tokens: list[str] = []
        missing: set[str] = set()

        for char in text.lower():
            if char.isspace():
                tokens.append(SPACE_TOKEN)
                continue
            if not is_letter(char):  # Цифри та розділові знаки не шифруються
                continue

            positions = index.get(char)
            if not positions:
                missing.add(char)
                continue
            r, c = self._rng.choice(positions)
            tokens.append(f"{r}/{c}")

        if missing:
            raise ValueError(
                "У вірші відсутні літери: " + ", ".join(sorted(missing)) +
                ". Оберіть довший вірш або збільшіть ширину."
            )
        if not any(t != SPACE_TOKEN for t in tokens):
            raise ValueError("У тексті немає літер для шифрування.")
        return ", ".join(tokens)

    def decrypt(self, data: str, key: str) -> str:
        tokens = _split_tokens(data)
        rows = PoemKeyValidator.validate(key, self.width)

        result = []
        for token in tokens:
            if token == SPACE_TOKEN:
                result.append(" ")
                continue
            match = _POSITION_RE.match(token)
            if not match:
                raise ValueError(f"Некоректний елемент шифрограми: '{token}'. Очікується формат 'рядок/стовпчик'.")
            r, c = int(match.group(1)), int(match.group(2))
            if not 1 <= r <= len(rows):
                raise ValueError(f"Рядка {r} немає у вірші (рядків: {len(rows)}).")
            if not 1 <= c <= len(rows[r - 1]):
                raise ValueError(f"У рядку {r} немає стовпчика {c} (довжина рядка: {len(rows[r - 1])}).")
            result.append(rows[r - 1][c - 1])
        return "".join(result)


class WordBookCipher(BaseCipher):
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def encrypt(self, data: str, key: str) -> str:
        text = DataValidator.validate_text(data)
        words = BookTextValidator.validate(key)

        index: dict[str, list[int]] = {}
        for n, word in enumerate(words, start=1):
            index.setdefault(word[0], []).append(n)

        tokens: list[str] = []
        missing: set[str] = set()

        for char in text.lower():
            if char.isspace():
                tokens.append(SPACE_TOKEN)
                continue
            if not is_letter(char):
                continue
            numbers = index.get(char)
            if not numbers:
                missing.add(char)
                continue
            tokens.append(str(self._rng.choice(numbers)))

        if missing:
            raise ValueError(
                "У тексті-ключі немає слів на літери: " + ", ".join(sorted(missing)) + "."
            )
        if not any(t != SPACE_TOKEN for t in tokens):
            raise ValueError("У тексті немає літер для шифрування.")
        return ", ".join(tokens)

    def decrypt(self, data: str, key: str) -> str:
        tokens = _split_tokens(data)
        words = BookTextValidator.validate(key)

        result = []
        for token in tokens:
            if token == SPACE_TOKEN:
                result.append(" ")
                continue
            if not token.isdigit():
                raise ValueError(f"Некоректний елемент шифрограми: '{token}'. Очікується номер слова.")
            n = int(token)
            if not 1 <= n <= len(words):
                raise ValueError(f"Слова №{n} немає в тексті-ключі (слів: {len(words)}).")
            result.append(words[n - 1][0])
        return "".join(result)
