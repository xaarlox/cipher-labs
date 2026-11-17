import unittest

from cipher_labs.core.ciphers.rsa import RSACipher, RSAKey, build_key, generate_keypair

# Числовий приклад з Вікіпедії: p = 61, q = 53, e = 17, m = 65 -> c = 2790
WIKI_KEY = build_key(61, 53, 17)


class TestNumericExample(unittest.TestCase):
    def test_key_parameters(self):
        self.assertEqual(WIKI_KEY.n, 3233)
        self.assertEqual(WIKI_KEY.phi, 3120)
        self.assertEqual(WIKI_KEY.d, 2753)

    def test_encrypt_number(self):
        self.assertEqual(RSACipher("numbers").encrypt("65", WIKI_KEY), "2790")

    def test_decrypt_number(self):
        self.assertEqual(RSACipher("numbers").decrypt("2790", WIKI_KEY), "65")

    def test_wikipedia_carmichael_exponent_also_works(self):
        # У Вікіпедії d = 413 обчислено через λ(n) = 780; результат той самий
        key = RSAKey(n=3233, e=17, d=413)
        self.assertEqual(RSACipher("numbers").decrypt("2790", key), "65")

    def test_several_numbers(self):
        cipher = RSACipher("numbers")
        encrypted = cipher.encrypt("0, 1, 65, 3232", WIKI_KEY)
        self.assertEqual(cipher.decrypt(encrypted, WIKI_KEY), "0, 1, 65, 3232")

    def test_public_key_only_can_encrypt(self):
        public = WIKI_KEY.public_key()
        self.assertEqual(RSACipher("numbers").encrypt("65", public), "2790")
        with self.assertRaises(ValueError):
            RSACipher("numbers").decrypt("2790", public)


class TestTextMode(unittest.TestCase):
    def test_single_byte_blocks_match_numeric_example(self):
        # n = 3233 -> блок 1 байт; 'A' = 65 -> 2790
        self.assertEqual(RSACipher("text").encrypt("A", WIKI_KEY), "2790")

    def test_roundtrip_small_key(self):
        cipher = RSACipher("text")
        text = "Hello, світ! ґ є ї 123"
        self.assertEqual(cipher.decrypt(cipher.encrypt(text, WIKI_KEY), WIKI_KEY), text)

    def test_roundtrip_various_key_sizes(self):
        text = "Федоренко Валерія Андріївна — RSA test, 2026!"
        for bits in (16, 32, 64, 256, 512, 1024):
            with self.subTest(bits=bits):
                key = generate_keypair(bits)
                cipher = RSACipher("text")
                self.assertEqual(cipher.decrypt(cipher.encrypt(text, key), key), text)

    def test_roundtrip_all_lengths(self):
        key = generate_keypair(64)
        cipher = RSACipher("text")
        for length in range(1, 30):
            with self.subTest(length=length):
                text = "ab" * length
                self.assertEqual(cipher.decrypt(cipher.encrypt(text, key), key), text)

    def test_wrong_key_fails(self):
        key, other = generate_keypair(512), generate_keypair(512)
        encrypted = RSACipher("text").encrypt("Таємниця", key)
        wrong = RSAKey(n=key.n, e=key.e, d=other.d)
        with self.assertRaises(ValueError):
            RSACipher("text").decrypt(encrypted, wrong)

    def test_too_small_modulus_for_text(self):
        key = build_key(5, 11, 3)  # n = 55 < 256
        with self.assertRaises(ValueError):
            RSACipher("text").encrypt("A", key)

    def test_nul_character_rejected(self):
        with self.assertRaises(ValueError):
            RSACipher("text").encrypt("a\x00b", WIKI_KEY)


class TestErrors(unittest.TestCase):
    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            RSACipher("blocks")

    def test_no_key(self):
        with self.assertRaises(ValueError):
            RSACipher().encrypt("text", None)

    def test_wrong_key_type(self):
        with self.assertRaises(TypeError):
            RSACipher().encrypt("text", "17, 3233")

    def test_number_not_less_than_n(self):
        with self.assertRaises(ValueError):
            RSACipher("numbers").encrypt("3233", WIKI_KEY)
        with self.assertRaises(ValueError):
            RSACipher("numbers").decrypt("5000", WIKI_KEY)

    def test_non_numeric_ciphertext(self):
        with self.assertRaises(ValueError):
            RSACipher("text").decrypt("12, abc", WIKI_KEY)
        with self.assertRaises(ValueError):
            RSACipher("numbers").encrypt("-5", WIKI_KEY)

    def test_empty_text(self):
        with self.assertRaises(ValueError):
            RSACipher().encrypt("", WIKI_KEY)


if __name__ == "__main__":
    unittest.main()
