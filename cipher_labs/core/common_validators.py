class DataValidator:
    @staticmethod
    def validate_text(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError(f"Очікувався рядок, отримано {type(text).__name__}.")
        if len(text) == 0:
            raise ValueError("Текст для обробки не може бути порожнім.")
        return text

    @staticmethod
    def validate_bytes(data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"Очікувались байти, отримано {type(data).__name__}.")
        if len(data) == 0:
            raise ValueError("Дані для обробки не можуть бути порожніми.")
        return bytes(data)
