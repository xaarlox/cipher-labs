from tkinter import messagebox

import customtkinter as ctk

from cipher_labs.core import RSAAttack, RSACipher, RSAKey, RSAKeyValidator
from cipher_labs.gui.colors import Colors

ONLINE_CALCULATOR = "https://www.alpertron.com.ar/ECM.HTM"
MAX_TIMEOUT = 600


class RSAAttackDialog(ctk.CTkToplevel):
    """Атака на RSA: факторизація n = p*q, відновлення d та розшифрування перехопленої шифрограми"""

    def __init__(self, parent, *, public_key: RSAKey | None, ciphertext: str, mode: str):
        super().__init__(parent)
        self.title("Атака на RSA (факторизація модуля n)")
        self.geometry("1100x1300")
        self.minsize(700, 600)
        self.transient(parent)
        self.grab_set()

        bold = ("Arial", 14, "bold")

        ctk.CTkLabel(self, text="Відкритий ключ жертви (e, n):", font=bold).pack(
            pady=(15, 5), padx=15, anchor="w")
        key_row = ctk.CTkFrame(self, fg_color="transparent")
        key_row.pack(fill="x", padx=15)
        ctk.CTkLabel(key_row, text="e:").pack(side="left")
        self.e_entry = ctk.CTkEntry(key_row, width=120)
        self.e_entry.pack(side="left", padx=6)
        ctk.CTkLabel(key_row, text="n:").pack(side="left")
        self.n_entry = ctk.CTkEntry(key_row)
        self.n_entry.pack(side="left", padx=6, fill="x", expand=True)
        if public_key is not None:
            self.e_entry.insert(0, str(public_key.e))
            self.n_entry.insert(0, str(public_key.n))

        ctk.CTkLabel(self, text="Перехоплена шифрограма (необов'язково):", font=bold).pack(
            pady=(15, 5), padx=15, anchor="w")
        self.txt_cipher = ctk.CTkTextbox(self, height=80, wrap="word", font=("Arial", 14))
        self.txt_cipher.pack(fill="x", padx=15)
        self.txt_cipher.insert("1.0", ciphertext.strip())

        opts = ctk.CTkFrame(self, fg_color="transparent")
        opts.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(opts, text="Шифрограма містить:").pack(side="left")
        self.mode = ctk.CTkSegmentedButton(opts, values=["Текст", "Числа"])
        self.mode.set("Числа" if mode == "numbers" else "Текст")
        self.mode.pack(side="left", padx=6)
        ctk.CTkLabel(opts, text="Ліміт часу (с):").pack(side="left", padx=(20, 2))
        self.timeout_entry = ctk.CTkEntry(opts, width=70)
        self.timeout_entry.insert(0, "30")
        self.timeout_entry.pack(side="left", padx=4)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(pady=15)
        ctk.CTkButton(
            buttons, text="Розкласти n і знайти закритий ключ", command=self._run_attack, height=35,
            font=bold, fg_color=Colors.DANGER, hover_color=Colors.DANGER_HOVER,
        ).pack(side="left", padx=6)
        ctk.CTkButton(buttons, text="Копіювати n", width=120, command=self._copy_n).pack(side="left", padx=6)

        ctk.CTkLabel(
            self, anchor="w", justify="left",
            text=f"Перевірити розклад можна онлайн-калькулятором:\n{ONLINE_CALCULATOR}",
        ).pack(fill="x", padx=15)

        ctk.CTkLabel(self, text="Результат:", font=bold).pack(pady=(10, 5), padx=15, anchor="w")
        self.txt_result = ctk.CTkTextbox(self, state="disabled", wrap="word", font=("Courier New", 14))
        self.txt_result.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _copy_n(self):
        self.clipboard_clear()
        self.clipboard_append(self.n_entry.get().strip())

    def _read_timeout(self) -> float:
        try:
            timeout = float(self.timeout_entry.get().replace(",", "."))
        except ValueError:
            raise ValueError("Ліміт часу має бути числом.") from None
        if not 0 < timeout <= MAX_TIMEOUT:
            raise ValueError(f"Ліміт часу має бути від 0 до {MAX_TIMEOUT} с.")
        return timeout

    def _show(self, text: str):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", "end")
        self.txt_result.insert("1.0", text)
        self.txt_result.configure(state="disabled")

    def _run_attack(self):
        try:
            e, n = RSAKeyValidator.parse_pair(f"{self.e_entry.get()}, {self.n_entry.get()}", "e")
            timeout = self._read_timeout()
        except (ValueError, TypeError) as err:
            messagebox.showerror("Помилка", str(err), parent=self)
            return

        self._show(f"Розкладаю n ({n.bit_length()} біт)...")
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            result = RSAAttack.recover_private_key(RSAKey(n=n, e=e), timeout=timeout)
        except (ValueError, TypeError) as err:
            self._show(f"Атака не вдалася:\n{err}")
            return
        finally:
            self.configure(cursor="")

        key = result.key
        lines = [
            f"n = {key.n} ({key.bits} біт)",
            f"n = p * q = {result.p} · {result.q}",
            f"Час факторизації: {result.elapsed:.4f} с",
            "",
            f"φ(n) = (p-1)(q-1) = {key.phi}",
            f"d = e^-1 mod φ(n) = {key.d}",
            f"Закритий ключ (d, n): {key.private_str()}",
        ]

        ciphertext = self.txt_cipher.get("1.0", "end-1c").strip()
        if ciphertext:
            cipher = RSACipher("numbers" if self.mode.get() == "Числа" else "text")
            try:
                plain = cipher.decrypt(ciphertext, key)
                lines += ["", "Розшифроване повідомлення:", plain]
            except (ValueError, TypeError) as err:
                lines += ["", f"Не вдалося розшифрувати шифрограму: {err}"]

        self._show("\n".join(lines))
