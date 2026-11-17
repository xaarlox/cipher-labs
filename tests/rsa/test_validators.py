import unittest

from cipher_labs.core.ciphers.rsa import RSADataValidator, RSAKeyValidator, build_key


class TestToInt(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(RSAKeyValidator.to_int("61", "p"), 61)
        self.assertEqual(RSAKeyValidator.to_int(" 1 000 ", "p"), 1000)
        self.assertEqual(RSAKeyValidator.to_int(53, "q"), 53)

    def test_invalid(self):
        for bad in ("abc", "", "1.5", True, None, 3.0):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    RSAKeyValidator.to_int(bad, "p")


class TestBitsAndExponent(unittest.TestCase):
    def test_bits_range(self):
        self.assertEqual(RSAKeyValidator.validate_bits("1024"), 1024)
        for bad in (8, 15, 4097, "x"):
            with self.subTest(bits=bad):
                with self.assertRaises(ValueError):
                    RSAKeyValidator.validate_bits(bad)

    def test_exponent(self):
        self.assertEqual(RSAKeyValidator.validate_exponent("65537"), 65537)
        for bad in (1, 2, 4, 65536, -3):
            with self.subTest(e=bad):
                with self.assertRaises(ValueError):
                    RSAKeyValidator.validate_exponent(bad)


class TestComponents(unittest.TestCase):
    def test_wiki_example(self):
        self.assertEqual(RSAKeyValidator.validate_components(61, 53, 17), (61, 53, 17, 3120))

    def test_non_prime(self):
        with self.assertRaises(ValueError):
            RSAKeyValidator.validate_components(60, 53, 17)
        with self.assertRaises(ValueError):
            RSAKeyValidator.validate_components(61, 51, 17)

    def test_equal_primes(self):
        with self.assertRaises(ValueError):
            RSAKeyValidator.validate_components(61, 61, 17)

    def test_e_not_coprime(self):
        with self.assertRaises(ValueError) as ctx:
            RSAKeyValidator.validate_components(61, 53, 15)  # НСД(15, 3120) = 15
        self.assertIn("НСД", str(ctx.exception))

    def test_e_out_of_range(self):
        for e in (1, 3120, 5000):
            with self.subTest(e=e):
                with self.assertRaises(ValueError):
                    RSAKeyValidator.validate_components(61, 53, e)


class TestParsePair(unittest.TestCase):
    def test_formats(self):
        for text in ("17, 3233", "(17,3233)", "17 3233", "17;3233"):
            with self.subTest(text=text):
                self.assertEqual(RSAKeyValidator.parse_pair(text, "e"), (17, 3233))

    def test_invalid(self):
        for bad in ("17", "17, 3233, 5", "e, n", "3233, 17", "17, 3"):
            with self.subTest(text=bad):
                with self.assertRaises(ValueError):
                    RSAKeyValidator.parse_pair(bad, "e")
        with self.assertRaises(TypeError):
            RSAKeyValidator.parse_pair(17, "e")


class TestValidateKey(unittest.TestCase):
    def test_none_and_wrong_type(self):
        with self.assertRaises(ValueError):
            RSAKeyValidator.validate_key(None, need_private=False)
        with self.assertRaises(TypeError):
            RSAKeyValidator.validate_key("17, 3233", need_private=False)

    def test_private_required(self):
        key = build_key(61, 53, 17)
        self.assertIs(RSAKeyValidator.validate_key(key, need_private=True), key)
        with self.assertRaises(ValueError):
            RSAKeyValidator.validate_key(key.public_key(), need_private=True)


class TestParseNumbers(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(RSADataValidator.parse_numbers("65, 66 67;\n68", 3233), [65, 66, 67, 68])

    def test_invalid(self):
        for bad in ("", "  ", "a, 1", "-1", "1.5", "3233"):
            with self.subTest(text=bad):
                with self.assertRaises(ValueError):
                    RSADataValidator.parse_numbers(bad, 3233)
        with self.assertRaises(TypeError):
            RSADataValidator.parse_numbers(65, 3233)


if __name__ == "__main__":
    unittest.main()
