import unittest

from cipher_labs.core import KeyValidator


class TestKeyValidator(unittest.TestCase):
    def test_valid_key(self):
        self.assertEqual(KeyValidator.validate(3), 3)
        self.assertEqual(KeyValidator.validate(-5), -5)
        self.assertEqual(KeyValidator.validate("14"), 14)

    def test_rejects_bool(self):
        with self.assertRaises(ValueError):
            KeyValidator.validate(True)
        with self.assertRaises(ValueError):
            KeyValidator.validate(False)

    def test_rejects_non_integers(self):
        invalid_keys = ["abc", "3.14", None, [], {}, "3a"]

        for key in invalid_keys:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    KeyValidator.validate(key)


if __name__ == "__main__":
    unittest.main()
