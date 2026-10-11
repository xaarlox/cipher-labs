import customtkinter as ctk

from caesar_cipher.gui.colors import Colors

TRITHEMIUS_MODES = ["Лінійний", "Нелінійний", "Гасло"]
BOOK_MODES = ["Вірш", "Слова"]


class CipherSelector:
    def __init__(self, parent, *, on_change):
        self._on_change = on_change

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")

        self._type = ctk.CTkSegmentedButton(
            self.frame,
            values=["Цезар", "Тритеміус", "Книжковий"],
            command=self._on_type_change,
            selected_color=Colors.TEAL,
            selected_hover_color=Colors.TEAL_HOVER,
            unselected_color=Colors.NEUTRAL,
            unselected_hover_color=Colors.NEUTRAL_HOVER,
            font=("Arial", 14, "bold")
        )
        self._type.set("Цезар")
        self._type.pack(pady=(4, 0))

        self._trithemius_mode = self._make_sub_selector(TRITHEMIUS_MODES)
        self._book_mode = self._make_sub_selector(BOOK_MODES)

    def _make_sub_selector(self, values):
        button = ctk.CTkSegmentedButton(
            self.frame,
            values=values,
            command=lambda _v: self._notify(),
            selected_color=Colors.PURPLE,
            selected_hover_color=Colors.PURPLE_HOVER,
            unselected_color=Colors.NEUTRAL,
            unselected_hover_color=Colors.NEUTRAL_HOVER,
            font=("Arial", 13)
        )
        button.set(values[0])
        return button

    def pack(self, **kw):
        self.frame.pack(**kw)

    @property
    def choice(self) -> str:
        kind = self._type.get()
        if kind == "Тритеміус":
            return f"Тритеміус ({self._trithemius_mode.get()})"
        if kind == "Книжковий":
            return f"Книжковий ({self._book_mode.get()})"
        return "Цезар"

    def _on_type_change(self, value: str) -> None:
        self._trithemius_mode.pack_forget()
        self._book_mode.pack_forget()
        if value == "Тритеміус":
            self._trithemius_mode.pack(pady=(6, 4))
        elif value == "Книжковий":
            self._book_mode.pack(pady=(6, 4))
        self._notify()

    def _notify(self) -> None:
        self._on_change(self.choice)
