from collections import Counter

from cipher_labs.core.alphabets import ALPHABETS, find_alphabet
from cipher_labs.core.common_validators import DataValidator


class TrithemiusAttack:
    @staticmethod
    def _collect_shifts(plaintext: str, ciphertext: str) -> list[tuple[int, int, int]]:
        entries = []
        p = 0
        for p_char, c_char in zip(plaintext, ciphertext):
            alpha_p = find_alphabet(p_char)
            if alpha_p is not None:
                alpha_c = find_alphabet(c_char)
                if alpha_c is not None and len(alpha_c) == len(alpha_p):
                    n = len(alpha_p)
                    x = alpha_p.index(p_char)
                    y = alpha_c.index(c_char)
                    entries.append((p, (y - x + n) % n, n))
                p += 1
        return entries

    @staticmethod
    def _dominant_group(entries: list[tuple[int, int, int]]) -> tuple[int, list[tuple[int, int]]]:
        counts = Counter(n for _, _, n in entries)
        dominant_n = counts.most_common(1)[0][0]
        return dominant_n, [(p, k) for p, k, n in entries if n == dominant_n]

    @staticmethod
    def _find_linear(pairs: list[tuple[int, int]], n: int):
        if len(pairs) < 2:
            return None
        p0, k0 = pairs[0]
        for a in range(n):
            b = (k0 - a * p0) % n
            if all((a * p + b) % n == k for p, k in pairs):
                return a, b
        return None

    @staticmethod
    def _find_quadratic(pairs: list[tuple[int, int]], n: int):
        if len(pairs) < 3:
            return None
        p0, k0 = pairs[0]
        for a in range(n):
            for b in range(n):
                c = (k0 - a * p0 * p0 - b * p0) % n
                if all((a * p * p + b * p + c) % n == k for p, k in pairs):
                    return a, b, c
        return None

    @staticmethod
    def _find_repeating_passphrase(pairs: list[tuple[int, int]], n: int):
        shifts = [k for _, k in pairs]
        max_len = len(shifts)
        display_alphabet = next(a for a in ALPHABETS if len(a) == n)
        for length in range(1, max_len):
            pattern = shifts[:length]
            if all(shifts[i] == pattern[i % length] for i in range(max_len)):
                return "".join(display_alphabet[k] for k in pattern)
        return None

    @classmethod
    def analyze(cls, plaintext: str, ciphertext: str) -> dict:
        plaintext = DataValidator.validate_text(plaintext)
        ciphertext = DataValidator.validate_text(ciphertext)
        if len(plaintext) != len(ciphertext):
            raise ValueError("Довжина відкритого та шифрованого текстів повинна співпадати.")

        entries = cls._collect_shifts(plaintext, ciphertext)
        if not entries:
            raise ValueError("Не знайдено жодного дійсного символу для аналізу.")

        n, pairs = cls._dominant_group(entries)

        results = {
            "linear": cls._find_linear(pairs, n),
            "quadratic": cls._find_quadratic(pairs, n),
            "passphrase": None,
        }
        if results["linear"] is None and results["quadratic"] is None:
            results["passphrase"] = cls._find_repeating_passphrase(pairs, n)

        return results
