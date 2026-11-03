import unittest

from cipher_labs.core.ciphers.symmetric import (
    SYMMETRIC_ALGORITHMS,
    SYMMETRIC_MODES,
    SymmetricValidator,
)


class TestAlgorithmAndMode(unittest.TestCase):
    def test_valid_algorithms(self):
        for algorithm in SYMMETRIC_ALGORITHMS:
            self.assertEqual(SymmetricValidator.validate_algorithm(algorithm), algorithm)

    def test_invalid_algorithm(self):
        for bad in ("RC4", "des", "", None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    SymmetricValidator.validate_algorithm(bad)

    def test_valid_modes(self):
        for mode in SYMMETRIC_MODES:
            self.assertEqual(SymmetricValidator.validate_mode(mode), mode)

    def test_invalid_mode(self):
        for bad in ("XYZ", "cbc", "", None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    SymmetricValidator.validate_mode(bad)

    def test_block_and_key_sizes(self):
        self.assertEqual(SymmetricValidator.block_size("DES"), 8)
        self.assertEqual(SymmetricValidator.block_size("3DES"), 8)
        self.assertEqual(SymmetricValidator.block_size("AES"), 16)
        self.assertEqual(SymmetricValidator.key_sizes("DES"), (8,))
        self.assertEqual(SymmetricValidator.key_sizes("3DES"), (16, 24))
        self.assertEqual(SymmetricValidator.key_sizes("AES"), (16, 24, 32))


class TestParseBytes(unittest.TestCase):
    def test_plain_text_is_utf8(self):
        self.assertEqual(SymmetricValidator.parse_bytes("ABC", "Ключ"), b"ABC")
        self.assertEqual(SymmetricValidator.parse_bytes("ключ", "Ключ"), "ключ".encode("utf-8"))

    def test_hex_notation(self):
        self.assertEqual(SymmetricValidator.parse_bytes("hex:0102ff", "Ключ"), b"\x01\x02\xff")
        self.assertEqual(SymmetricValidator.parse_bytes("HEX:01 02-FF", "Ключ"), b"\x01\x02\xff")

    def test_bytes_passthrough(self):
        self.assertEqual(SymmetricValidator.parse_bytes(b"\x01\x02", "Ключ"), b"\x01\x02")
        self.assertEqual(SymmetricValidator.parse_bytes(bytearray(b"\x01"), "Ключ"), b"\x01")

    def test_invalid_hex(self):
        for bad in ("hex:ZZ", "hex:123", "hex:0g"):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    SymmetricValidator.parse_bytes(bad, "Ключ")

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            SymmetricValidator.parse_bytes(123, "Ключ")


class TestKeyValidation(unittest.TestCase):
    def test_valid_key_lengths(self):
        cases = {"DES": (8,), "3DES": (16, 24), "AES": (16, 24, 32)}
        for algorithm, lengths in cases.items():
            for length in lengths:
                with self.subTest(algorithm=algorithm, length=length):
                    key = SymmetricValidator.validate_key(algorithm, "K" * length)
                    self.assertEqual(len(key), length)

    def test_invalid_key_lengths(self):
        cases = {"DES": (0, 7, 16), "3DES": (8, 15, 32), "AES": (8, 15, 17, 33)}
        for algorithm, lengths in cases.items():
            for length in lengths:
                with self.subTest(algorithm=algorithm, length=length):
                    with self.assertRaises(ValueError):
                        SymmetricValidator.validate_key(algorithm, "K" * length)

    def test_hex_key(self):
        key = SymmetricValidator.validate_key("DES", "hex:0102030405060708")
        self.assertEqual(key, bytes(range(1, 9)))

    def test_key_length_counts_bytes_not_characters(self):
        # 4 українські літери = 8 байт UTF-8
        self.assertEqual(len(SymmetricValidator.validate_key("DES", "ключ")), 8)


class TestIvValidation(unittest.TestCase):
    def test_ecb_has_no_iv(self):
        self.assertIsNone(SymmetricValidator.validate_iv("AES", "ECB", ""))
        self.assertIsNone(SymmetricValidator.validate_iv("DES", "ECB", "anything"))

    def test_valid_iv_for_every_other_mode(self):
        for algorithm in SYMMETRIC_ALGORITHMS:
            block = SymmetricValidator.block_size(algorithm)
            for mode in SYMMETRIC_MODES:
                if mode == "ECB":
                    continue
                with self.subTest(algorithm=algorithm, mode=mode):
                    iv = SymmetricValidator.validate_iv(algorithm, mode, "I" * block)
                    self.assertEqual(len(iv), block)

    def test_invalid_iv_length(self):
        with self.assertRaises(ValueError):
            SymmetricValidator.validate_iv("AES", "CBC", "ABCDEFGH")  # потрібно 16
        with self.assertRaises(ValueError):
            SymmetricValidator.validate_iv("DES", "CBC", "ABCDEFGHIJKLMNOP")  # потрібно 8
        with self.assertRaises(ValueError):
            SymmetricValidator.validate_iv("DES", "CFB", "")

    def test_ctr_message_mentions_counter(self):
        with self.assertRaises(ValueError) as ctx:
            SymmetricValidator.validate_iv("AES", "CTR", "short")
        self.assertIn("лічильника", str(ctx.exception))

    def test_hex_iv(self):
        iv = SymmetricValidator.validate_iv("DES", "CBC", "hex:0102030405060708")
        self.assertEqual(iv, bytes(range(1, 9)))


if __name__ == "__main__":
    unittest.main()
