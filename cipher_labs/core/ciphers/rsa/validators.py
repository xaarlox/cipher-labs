import math
import re

from .numtheory import is_probable_prime

MIN_KEY_BITS = 16
MAX_KEY_BITS = 4096
DEFAULT_KEY_BITS = 1024
DEFAULT_PUBLIC_EXPONENT = 65537

_SPLIT_RE = re.compile(r"[,;\s()]+")


class RSAKeyValidator:
    @staticmethod
    def to_int(value, name: str) -> int:
        if isinstance(value, bool):
            raise ValueError(f"{name}: очікується ціле число.")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            text = value.strip().replace(" ", "")
            try:
                return int(text)
            except ValueError:
                raise ValueError(f"{name}: '{value}' не є цілим числом.") from None
        raise ValueError(f"{name}: очікується ціле число.")

    @classmethod
    def validate_bits(cls, bits) -> int:
        bits = cls.to_int(bits, "Розмір ключа")
        if not MIN_KEY_BITS <= bits <= MAX_KEY_BITS:
            raise ValueError(f"Розмір ключа має бути від {MIN_KEY_BITS} до {MAX_KEY_BITS} біт.")
        return bits

    @classmethod
    def validate_exponent(cls, e) -> int:
        e = cls.to_int(e, "Відкрита експонента e")
        if e < 3 or e % 2 == 0:
            raise ValueError("Відкрита експонента e має бути непарним числом, не меншим за 3.")
        return e

    @classmethod
    def validate_components(cls, p, q, e) -> tuple[int, int, int, int]:
        """Перевіряє p, q, e і повертає (p, q, e, φ(n))"""
        p = cls.to_int(p, "p")
        q = cls.to_int(q, "q")
        e = cls.to_int(e, "e")
        if not is_probable_prime(p):
            raise ValueError(f"p = {p} не є простим числом.")
        if not is_probable_prime(q):
            raise ValueError(f"q = {q} не є простим числом.")
        if p == q:
            raise ValueError("Числа p і q мають бути різними.")
        phi = (p - 1) * (q - 1)
        if not 1 < e < phi:
            raise ValueError(f"Має виконуватися 1 < e < φ(n) = {phi}.")
        if math.gcd(e, phi) != 1:
            raise ValueError(f"e = {e} не взаємно просте з φ(n) = {phi} (НСД = {math.gcd(e, phi)}).")
        return p, q, e, phi

    @classmethod
    def parse_pair(cls, text, first_name: str) -> tuple[int, int]:
        """Розбирає запис ключа '(x, n)' / 'x, n' / 'x n'"""
        if not isinstance(text, str):
            raise TypeError("Ключ має бути рядком.")
        parts = [p for p in _SPLIT_RE.split(text.strip()) if p]
        if len(parts) != 2:
            raise ValueError(f"Ключ має містити два числа: {first_name}, n.")
        x = cls.to_int(parts[0], first_name)
        n = cls.to_int(parts[1], "n")
        if n < 6:
            raise ValueError("Модуль n має бути більшим за 5.")
        if not 1 < x < n:
            raise ValueError(f"Має виконуватися 1 < {first_name} < n.")
        return x, n

    @staticmethod
    def validate_key(key, need_private: bool):
        from .keys import RSAKey  # Уникнення циклічного імпорту

        if key is None:
            raise ValueError("Ключі RSA не задано. Сформуйте їх кнопкою «Ключі RSA...».")
        if not isinstance(key, RSAKey):
            raise TypeError("Очікувався ключ RSA (RSAKey).")
        if need_private and key.d is None:
            raise ValueError(
                "Для розшифрування потрібен закритий ключ (d, n). "
                "Задано лише відкритий ключ."
            )
        return key


class RSADataValidator:
    @staticmethod
    def parse_numbers(text, n: int, name: str = "Число") -> list[int]:
        if not isinstance(text, str):
            raise TypeError(f"Очікувався рядок, отримано {type(text).__name__}.")
        parts = [p for p in _SPLIT_RE.split(text.strip()) if p]
        if not parts:
            raise ValueError("Немає чисел для обробки.")
        numbers = []
        for part in parts:
            if not part.isdigit():
                raise ValueError(f"'{part}' не є невід'ємним цілим числом.")
            value = int(part)
            if value >= n:
                raise ValueError(f"{name} {value} має бути меншим за модуль n = {n}.")
            numbers.append(value)
        return numbers
