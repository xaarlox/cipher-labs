import random
import unittest

from cipher_labs.core import PoemCipher, WordBookCipher

POEM = (
    "Як умру, то поховайте\n"
    "Мене на могилі\n"
    "Серед степу широкого\n"
    "На Вкраїні милій\n"
)

LETTER_WORDS = "а б в г д е ж з и і к л м н о п р с т у я"


def poem_cipher(width=30, seed=1):
    return PoemCipher(width=width, rng=random.Random(seed))


class TestPoemCipher(unittest.TestCase):
    def test_known_positions_decrypt(self):
        self.assertEqual(poem_cipher().decrypt("1/1, 1/2, _, 2/1", POEM), "як м")

    def test_roundtrip(self):
        for seed in range(5):
            with self.subTest(seed=seed):
                cipher = poem_cipher(seed=seed)
                code = cipher.encrypt("Поховайте мене", POEM)
                self.assertEqual(cipher.decrypt(code, POEM), "поховайте мене")

    def test_encryption_is_randomized(self):
        codes = {poem_cipher(seed=s).encrypt("ооо", POEM) for s in range(20)}
        self.assertGreater(len(codes), 1)

    def test_punctuation_is_skipped_and_spaces_kept(self):
        cipher = poem_cipher()
        code = cipher.encrypt("Мене, на!", POEM)
        self.assertIn("_", code)
        self.assertEqual(cipher.decrypt(code, POEM), "мене на")

    def test_shch_is_replaced_with_sh(self):
        cipher = poem_cipher()
        self.assertEqual(cipher.decrypt(cipher.encrypt("щ", POEM), POEM), "ш")

    def test_missing_letter_raises(self):
        with self.assertRaises(ValueError):
            poem_cipher().encrypt("ф", POEM)

    def test_narrow_width_drops_letters(self):
        with self.assertRaises(ValueError):
            poem_cipher(width=10).encrypt("х", POEM)

    def test_out_of_range_positions_raise(self):
        cipher = poem_cipher()
        for code in ("99/1", "1/99", "0/1", "1/0"):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    cipher.decrypt(code, POEM)

    def test_bad_token_raises(self):
        with self.assertRaises(ValueError):
            poem_cipher().decrypt("abc", POEM)

    def test_empty_inputs_raise(self):
        with self.assertRaises(ValueError):
            poem_cipher().encrypt("", POEM)
        with self.assertRaises(ValueError):
            poem_cipher().encrypt("привіт", "   ")
        with self.assertRaises(ValueError):
            poem_cipher().decrypt("", POEM)

    def test_text_without_letters_raises(self):
        with self.assertRaises(ValueError):
            poem_cipher().encrypt("123 !!!", POEM)

    def test_invalid_width_raises(self):
        with self.assertRaises(ValueError):
            PoemCipher(width=0)


class TestWordBookCipher(unittest.TestCase):
    def test_known_numbers_decrypt(self):
        self.assertEqual(WordBookCipher().decrypt("1, 2, 3", LETTER_WORDS), "абв")

    def test_roundtrip(self):
        for seed in range(5):
            with self.subTest(seed=seed):
                cipher = WordBookCipher(rng=random.Random(seed))
                code = cipher.encrypt("Мене на могилі", LETTER_WORDS)
                self.assertEqual(cipher.decrypt(code, LETTER_WORDS), "мене на могилі")

    def test_picks_any_matching_word(self):
        key = "ананас авокадо абрикос"
        numbers = {WordBookCipher(rng=random.Random(s)).encrypt("а", key) for s in range(30)}
        self.assertEqual(numbers, {"1", "2", "3"})

    def test_missing_letter_raises(self):
        with self.assertRaises(ValueError):
            WordBookCipher().encrypt("ф", LETTER_WORDS)

    def test_out_of_range_number_raises(self):
        with self.assertRaises(ValueError):
            WordBookCipher().decrypt("99", LETTER_WORDS)
        with self.assertRaises(ValueError):
            WordBookCipher().decrypt("0", LETTER_WORDS)

    def test_bad_token_raises(self):
        with self.assertRaises(ValueError):
            WordBookCipher().decrypt("1/2", LETTER_WORDS)


if __name__ == "__main__":
    unittest.main()
