from cipher_labs.core.alphabets import find_alphabet
from cipher_labs.core.base import BaseCipher
from cipher_labs.core.common_validators import DataValidator
from .validators import KeyValidator


class TextCaesarCipher(BaseCipher):
    @staticmethod
    def _shift_char(char: str, alphabet: str, shift: int) -> str:
        n = len(alphabet)
        current_idx = alphabet.index(char)
        new_idx = (current_idx + shift) % n
        return alphabet[new_idx]

    def _transform(self, text: str, shift: int) -> str:
        result = []

        for char in text:
            alphabet = find_alphabet(char)
            if alphabet is not None:
                result.append(self._shift_char(char, alphabet, shift))
            else:
                result.append(char)

        return "".join(result)

    def encrypt(self, data: str, key) -> str:
        valid_text = DataValidator.validate_text(data)
        valid_key = KeyValidator.validate(key)
        return self._transform(valid_text, valid_key)

    def decrypt(self, data: str, key) -> str:
        valid_text = DataValidator.validate_text(data)
        valid_key = KeyValidator.validate(key)
        return self._transform(valid_text, -valid_key)


class UniversalByteCaesarCipher(BaseCipher):
    @staticmethod
    def _build_table(shift: int) -> bytes:
        shift %= 256
        return bytes((i + shift) % 256 for i in range(256))

    def _transform(self, data: bytes, shift: int) -> bytes:
        table = self._build_table(shift)
        return data.translate(table)

    def encrypt(self, data: bytes, key) -> bytes:
        valid_data = DataValidator.validate_bytes(data)
        valid_key = KeyValidator.validate(key)
        return self._transform(valid_data, valid_key)

    def decrypt(self, data: bytes, key) -> bytes:
        valid_data = DataValidator.validate_bytes(data)
        valid_key = KeyValidator.validate(key)
        return self._transform(valid_data, -valid_key)
