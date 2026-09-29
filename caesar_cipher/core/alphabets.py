UKR_LOWER = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
UKR_UPPER = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
ENG_LOWER = "abcdefghijklmnopqrstuvwxyz"
ENG_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ALPHABETS = (UKR_LOWER, UKR_UPPER, ENG_LOWER, ENG_UPPER)


def find_alphabet(char: str) -> str | None:
    for alphabet in ALPHABETS:
        if char in alphabet:
            return alphabet
    return None
