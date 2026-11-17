from tkinter import filedialog, messagebox

import customtkinter as ctk

from cipher_labs.core import (
    DEFAULT_KEY_BITS,
    DEFAULT_PUBLIC_EXPONENT,
    FileManager,
    RSAKey,
    build_key,
    generate_keypair,
    parse_public_key,
)
from cipher_labs.gui.colors import Colors

XML_FILE_TYPES = [("XML-файли", "*.xml"), ("Усі файли", "*.*")]
WIKI_EXAMPLE = ("61", "53", "17")


class RSAKeyDialog(ctk.CTkToplevel):
    """Діалог формування ключів RSA: генерація пари, ручне задання p, q, e,
    імпорт/експорт відкритого ключа (аналог ToXmlString/FromXmlString з .NET)"""

    def __init__(self, parent, *, key: RSAKey | None, on_apply):
        super().__init__(parent)
        self._key = key
        self._on_apply = on_apply

        self.title("Ключі RSA")
        self.geometry("1700x1100")
        self.transient(parent)

        self._build_generate_section()
        self._build_manual_section()
        self._build_import_section()

        self.output = ctk.CTkTextbox(self, wrap="word", font=("Courier New", 14), state="disabled")
        self.output.pack(fill="both", expand=True, padx=12, pady=(8, 4))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=(4, 12))
        ctk.CTkButton(bar, text="Копіювати відкритий ключ", width=220,
                      command=self._copy_public).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Експорт відкритого ключа (XML)...", width=260,
                      command=self._export_public).pack(side="left", padx=4)
        ctk.CTkButton(
            bar, text="Застосувати", width=130, command=self._apply,
            fg_color=Colors.SUCCESS, hover_color=Colors.SUCCESS_HOVER,
        ).pack(side="right", padx=4)

        self._show(key)
        self.after(150, self._grab)

    # Побудова інтерфейсу
    def _section(self, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold"), anchor="w").pack(
            fill="x", padx=8, pady=(6, 0))
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 6))
        return row

    @staticmethod
    def _entry(row, label: str, width: int, value: str = "", placeholder: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(row, text=label).pack(side="left", padx=(6, 2))
        entry = ctk.CTkEntry(row, width=width, placeholder_text=placeholder)
        if value:
            entry.insert(0, value)
        entry.pack(side="left", padx=4, pady=6)
        return entry

    def _build_generate_section(self):
        row = self._section("1. Генерація випадкової пари ключів")
        self.bits_entry = self._entry(row, "Розмір n (біт):", 90, str(DEFAULT_KEY_BITS))
        self.gen_e_entry = self._entry(row, "e:", 110, str(DEFAULT_PUBLIC_EXPONENT), "авто")
        ctk.CTkButton(
            row, text="Згенерувати", width=140, command=self._generate,
            fg_color=Colors.TEAL, hover_color=Colors.TEAL_HOVER,
        ).pack(side="left", padx=8)

    def _build_manual_section(self):
        row = self._section("2. Задати p, q, e вручну (числовий приклад)")
        self.p_entry = self._entry(row, "p:", 130)
        self.q_entry = self._entry(row, "q:", 130)
        self.e_entry = self._entry(row, "e:", 90)
        ctk.CTkButton(row, text="Обчислити", width=120, command=self._build_manual).pack(side="left", padx=8)
        ctk.CTkButton(
            row, text="Приклад з Вікіпедії", width=170, command=self._fill_wiki_example,
            fg_color=Colors.NEUTRAL, hover_color=Colors.NEUTRAL_HOVER,
        ).pack(side="left", padx=4)

    def _build_import_section(self):
        row = self._section("3. Відкритий ключ іншої сторони (для шифрування повідомлення їй)")
        self.public_entry = self._entry(row, "(e, n):", 360, placeholder="Наприклад: 17, 3233")
        ctk.CTkButton(row, text="Імпортувати", width=130, command=self._import_public).pack(side="left", padx=8)
        ctk.CTkButton(row, text="З файлу XML...", width=140, command=self._import_xml).pack(side="left", padx=4)

    def _grab(self):
        try:
            self.lift()
            self.grab_set()
        except Exception:
            pass

    # Дії
    def _error(self, err: Exception):
        messagebox.showerror("Помилка", str(err), parent=self)

    def _generate(self):
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            key = generate_keypair(self.bits_entry.get(), self.gen_e_entry.get().strip() or None)
        except (ValueError, TypeError) as err:
            self._error(err)
            return
        finally:
            self.configure(cursor="")
        self._show(key)

    def _fill_wiki_example(self):
        for entry, value in zip((self.p_entry, self.q_entry, self.e_entry), WIKI_EXAMPLE):
            entry.delete(0, "end")
            entry.insert(0, value)
        self._build_manual()

    def _build_manual(self):
        try:
            key = build_key(self.p_entry.get(), self.q_entry.get(), self.e_entry.get())
        except (ValueError, TypeError) as err:
            self._error(err)
            return
        self._show(key)

    def _import_public(self):
        try:
            key = parse_public_key(self.public_entry.get())
        except (ValueError, TypeError) as err:
            self._error(err)
            return
        self._show(key)

    def _import_xml(self):
        path = filedialog.askopenfilename(filetypes=XML_FILE_TYPES, parent=self)
        if not path:
            return
        try:
            key = RSAKey.from_xml(FileManager.read_file(path))
        except (OSError, UnicodeDecodeError, ValueError) as err:
            self._error(err)
            return
        self._show(key)

    def _require_key(self) -> RSAKey | None:
        if self._key is None:
            messagebox.showwarning("Увага", "Спочатку згенеруйте або задайте ключі.", parent=self)
        return self._key

    def _copy_public(self):
        key = self._require_key()
        if key is None:
            return
        self.clipboard_clear()
        self.clipboard_append(key.public_str())

    def _export_public(self):
        key = self._require_key()
        if key is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xml", initialfile="public_key.xml", filetypes=XML_FILE_TYPES, parent=self,
        )
        if not path:
            return
        try:
            FileManager.save_file(path, key.to_xml(include_private=False))
        except OSError as err:
            self._error(err)
            return
        messagebox.showinfo("Готово", f"Відкритий ключ збережено:\n{path}", parent=self)

    def _apply(self):
        key = self._require_key()
        if key is None:
            return
        self._on_apply(key)
        self.destroy()

    # Відображення
    def _show(self, key: RSAKey | None):
        self._key = key
        if key is None:
            text = "Ключі ще не задано."
        else:
            lines = [f"n = {key.n}", f"    ({key.bits} біт, {len(str(key.n))} десяткових цифр)"]
            if key.p is not None:
                lines += [f"p = {key.p}", f"q = {key.q}", f"φ(n) = (p-1)(q-1) = {key.phi}"]
            lines += ["", f"e = {key.e}"]
            if key.has_private:
                lines.append(f"d = e^-1 mod φ(n) = {key.d}")
            lines += ["", f"Відкритий ключ (e, n): {key.public_str()}"]
            if key.has_private:
                lines.append(f"Закритий ключ (d, n): {key.private_str()}")
            else:
                lines.append("Закритий ключ: невідомий (можна лише шифрувати)")
            lines += ["", "XML відкритого ключа (ToXmlString(false)):", key.to_xml(include_private=False)]
            text = "\n".join(lines)

        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")
