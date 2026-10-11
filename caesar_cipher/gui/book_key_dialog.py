from tkinter import filedialog, messagebox

import customtkinter as ctk

from caesar_cipher.core import FileManager, PoemKeyValidator, BookTextValidator
from caesar_cipher.gui.colors import Colors


class BookKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, *, text: str, width: int, poem_mode: bool, on_apply):
        super().__init__(parent)
        self._poem_mode = poem_mode
        self._on_apply = on_apply

        self.title("Ключ: вірш" if poem_mode else "Ключ: текст книги")
        self.geometry("900x720")
        self.transient(parent)

        label = "Вставте вірш (кожен рядок вірша — окремий рядок таблиці):" if poem_mode \
            else "Вставте текст книги/уривок (номери слів рахуються з 1):"
        ctk.CTkLabel(self, text=label, anchor="w").pack(fill="x", padx=12, pady=(10, 2))

        self.textbox = ctk.CTkTextbox(self, height=220, wrap="word", font=("Arial", 14))
        self.textbox.pack(fill="x", padx=12, pady=4)
        self.textbox.insert("1.0", text)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=4)

        if poem_mode:
            ctk.CTkLabel(bar, text="Ширина таблиці:").pack(side="left")
            self.width_entry = ctk.CTkEntry(bar, width=60)
            self.width_entry.insert(0, str(width))
            self.width_entry.pack(side="left", padx=6)
            ctk.CTkButton(bar, text="Показати таблицю", width=160, command=self._refresh_preview).pack(
                side="left", padx=6)

        ctk.CTkButton(bar, text="З файлу…", width=100, command=self._load_file).pack(side="left", padx=6)
        ctk.CTkButton(
            bar, text="Застосувати", width=130, command=self._apply,
            fg_color=Colors.SUCCESS, hover_color=Colors.SUCCESS_HOVER,
        ).pack(side="right", padx=6)

        if poem_mode:
            self.preview = ctk.CTkTextbox(self, wrap="none", font=("Courier New", 14))
            self.preview.pack(fill="both", expand=True, padx=12, pady=(4, 12))
            self._refresh_preview()

        self.after(150, self._grab)

    def _grab(self):
        try:
            self.lift()
            self.grab_set()
        except Exception:
            pass

    def _text(self) -> str:
        return self.textbox.get("1.0", "end-1c")

    def _load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")])
        if not path:
            return
        try:
            content = FileManager.read_file(path)
        except (OSError, UnicodeDecodeError) as err:
            messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{err}", parent=self)
            return
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)
        if self._poem_mode:
            self._refresh_preview()

    def _refresh_preview(self):
        try:
            rows = PoemKeyValidator.validate(self._text(), self.width_entry.get())
            cols = max(len(r) for r in rows)
            lines = ["    " + " ".join(f"{i:>2}" for i in range(1, cols + 1))]
            for n, row in enumerate(rows, start=1):
                lines.append(f"{n:>3} " + " ".join(f"{ch.upper():>2}" for ch in row))
            content = "\n".join(lines)
        except (ValueError, TypeError) as err:
            content = str(err)
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", content)
        self.preview.configure(state="disabled")

    def _apply(self):
        text = self._text()
        try:
            if self._poem_mode:
                width = PoemKeyValidator.validate_width(self.width_entry.get())
                PoemKeyValidator.validate(text, width)
            else:
                width = 10
                BookTextValidator.validate(text)
        except (ValueError, TypeError) as err:
            messagebox.showerror("Помилка", str(err), parent=self)
            return
        self._on_apply(text, width)
        self.destroy()
