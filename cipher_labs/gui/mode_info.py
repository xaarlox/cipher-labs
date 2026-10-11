CAESAR = "Цезар"
BOOK_POEM = "Книжковий (Вірш)"
BOOK_WORDS = "Книжковий (Слова)"
BOOK_MODES = (BOOK_POEM, BOOK_WORDS)

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
