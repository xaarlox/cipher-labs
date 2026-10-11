import customtkinter as ctk

from .colors import Colors


def _button(parent, text, cmd, width=100, **kw):
    b = ctk.CTkButton(parent, text=text, width=width, command=cmd, **kw)
    b.pack(side="left", padx=4, pady=6)
    return b


def build_file_toolbar(parent, *, on_new, on_open, on_save, on_print, on_exit, on_about):
    bar = ctk.CTkFrame(parent)

    _button(bar, "Створити", on_new)
    _button(bar, "Відкрити", on_open)
    _button(bar, "Зберегти", on_save)
    _button(bar, "Друк", on_print)

    ctk.CTkButton(
        bar, text="Вихід", width=90, command=on_exit, fg_color=Colors.DANGER, hover_color=Colors.DANGER_HOVER,
    ).pack(side="right", padx=4)

    ctk.CTkButton(
        bar, text="Про розробника", width=130, command=on_about, fg_color=Colors.NEUTRAL,
        hover_color=Colors.NEUTRAL_HOVER,
    ).pack(side="right", padx=4)

    return bar


def build_crypto_bar(parent, *, on_encrypt, on_decrypt, on_attack, on_book_key):
    bar = ctk.CTkFrame(parent)

    key_label = ctk.CTkLabel(bar, text="Ключ:")
    key_label.pack(side="left", padx=(8, 2))

    key_holder = ctk.CTkFrame(bar, fg_color="transparent")
    key_holder.pack(side="left")

    key_entry = ctk.CTkEntry(key_holder, width=140, placeholder_text="Введіть ключ")
    key_entry.pack(side="left", padx=4, pady=6)

    book_btn = ctk.CTkButton(
        key_holder, text="Вибрати вірш...", width=210, command=on_book_key,
        fg_color=Colors.PURPLE, hover_color=Colors.PURPLE_HOVER,
    )

    _button(
        bar, "Зашифрувати", on_encrypt, width=130,
        fg_color=Colors.SUCCESS, hover_color=Colors.SUCCESS_HOVER,
    )
    _button(
        bar, "Розшифрувати", on_decrypt, width=140,
        fg_color=Colors.WARNING, hover_color=Colors.WARNING_HOVER,
    )

    attack_btn = ctk.CTkButton(
        bar, text="Атака (Аналіз)", width=130, command=on_attack,
        fg_color=Colors.DANGER, hover_color=Colors.DANGER_HOVER,
    )
    attack_btn.pack(side="right", padx=4, pady=6)

    return bar, key_label, key_entry, attack_btn, book_btn


def build_binary_tools_bar(parent, *, on_encrypt_file, on_decrypt_file):
    bar = ctk.CTkFrame(parent)

    ctk.CTkLabel(
        bar, text="Файл будь-якого формату (jpg, pdf, docx тощо):",
    ).pack(side="left", padx=(8, 2))

    encrypt_btn = _button(
        bar, "Зашифрувати файл", on_encrypt_file, width=160,
        fg_color=Colors.TEAL, hover_color=Colors.TEAL_HOVER,
    )
    decrypt_btn = _button(
        bar, "Розшифрувати файл", on_decrypt_file, width=170,
        fg_color=Colors.PURPLE, hover_color=Colors.PURPLE_HOVER,
    )

    return bar, encrypt_btn, decrypt_btn
