import customtkinter as ctk

from caesar_cipher.gui.colors import Colors

TRITHEMIUS_MODES = ["Лінійний", "Нелінійний", "Гасло"]


class CipherSelector:
    def __init__(self, parent, *, on_change):
        self._on_change = on_change

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")

        self._type = ctk.CTkSegmentedButton(
            self.frame,
            values=["Цезар", "Тритеміус"],
            command=self._on_type_change,
            selected_color=Colors.TEAL,
            selected_hover_color=Colors.TEAL_HOVER,
            unselected_color=Colors.NEUTRAL,
            unselected_hover_color=Colors.NEUTRAL_HOVER,
            font=("Arial", 14, "bold")
        )
        self._type.set("Цезар")
        self._type.pack(pady=(4, 0))

        self._trithemius_mode = ctk.CTkSegmentedButton(
            self.frame,
            values=TRITHEMIUS_MODES,
            command=lambda _v: self._notify(),
            selected_color=Colors.PURPLE,
            selected_hover_color=Colors.PURPLE_HOVER,
            unselected_color=Colors.NEUTRAL,
            unselected_hover_color=Colors.NEUTRAL_HOVER,
            font=("Arial", 13)
        )
        self._trithemius_mode.set(TRITHEMIUS_MODES[0])

    def pack(self, **kw):
        self.frame.pack(**kw)

    @property
    def choice(self) -> str:
        if self._type.get() == "Цезар":
            return "Цезар"
        return f"Тритеміус ({self._trithemius_mode.get()})"

    def _on_type_change(self, value: str) -> None:
        if value == "Тритеміус":
            self._trithemius_mode.pack(pady=(6, 4))
        else:
            self._trithemius_mode.pack_forget()
        self._notify()

    def _notify(self) -> None:
        self._on_change(self.choice)
