from cipher_labs.core.base import BaseCipher
from cipher_labs.core.common_validators import DataValidator
from .keys import RSAKey
from .validators import RSADataValidator, RSAKeyValidator

RSA_MODES = ("text", "numbers")


class RSACipher(BaseCipher):
    """Шифрування RSA: c = m^e mod n, розшифрування: m = c^d mod n

    Режим 'numbers' шифрує окремі числа m < n (для перевірки на числовому прикладі),
    режим 'text' – текст: байти UTF-8 розбиваються на блоки по k байт, де 256^k ≤ n,
    кожен блок шифрується як число. Шифрограма – числа через кому
    """

    def __init__(self, mode: str = "text"):
        if mode not in RSA_MODES:
            raise ValueError(f"Недопустимий режим '{mode}'. Оберіть з {RSA_MODES}.")
        self.mode = mode

    @staticmethod
    def encrypt_int(m: int, key: RSAKey) -> int:
        return pow(m, key.e, key.n)

    @staticmethod
    def decrypt_int(c: int, key: RSAKey) -> int:
        return pow(c, key.d, key.n)

    @staticmethod
    def block_size(n: int) -> int:
        """Найбільша кількість байт k, для якої будь-який блок менший за n"""
        return (n.bit_length() - 1) // 8

    def encrypt(self, data: str, key) -> str:
        key = RSAKeyValidator.validate_key(key, need_private=False)
        text = DataValidator.validate_text(data)

        if self.mode == "numbers":
            numbers = RSADataValidator.parse_numbers(text, key.n, "Число m")
            return ", ".join(str(self.encrypt_int(m, key)) for m in numbers)

        if "\x00" in text:
            raise ValueError("Текст не може містити нульовий символ.")
        k = self.block_size(key.n)
        if k < 1:
            raise ValueError(
                f"Модуль n = {key.n} замалий для шифрування тексту (потрібно n ≥ 256). "
                "Використайте режим «Числа» або більший ключ."
            )
        raw = text.encode("utf-8")
        blocks = (raw[i:i + k] for i in range(0, len(raw), k))
        return ", ".join(str(self.encrypt_int(int.from_bytes(b, "big"), key)) for b in blocks)

    def decrypt(self, data: str, key) -> str:
        key = RSAKeyValidator.validate_key(key, need_private=True)
        text = DataValidator.validate_text(data)
        numbers = RSADataValidator.parse_numbers(text, key.n, "Шифроблок c")

        if self.mode == "numbers":
            return ", ".join(str(self.decrypt_int(c, key)) for c in numbers)

        k = self.block_size(key.n)
        if k < 1:
            raise ValueError(f"Модуль n = {key.n} замалий для тексту. Використайте режим «Числа».")
        wrong_key = ValueError("Не вдалося розшифрувати: хибний ключ або пошкоджена шифрограма.")

        chunks = []
        for i, c in enumerate(numbers):
            m = self.decrypt_int(c, key)
            # Усі блоки, крім останнього, мають рівно k байт; останній – свою довжину
            length = k if i < len(numbers) - 1 else max(1, (m.bit_length() + 7) // 8)
            try:
                chunk = m.to_bytes(length, "big")
            except OverflowError:
                raise wrong_key from None
            if len(chunk) > k:
                raise wrong_key
            chunks.append(chunk)

        try:
            return b"".join(chunks).decode("utf-8")
        except UnicodeDecodeError:
            raise wrong_key from None
