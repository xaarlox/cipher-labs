from cipher_labs.core import SYMMETRIC_ALGORITHMS, SYMMETRIC_MODES

CAESAR = "Цезар"
BOOK_POEM = "Книжковий (Вірш)"
BOOK_WORDS = "Книжковий (Слова)"
BOOK_MODES = (BOOK_POEM, BOOK_WORDS)
RSA_MODES = {"RSA (Текст)": "text", "RSA (Числа)": "numbers"}

_CAESAR_ABOUT = (
    "Лабораторна робота №1. Шифр Цезаря\n\n"
    "Курс: 4\n"
    "Група: ТВ-33\n"
    "ПІБ: Федоренко Валерія Андріївна\n"
    "GitHub: xaarlox\n"
    "Версія: 1.0"
)

_TRITHEMIUS_ABOUT = (
    "Лабораторна робота №2. Шифр Тритеміуса\n\n"
    "Курс: 4\n"
    "Група: ТВ-33\n"
    "ПІБ: Федоренко Валерія Андріївна\n"
    "GitHub: xaarlox\n"
    "Версія: 2.0"
)

_BOOK_ABOUT = (
    "Лабораторна робота №3. Книжковий шифр\n\n"
    "Курс: 4\n"
    "Група: ТВ-33\n"
    "ПІБ: Федоренко Валерія Андріївна\n"
    "GitHub: xaarlox\n"
    "Версія: 3.0"
)

MODE_INFO = {
    CAESAR: {
        "title_suffix": "Шифр Цезаря",
        "supports_binary_files": True,
        "about": _CAESAR_ABOUT,
    },
    "Тритеміус (Лінійний)": {
        "title_suffix": "Шифр Тритеміуса",
        "supports_binary_files": False,
        "about": _TRITHEMIUS_ABOUT,
    },
    BOOK_POEM: {
        "title_suffix": "Віршований шифр",
        "supports_binary_files": False,
        "about": _BOOK_ABOUT,
    },
    BOOK_WORDS: {
        "title_suffix": "Книжковий шифр",
        "supports_binary_files": False,
        "about": _BOOK_ABOUT,
    },
}

MODE_INFO["Тритеміус (Нелінійний)"] = MODE_INFO["Тритеміус (Лінійний)"]
MODE_INFO["Тритеміус (Гасло)"] = MODE_INFO["Тритеміус (Лінійний)"]

_SYMMETRIC_ABOUT = (
    "Лабораторна робота №5. Шифри DES/TripleDES/AES\n\n"
    "Курс: 4\n"
    "Група: ТВ-33\n"
    "ПІБ: Федоренко Валерія Андріївна\n"
    "GitHub: xaarlox\n"
    "Версія: 5.0"
)

# (підпис ключа, приклад ключа, приклад IV)
SYMMETRIC_HINTS = {
    "DES": ("Ключ (8 байт):", "ABCDEFGH", "ABCDEFGH"),
    "3DES": ("Ключ (16/24 байти):", "ABCDEFGHIJKLMNOP", "ABCDEFGH"),
    "AES": ("Ключ (16/24/32 байти):", "0123456789ABCDEF", "ABCDEFGHIJKLMNOP"),
}

for _algorithm in SYMMETRIC_ALGORITHMS:
    for _mode in SYMMETRIC_MODES:
        MODE_INFO[f"{_algorithm} ({_mode})"] = {
            "title_suffix": f"{_algorithm}, режим {_mode}",
            "supports_binary_files": True,
            "about": _SYMMETRIC_ABOUT,
        }


def parse_symmetric(choice: str) -> tuple[str, str] | None:
    name, _, rest = choice.partition(" (")
    mode = rest.rstrip(")")
    if name in SYMMETRIC_ALGORITHMS and mode in SYMMETRIC_MODES:
        return name, mode
    return None


_RSA_ABOUT = (
    "Лабораторна робота №7. Шифр RSA\n\n"
    "Курс: 4\n"
    "Група: ТВ-33\n"
    "ПІБ: Федоренко Валерія Андріївна\n"
    "GitHub: xaarlox\n"
    "Версія: 7.0"
)

for _choice in RSA_MODES:
    MODE_INFO[_choice] = {
        "title_suffix": "Шифр RSA",
        "supports_binary_files": False,
        "about": _RSA_ABOUT,
    }
