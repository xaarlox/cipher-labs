import unittest

from cipher_labs.core import TrithemiusKeyValidator


class TestTrithemiusKeyValidator(unittest.TestCase):
    def test_validate_linear(self):
        self.assertEqual(TrithemiusKeyValidator.validate_linear("2, 5"), (2, 5))
        self.assertEqual(TrithemiusKeyValidator.validate_linear(" 2 ; 5 "), (2, 5))
        self.assertEqual(TrithemiusKeyValidator.validate_linear([2, 5]), (2, 5))
        self.assertEqual(TrithemiusKeyValidator.validate_linear("-1, 10"), (-1, 10))

        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_linear("2, 5, 3")
        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_linear("2")
        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_linear("A, B")

    def test_validate_quadratic(self):
        self.assertEqual(TrithemiusKeyValidator.validate_quadratic("1, 2, 3"), (1, 2, 3))
        self.assertEqual(TrithemiusKeyValidator.validate_quadratic(" -1 ; 0 ; 5 "), (-1, 0, 5))
        self.assertEqual(TrithemiusKeyValidator.validate_quadratic((4, 5, 6)), (4, 5, 6))

        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_quadratic("1, 2")
        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_quadratic("1, 2, 3.5")

    def test_validate_passphrase(self):
        self.assertEqual(TrithemiusKeyValidator.validate_passphrase("Секрет"), "Секрет")
        self.assertEqual(TrithemiusKeyValidator.validate_passphrase(" password "), "password")

        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_passphrase("")
        with self.assertRaises(ValueError):
            TrithemiusKeyValidator.validate_passphrase("secret 123")
        with self.assertRaises(TypeError):
            TrithemiusKeyValidator.validate_passphrase(123)


if __name__ == "__main__":
    unittest.main()
