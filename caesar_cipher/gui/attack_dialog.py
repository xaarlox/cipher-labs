from tkinter import messagebox
import customtkinter as ctk

from caesar_cipher.core import TrithemiusAttack


class AttackDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Активна атака на шифр Тритеміуса")
        self.geometry("900x1100")
        self.minsize(600, 500)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        self.lbl_plain = ctk.CTkLabel(self, text="Відкритий текст (Plaintext):", font=("Arial", 14, "bold"))
        self.lbl_plain.pack(pady=(15, 5), padx=15, anchor="w")

        self.txt_plain = ctk.CTkTextbox(self, height=100, wrap="word", font=("Arial", 14))
        self.txt_plain.pack(fill="x", padx=15)

        self.lbl_cipher = ctk.CTkLabel(self, text="Зашифрований текст (Ciphertext):", font=("Arial", 14, "bold"))
        self.lbl_cipher.pack(pady=(15, 5), padx=15, anchor="w")

        self.txt_cipher = ctk.CTkTextbox(self, height=100, wrap="word", font=("Arial", 14))
        self.txt_cipher.pack(fill="x", padx=15)

        self.btn_analyze = ctk.CTkButton(
            self, text="Знайти ключ шифрування",
            command=self._run_attack,
            height=35,
            font=("Arial", 14, "bold")
        )
        self.btn_analyze.pack(pady=20)

        self.lbl_result = ctk.CTkLabel(self, text="Знайдені ключі:", font=("Arial", 14, "bold"))
        self.lbl_result.pack(pady=(0, 5), padx=15, anchor="w")

        self.txt_result = ctk.CTkTextbox(self, height=100, state="disabled", font=("Consolas", 14))
        self.txt_result.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _run_attack(self):
        plain = self.txt_plain.get("1.0", "end-1c").strip()
        cipher = self.txt_cipher.get("1.0", "end-1c").strip()

        if not plain or not cipher:
            messagebox.showwarning("Увага", "Для проведення аналізу необхідно ввести обидва тексти.")
            return

        try:
            results = TrithemiusAttack.analyze(plain, cipher)

            output = []
            if results.get("linear"):
                output.append(f"Лінійний ключ (A, B): {results['linear']}")
            else:
                output.append("Лінійний ключ (A, B): Не знайдено")

            if results.get("quadratic"):
                output.append(f"Квадратичний ключ (A, B, C): {results['quadratic']}")
            else:
                output.append("Квадратичний ключ (A, B, C): Не знайдено")

            if results.get("passphrase"):
                output.append(f"Гасло: '{results['passphrase']}'")
            else:
                output.append("Гасло: Не знайдено")

            self.txt_result.configure(state="normal")
            self.txt_result.delete("1.0", "end")
            self.txt_result.insert("1.0", "\n".join(output))
            self.txt_result.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Помилка аналізу", f"Не вдалося виконати злом:\n{str(e)}")
