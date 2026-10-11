import unittest

from cipher_labs.core import DataValidator


class TestDataValidator(unittest.TestCase):
    def test_validate_text(self):
        self.assertEqual(DataValidator.validate_text("Привіт"), "Привіт")

        with self.assertRaises(ValueError):
            DataValidator.validate_text("")

        with self.assertRaises(TypeError):
            DataValidator.validate_text(12345)

    def test_validate_bytes(self):
        valid_bytes = b"sample_bytes"
        self.assertEqual(DataValidator.validate_bytes(valid_bytes), valid_bytes)
        self.assertEqual(DataValidator.validate_bytes(bytearray(b"test")), b"test")

        with self.assertRaises(ValueError):
            DataValidator.validate_bytes(b"")

        with self.assertRaises(TypeError):
            DataValidator.validate_bytes("рядок замість байтів")


if __name__ == "__main__":
    unittest.main()
