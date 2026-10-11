import unittest

from cipher_labs.core import BookTextValidator, PoemKeyValidator


class TestPoemKeyValidator(unittest.TestCase):
    def test_validate_width(self):
        self.assertEqual(PoemKeyValidator.validate_width(10), 10)
        self.assertEqual(PoemKeyValidator.validate_width("12"), 12)

        for bad in (0, 100, -1, "abc", "3.5", None, True):
            with self.subTest(width=bad):
                with self.assertRaises(ValueError):
                    PoemKeyValidator.validate_width(bad)

    def test_rows_are_trimmed_and_normalized(self):
        rows = PoemKeyValidator.validate("Як умру, то поховайте\nМене на могилі", 10)
        self.assertEqual(rows, ["якумрутопо", "мененамоги"])

    def test_empty_lines_and_punctuation_are_skipped(self):
        rows = PoemKeyValidator.validate("\n  ...  \nАбв\n", 10)
        self.assertEqual(rows, ["абв"])

    def test_no_letters_raises(self):
        with self.assertRaises(ValueError):
            PoemKeyValidator.validate("123 !!! ...", 10)
        with self.assertRaises(ValueError):
            PoemKeyValidator.validate("   ", 10)

    def test_too_many_rows_raises(self):
        with self.assertRaises(ValueError):
            PoemKeyValidator.validate("а\n" * 100, 10)

    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            PoemKeyValidator.validate(123, 10)


class TestBookTextValidator(unittest.TestCase):
    def test_words_are_extracted_lowercase(self):
        self.assertEqual(BookTextValidator.validate("Як умру, то 123 ПОХОВАЙТЕ"),
                         ["як", "умру", "то", "поховайте"])

    def test_no_words_raises(self):
        with self.assertRaises(ValueError):
            BookTextValidator.validate("123 !!! ...")

    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            BookTextValidator.validate(None)


if __name__ == "__main__":
    unittest.main()
