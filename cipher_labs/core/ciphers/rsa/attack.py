import math
import secrets
import time
from dataclasses import dataclass

from .keys import RSAKey, build_key
from .numtheory import SMALL_PRIMES, is_probable_prime

DEFAULT_TIMEOUT = 30.0


@dataclass(frozen=True)
class RSAAttackResult:
    key: RSAKey  # Відновлена пара ключів (з p, q, d)
    elapsed: float  # Час факторизації, с

    @property
    def p(self) -> int:
        return self.key.p

    @property
    def q(self) -> int:
        return self.key.q


class RSAAttack:
    """Атака на RSA факторизацією модуля n: знаючи p і q, обчислюємо φ(n) і d = e^-1 mod φ(n)"""

    @staticmethod
    def _trial_division(n: int) -> int | None:
        for p in SMALL_PRIMES:
            if p * p > n:
                return None
            if n % p == 0:
                return p
        return None

    @staticmethod
    def _pollard_brent(n: int, deadline: float) -> int:
        """Ро-метод Полларда (варіант Брента). Повертає нетривіальний дільник n"""
        while True:
            y, c, m = secrets.randbelow(n - 1) + 1, secrets.randbelow(n - 1) + 1, 128
            g, r, q = 1, 1, 1
            x = ys = y
            while g == 1:
                if time.perf_counter() > deadline:
                    raise TimeoutError
                x = y
                for _ in range(r):
                    y = (y * y + c) % n
                k = 0
                while k < r and g == 1:
                    ys = y
                    for _ in range(min(m, r - k)):
                        y = (y * y + c) % n
                        q = q * abs(x - y) % n
                    g = math.gcd(q, n)
                    k += m
                r *= 2
            if g == n:
                g = 1
                while g == 1:
                    ys = (ys * ys + c) % n
                    g = math.gcd(abs(x - ys), n)
            if g != n:
                return g

    @classmethod
    def factorize(cls, n: int, timeout: float = DEFAULT_TIMEOUT) -> tuple[int, int]:
        """Розкладає n = p*q на два множники. TimeoutError, якщо не встигли"""
        if n < 4:
            raise ValueError("Модуль n має бути не меншим за 4.")
        if is_probable_prime(n):
            raise ValueError(f"n = {n} є простим числом – це не модуль RSA.")
        small = cls._trial_division(n)
        if small is not None:
            p = small
        else:
            p = cls._pollard_brent(n, time.perf_counter() + timeout)
        q = n // p
        return min(p, q), max(p, q)

    @classmethod
    def recover_private_key(cls, public_key: RSAKey, timeout: float = DEFAULT_TIMEOUT) -> RSAAttackResult:
        if not isinstance(public_key, RSAKey):
            raise TypeError("Очікувався відкритий ключ RSA (RSAKey).")
        start = time.perf_counter()
        try:
            p, q = cls.factorize(public_key.n, timeout)
        except TimeoutError:
            raise ValueError(
                f"Не вдалося розкласти n ({public_key.bits} біт) за {timeout:g} с. "
                "Для такого розміру модуля атака факторизацією непрактична."
            ) from None
        elapsed = time.perf_counter() - start
        if not (is_probable_prime(p) and is_probable_prime(q)):
            raise ValueError(f"n = {p} * {q} не є добутком двох простих чисел.")
        key = build_key(p, q, public_key.e)
        return RSAAttackResult(key=key, elapsed=elapsed)
