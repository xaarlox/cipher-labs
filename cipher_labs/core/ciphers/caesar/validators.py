class KeyValidator:
    @staticmethod
    def validate(key) -> int:
        if isinstance(key, bool):
            raise ValueError("Ключ не може бути логічним значенням (True/False).")
        try:
            return int(key)
        except (TypeError, ValueError):
            raise ValueError(f"Некоректний ключ '{key}'. Ключ має бути цілим числом.")
