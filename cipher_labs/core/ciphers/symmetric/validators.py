import re

SYMMETRIC_ALGORITHMS = ("DES", "3DES", "AES")
SYMMETRIC_MODES = ("ECB", "CBC", "CFB", "OFB", "CTR")
HEX_PREFIX = "hex:"

# block - розмір блоку (байт), keys - допустимі довжини ключа (байт)
_SPECS = {
    "DES": {"block": 8, "keys": (8,)},
    "3DES": {"block": 8, "keys": (16, 24)},
    "AES": {"block": 16, "keys": (16, 24, 32)},
}


class SymmetricValidator:
    @staticmethod
    def validate_algorithm(algorithm) -> str:
        if algorithm not in SYMMETRIC_ALGORITHMS:
            raise ValueError(f"Недопустимий алгоритм '{algorithm}'. Оберіть з {SYMMETRIC_ALGORITHMS}.")
        return algorithm

    @staticmethod
    def validate_mode(mode) -> str:
        if mode not in SYMMETRIC_MODES:
            raise ValueError(f"Недопустимий режим '{mode}'. Оберіть з {SYMMETRIC_MODES}.")
        return mode

    @staticmethod
    def block_size(algorithm: str) -> int:
        return _SPECS[algorithm]["block"]

    @staticmethod
    def key_sizes(algorithm: str) -> tuple[int, ...]:
        return _SPECS[algorithm]["keys"]

    @staticmethod
    def parse_bytes(value, label: str) -> bytes:
        if isinstance(value, (bytes, bytearray)):
            return bytes(value)
        if not isinstance(value, str):
            raise TypeError(f"{label} має бути рядком або байтами.")
        if value.lower().startswith(HEX_PREFIX):
            digits = re.sub(r"[\s-]", "", value[len(HEX_PREFIX):])
            try:
                return bytes.fromhex(digits)
            except ValueError:
                raise ValueError(
                    f"{label}: після '{HEX_PREFIX}' очікується шістнадцятковий запис "
                    f"(парна кількість цифр 0-9, A-F)."
                ) from None
        return value.encode("utf-8")

    @classmethod
    def validate_key(cls, algorithm: str, key) -> bytes:
        key_bytes = cls.parse_bytes(key, "Ключ")
        sizes = cls.key_sizes(algorithm)
        if len(key_bytes) not in sizes:
            allowed = ", ".join(str(s) for s in sizes)
            raise ValueError(
                f"Ключ {algorithm} має містити {allowed} байт, отримано: {len(key_bytes)}. "
                f"Для довільних байтів використовуйте запис '{HEX_PREFIX}...'."
            )
        return key_bytes

    @classmethod
    def validate_iv(cls, algorithm: str, mode: str, iv) -> bytes | None:
        if mode == "ECB":
            return None
        label = "Початкове значення лічильника (IV)" if mode == "CTR" else "Вектор ініціалізації (IV)"
        iv_bytes = cls.parse_bytes(iv, label)
        block = cls.block_size(algorithm)
        if len(iv_bytes) != block:
            raise ValueError(f"{label} для {algorithm} має містити {block} байт, отримано: {len(iv_bytes)}.")
        return iv_bytes
