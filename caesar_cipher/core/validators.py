import re

from caesar_cipher.core.alphabets import find_alphabet


class KeyValidator:
    @staticmethod
    def validate(key) -> int:
        if isinstance(key, bool):
            raise ValueError("Ключ не може бути логічним значенням (True/False).")
        try:
            return int(key)
        except (TypeError, ValueError):
            raise ValueError(f"Некоректний ключ '{key}'. Ключ має бути цілим числом.")


class TrithemiusKeyValidator:
    @staticmethod
    def _to_int(value) -> int:
        if isinstance(value, bool):
            raise ValueError(f"'{value}' не є цілим числом.")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                raise ValueError(f"'{value}' не є цілим числом.") from None
        raise ValueError(f"'{value}' не є цілим числом.")

    @classmethod
    def _parse_vector(cls, key, size: int, hint: str) -> tuple[int, ...]:
        if isinstance(key, str):
            parts = [p for p in re.split(r"[,;\s]+", key.strip()) if p]
        elif isinstance(key, (list, tuple)):
            parts = list(key)
        else:
            raise TypeError("Ключ має бути рядком або послідовністю цілих чисел.")

        if len(parts) != size:
            raise ValueError(
                f"Ключ має містити рівно {size} цілих числа ({hint}), отримано: {len(parts)}."
            )
        return tuple(cls._to_int(p) for p in parts)

    @classmethod
    def validate_linear(cls, key) -> tuple[int, int]:
        return cls._parse_vector(key, 2, "A, B")

    @classmethod
    def validate_quadratic(cls, key) -> tuple[int, int, int]:
        return cls._parse_vector(key, 3, "A, B, C")

    @staticmethod
    def validate_passphrase(key) -> str:
        if not isinstance(key, str):
            raise TypeError("Гасло має бути рядком.")

        passphrase = key.strip()
        if not passphrase:
            raise ValueError("Гасло не може бути порожнім.")

        invalid = sorted({c for c in passphrase if find_alphabet(c) is None})
        if invalid:
            raise ValueError(
                "Гасло може містити лише літери українського або англійського алфавіту. "
                "Недопустимі символи: " + ", ".join(repr(c) for c in invalid) + "."
            )
        return passphrase


class DataValidator:
    @staticmethod
    def validate_text(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(f"Очікувався рядок, отримано {type(text).__name__}.")
        if len(text) == 0:
            raise ValueError("Текст для обробки не може бути порожнім.")
        return text

    @staticmethod
    def validate_bytes(data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"Очікувались байти, отримано {type(data).__name__}.")
        if len(data) == 0:
            raise ValueError("Дані для обробки не можуть бути порожніми.")
        return bytes(data)
