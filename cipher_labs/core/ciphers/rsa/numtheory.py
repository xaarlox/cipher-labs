import math
import secrets


def _sieve(limit: int) -> tuple[int, ...]:
    flags = bytearray([1]) * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(limit) + 1):
        if flags[i]:
            flags[i * i::i] = bytearray(len(flags[i * i::i]))
    return tuple(i for i, is_prime in enumerate(flags) if is_prime)


SMALL_PRIMES = _sieve(2000)

# Для n < 3.3 * 10^24 перевірка Міллера–Рабіна за цими основами є точною
_DETERMINISTIC_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
_DETERMINISTIC_LIMIT = 3_317_044_064_679_887_385_961_981


def _miller_rabin_round(n: int, d: int, s: int, a: int) -> bool:
    x = pow(a, d, n)
    if x in (1, n - 1):
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False


def is_probable_prime(n: int, rounds: int = 40) -> bool:
    """Тест Міллера–Рабіна: точний для n < 3.3*10^24, імовірнісний (помилка < 4^-rounds) для більших"""
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False

    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    if n < _DETERMINISTIC_LIMIT:
        bases = _DETERMINISTIC_BASES
    else:
        bases = tuple(secrets.randbelow(n - 3) + 2 for _ in range(rounds))
    return all(_miller_rabin_round(n, d, s, a) for a in bases)


def generate_prime(bits: int) -> int:
    """Випадкове просте число рівно з `bits` бітами"""
    if bits < 4:
        raise ValueError("Розмір простого числа має бути щонайменше 4 біти.")
    while True:
        candidate = secrets.randbits(bits) | (0b11 << (bits - 2)) | 1
        if is_probable_prime(candidate):
            return candidate


def mod_inverse(a: int, m: int) -> int:
    """Обернене за модулем (розширений алгоритм Евкліда)"""
    old_r, r = a % m, m
    old_s, s = 1, 0
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:
        raise ValueError(f"Число {a} не має оберненого за модулем {m} (НСД = {old_r}).")
    return old_s % m
