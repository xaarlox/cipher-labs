import os
import unittest

from cipher_labs.core.ciphers.symmetric import (
    SYMMETRIC_ALGORITHMS,
    SYMMETRIC_MODES,
    SymmetricCipher,
)

KEYS = {
    "DES": "ABCDEFGH",
    "3DES": "ABCDEFGHIJKLMNOP",
    "AES": "0123456789ABCDEF",
}
IVS = {
    "DES": "ABCDEFGH",
    "3DES": "ABCDEFGH",
    "AES": "ABCDEFGHIJKLMNOP",
}


class TestKnownAnswers(unittest.TestCase):
    def test_des_classic_vector(self):
        cipher = SymmetricCipher("DES", "ECB")
        result = cipher.encrypt_bytes(bytes.fromhex("0123456789ABCDEF"), "hex:133457799BBCDFF1")
        self.assertEqual(result[:8].hex().upper(), "85E813540F0AB405")

    def test_aes_fips197_vector(self):
        cipher = SymmetricCipher("AES", "ECB")
        key = "hex:000102030405060708090a0b0c0d0e0f"
        result = cipher.encrypt_bytes(bytes.fromhex("00112233445566778899aabbccddeeff"), key)
        self.assertEqual(result[:16].hex(), "69c4e0d86a7b0430d8cdb78070b4c55a")


class TestRoundtrip(unittest.TestCase):
    def test_text_all_algorithms_and_modes(self):
        original = "Hello World! Привіт, світе: ґанок, єнот, їжак. 12345"
        for algorithm in SYMMETRIC_ALGORITHMS:
            for mode in SYMMETRIC_MODES:
                with self.subTest(algorithm=algorithm, mode=mode):
                    cipher = SymmetricCipher(algorithm, mode, IVS[algorithm])
                    encrypted = cipher.encrypt(original, KEYS[algorithm])
                    self.assertNotEqual(encrypted, original)
                    self.assertEqual(cipher.decrypt(encrypted, KEYS[algorithm]), original)

    def test_bytes_various_lengths(self):
        for algorithm in SYMMETRIC_ALGORITHMS:
            for mode in SYMMETRIC_MODES:
                for length in (1, 7, 8, 9, 15, 16, 17, 1000):
                    with self.subTest(algorithm=algorithm, mode=mode, length=length):
                        data = os.urandom(length)
                        cipher = SymmetricCipher(algorithm, mode, IVS[algorithm])
                        encrypted = cipher.encrypt_bytes(data, KEYS[algorithm])
                        self.assertEqual(cipher.decrypt_bytes(encrypted, KEYS[algorithm]), data)

    def test_methodical_example_des_cbc(self):
        cipher = SymmetricCipher("DES", "CBC", "ABCDEFGH")
        encrypted = cipher.encrypt_bytes(b"Hello World!", "ABCDEFGH")
        self.assertEqual(len(encrypted), 16)  # 12 байт + PKCS7 до 16
        self.assertEqual(cipher.decrypt_bytes(encrypted, "ABCDEFGH"), b"Hello World!")

    def test_3des_with_24_byte_key(self):
        cipher = SymmetricCipher("3DES", "CBC", "ABCDEFGH")
        key = "ABCDEFGHIJKLMNOPQRSTUVWX"
        encrypted = cipher.encrypt("Секретне повідомлення", key)
        self.assertEqual(cipher.decrypt(encrypted, key), "Секретне повідомлення")

    def test_hex_key_and_iv(self):
        cipher = SymmetricCipher("DES", "CBC", "hex:0102030405060708")
        encrypted = cipher.encrypt("test", "hex:0102030405060708")
        self.assertEqual(cipher.decrypt(encrypted, "hex:01 02 03 04 05 06 07 08"), "test")

    def test_ciphertext_with_separators(self):
        cipher = SymmetricCipher("AES", "CBC", IVS["AES"])
        encrypted = cipher.encrypt("test", KEYS["AES"])
        spaced = "-".join(encrypted[i:i + 2] for i in range(0, len(encrypted), 2))
        self.assertEqual(cipher.decrypt(spaced, KEYS["AES"]), "test")


class TestModeProperties(unittest.TestCase):
    def test_ecb_repeats_blocks_but_cbc_does_not(self):
        data = b"A" * 32
        ecb = SymmetricCipher("AES", "ECB").encrypt_bytes(data, KEYS["AES"])
        cbc = SymmetricCipher("AES", "CBC", IVS["AES"]).encrypt_bytes(data, KEYS["AES"])
        self.assertEqual(ecb[:16], ecb[16:32])
        self.assertNotEqual(cbc[:16], cbc[16:32])

    def test_stream_modes_keep_length(self):
        for mode in ("CFB", "OFB", "CTR"):
            with self.subTest(mode=mode):
                cipher = SymmetricCipher("DES", mode, IVS["DES"])
                self.assertEqual(len(cipher.encrypt_bytes(b"12345", KEYS["DES"])), 5)

    def test_different_iv_gives_different_ciphertext(self):
        a = SymmetricCipher("AES", "CBC", "A" * 16).encrypt("same text", KEYS["AES"])
        b = SymmetricCipher("AES", "CBC", "B" * 16).encrypt("same text", KEYS["AES"])
        self.assertNotEqual(a, b)

    def test_ecb_ignores_iv(self):
        cipher = SymmetricCipher("DES", "ECB", "")
        self.assertEqual(cipher.decrypt(cipher.encrypt("abc", KEYS["DES"]), KEYS["DES"]), "abc")


class TestErrors(unittest.TestCase):
    def test_invalid_algorithm_and_mode(self):
        with self.assertRaises(ValueError):
            SymmetricCipher("RC4", "CBC")
        with self.assertRaises(ValueError):
            SymmetricCipher("AES", "XYZ")

    def test_invalid_key_and_iv_are_reported_on_use(self):
        with self.assertRaises(ValueError):
            SymmetricCipher("DES", "ECB").encrypt("test", "short")
        with self.assertRaises(ValueError):
            SymmetricCipher("AES", "CBC", "ABCDEFGH").encrypt("test", KEYS["AES"])

    def test_invalid_ciphertext_hex(self):
        with self.assertRaises(ValueError):
            SymmetricCipher("DES", "ECB").decrypt("not hex!", KEYS["DES"])

    def test_degenerate_3des_key_rejected(self):
        with self.assertRaises(ValueError):
            SymmetricCipher("3DES", "ECB").encrypt("test", "ABCDEFGHABCDEFGH")

    def test_wrong_key_fails_to_decrypt(self):
        cipher = SymmetricCipher("AES", "CBC", IVS["AES"])
        encrypted = cipher.encrypt("Таємний текст", KEYS["AES"])
        with self.assertRaises(ValueError):
            cipher.decrypt(encrypted, "FEDCBA9876543210")

    def test_truncated_ciphertext(self):
        cipher = SymmetricCipher("DES", "CBC", IVS["DES"])
        with self.assertRaises(ValueError):
            cipher.decrypt("AABBCC", KEYS["DES"])

    def test_empty_and_wrong_types(self):
        cipher = SymmetricCipher("DES", "ECB")
        with self.assertRaises(ValueError):
            cipher.encrypt("", KEYS["DES"])
        with self.assertRaises(TypeError):
            cipher.encrypt_bytes("text", KEYS["DES"])


if __name__ == "__main__":
    unittest.main()
