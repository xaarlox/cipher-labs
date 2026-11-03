import re

from Crypto.Cipher import AES, DES, DES3
from Crypto.Util.Padding import pad, unpad

from cipher_labs.core.base import BaseCipher
from cipher_labs.core.common_validators import DataValidator
from .validators import SymmetricValidator

_BACKENDS = {"DES": DES, "3DES": DES3, "AES": AES}

# Блокові режими вимагають доповнення; потокові (CFB, OFB, CTR) довжину тексту не змінюють
_PADDED_MODES = ("ECB", "CBC")


class SymmetricCipher(BaseCipher):
    """DES/3DES/AES у режимах ECB, CBC, CFB, OFB, CTR

    encrypt/decrypt працюють з текстом (шифротекст - hex-рядок),
    encrypt_bytes/decrypt_bytes - з довільними байтами (файлами)
    """

    def __init__(self, algorithm: str = "AES", mode: str = "CBC", iv=""):
        self.algorithm = SymmetricValidator.validate_algorithm(algorithm)
        self.mode = SymmetricValidator.validate_mode(mode)
        self._iv = iv  # перевіряється під час шифрування, щоб помилку показав GUI

    def _build(self, key):
        backend = _BACKENDS[self.algorithm]
        key_bytes = SymmetricValidator.validate_key(self.algorithm, key)
        iv = SymmetricValidator.validate_iv(self.algorithm, self.mode, self._iv)
        mode_const = getattr(backend, f"MODE_{self.mode}")
        try:
            if self.mode == "ECB":
                return backend.new(key_bytes, mode_const)
            if self.mode == "CTR":
                return backend.new(key_bytes, mode_const, nonce=b"", initial_value=iv)
            return backend.new(key_bytes, mode_const, iv=iv)
        except ValueError as err:
            raise ValueError(f"Недопустимий ключ {self.algorithm}: {err}") from err

    def encrypt_bytes(self, data: bytes, key) -> bytes:
        raw = DataValidator.validate_bytes(data)
        cipher = self._build(key)
        if self.mode in _PADDED_MODES:
            raw = pad(raw, cipher.block_size)
        return cipher.encrypt(raw)

    def decrypt_bytes(self, data: bytes, key) -> bytes:
        raw = DataValidator.validate_bytes(data)
        cipher = self._build(key)
        padded = self.mode in _PADDED_MODES
        if padded and len(raw) % cipher.block_size:
            raise ValueError(
                f"Довжина шифротексту має бути кратною {cipher.block_size} байт "
                f"(отримано {len(raw)})."
            )
        result = cipher.decrypt(raw)
        if padded:
            try:
                result = unpad(result, cipher.block_size)
            except ValueError:
                raise ValueError(
                    "Не вдалося зняти доповнення: хибний ключ, IV чи режим або пошкоджені дані."
                ) from None
        return result

    def encrypt(self, data: str, key) -> str:
        text = DataValidator.validate_text(data)
        return self.encrypt_bytes(text.encode("utf-8"), key).hex().upper()

    def decrypt(self, data: str, key) -> str:
        text = DataValidator.validate_text(data)
        try:
            raw = bytes.fromhex(re.sub(r"[\s-]", "", text))
        except ValueError:
            raise ValueError("Шифрограма має бути шістнадцятковим рядком (цифри 0-9, A-F).") from None
        decrypted = self.decrypt_bytes(raw, key)
        try:
            return decrypted.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "Результат не є коректним UTF-8 текстом: перевірте ключ, IV і режим."
            ) from None
