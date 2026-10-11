from cipher_labs.core.alphabets import find_alphabet
from cipher_labs.core.base import BaseCipher
from cipher_labs.core.common_validators import DataValidator
from .validators import TrithemiusKeyValidator


class TextTrithemiusCipher(BaseCipher):
    def __init__(self, mode: str):
        valid_modes = ('linear', 'quadratic', 'passphrase')
        if mode not in valid_modes:
            raise ValueError(f"Недопустимий режим {mode}. Оберіть з {valid_modes}.")
        self.mode = mode

    def _get_shift(self, p: int, valid_key) -> int:
        if self.mode == 'linear':
            A, B = valid_key
            return A * p + B
        elif self.mode == 'quadratic':
            A, B, C = valid_key
            return A * (p ** 2) + B * p + C
        elif self.mode == 'passphrase':
            char = valid_key[p % len(valid_key)]
            alphabet = find_alphabet(char)
            if alphabet:
                return alphabet.index(char)
            return 0

    def _transform(self, text: str, valid_key, encrypt: bool) -> str:
        result = []
        p = 0

        for char in text:
            alphabet = find_alphabet(char)

            if alphabet is not None:
                n = len(alphabet)
                k = self._get_shift(p, valid_key)
                x = alphabet.index(char)

                if encrypt:
                    y = (x + k) % n
                else:
                    y = (x - (k % n) + n) % n

                result.append(alphabet[y])
                p += 1
            else:
                result.append(char)

        return "".join(result)

    def _validate_key_for_mode(self, key):
        if self.mode == 'linear':
            return TrithemiusKeyValidator.validate_linear(key)
        elif self.mode == 'quadratic':
            return TrithemiusKeyValidator.validate_quadratic(key)
        elif self.mode == 'passphrase':
            return TrithemiusKeyValidator.validate_passphrase(key)

    def encrypt(self, data: str, key) -> str:
        valid_text = DataValidator.validate_text(data)
        valid_key = self._validate_key_for_mode(key)
        return self._transform(valid_text, valid_key, encrypt=True)

    def decrypt(self, data: str, key) -> str:
        valid_text = DataValidator.validate_text(data)
        valid_key = self._validate_key_for_mode(key)
        return self._transform(valid_text, valid_key, encrypt=False)
