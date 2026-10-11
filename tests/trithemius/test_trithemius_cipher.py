import unittest

from cipher_labs.core import TextTrithemiusCipher


class TestTextTrithemiusCipher(unittest.TestCase):
    def test_linear_mode(self):
        cipher = TextTrithemiusCipher(mode='linear')
        original = "Криптографія - це цікаво!"
        key = "2, 5"

        encrypted = cipher.encrypt(original, key)
        decrypted = cipher.decrypt(encrypted, key)

        self.assertNotEqual(original, encrypted)
        self.assertEqual(decrypted, original)
        self.assertIn("-", encrypted)

    def test_quadratic_mode(self):
        cipher = TextTrithemiusCipher(mode='quadratic')
        original = "The Quick Brown Fox Jumps Over 13 Lazy Dogs!"
        key = "1, 2, 3"

        encrypted = cipher.encrypt(original, key)
        decrypted = cipher.decrypt(encrypted, key)

        self.assertNotEqual(original, encrypted)
        self.assertEqual(decrypted, original)
        self.assertIn("13", encrypted)

    def test_passphrase_mode(self):
        cipher = TextTrithemiusCipher(mode='passphrase')
        original = "Юний ґазда з'їв яблуко біля єнота!"
        key = "ключ"

        encrypted = cipher.encrypt(original, key)
        decrypted = cipher.decrypt(encrypted, key)

        self.assertEqual(decrypted, original)

    def test_invalid_mode_initialization(self):
        with self.assertRaises(ValueError):
            TextTrithemiusCipher(mode='unknown_mode')

    def test_position_counter_ignores_punctuation(self):
        # Пробіли та знаки пунктуації не мають збільшувати позицію p
        cipher = TextTrithemiusCipher(mode='linear')
        key = "1, 0"  # k = 1 * p + 0

        # Для тексту "A B" літера 'A' має p=0, а 'B' має p=1
        original = "A B"
        encrypted = cipher.encrypt(original, key)

        # A (p=0, k=0) -> A; пробіл пропускається; B (p=1, k=1) -> C
        self.assertEqual(encrypted, "A C")


if __name__ == "__main__":
    unittest.main()
