import math
import unittest

from cipher_labs.core.ciphers.rsa import RSAKey, build_key, generate_keypair, parse_public_key
from cipher_labs.core.ciphers.rsa.numtheory import generate_prime, is_probable_prime, mod_inverse


class TestNumberTheory(unittest.TestCase):
    def test_primality(self):
        primes = (2, 3, 5, 61, 53, 7919, 2_147_483_647, 2 ** 61 - 1, 2 ** 127 - 1)
        composites = (0, 1, 4, 3233, 561, 1105, 2 ** 32 + 1, 2 ** 61 + 1, (2 ** 61 - 1) * (2 ** 31 - 1))
        for p in primes:
            with self.subTest(prime=p):
                self.assertTrue(is_probable_prime(p))
        for c in composites:
            with self.subTest(composite=c):
                self.assertFalse(is_probable_prime(c))

    def test_generate_prime_has_exact_bits(self):
        for bits in (8, 16, 64, 256):
            with self.subTest(bits=bits):
                p = generate_prime(bits)
                self.assertEqual(p.bit_length(), bits)
                self.assertTrue(is_probable_prime(p))

    def test_mod_inverse(self):
        self.assertEqual(mod_inverse(17, 3120), 2753)
        self.assertEqual(17 * mod_inverse(17, 3120) % 3120, 1)
        with self.assertRaises(ValueError):
            mod_inverse(6, 3120)


class TestKeyGeneration(unittest.TestCase):
    def test_generated_key_is_consistent(self):
        for bits in (16, 64, 512, 1024):
            with self.subTest(bits=bits):
                key = generate_keypair(bits)
                self.assertEqual(key.bits, bits)
                self.assertEqual(key.n, key.p * key.q)
                self.assertNotEqual(key.p, key.q)
                self.assertEqual(math.gcd(key.e, key.phi), 1)
                self.assertEqual(key.e * key.d % key.phi, 1)
                self.assertEqual(pow(pow(42, key.e, key.n), key.d, key.n), 42)

    def test_default_exponent_is_65537(self):
        self.assertEqual(generate_keypair(512).e, 65537)

    def test_small_key_falls_back_to_smaller_exponent(self):
        key = generate_keypair(16)
        self.assertLess(key.e, key.phi)

    def test_custom_exponent(self):
        self.assertEqual(generate_keypair(256, e=3).e, 3)

    def test_keys_are_random(self):
        self.assertNotEqual(generate_keypair(256).n, generate_keypair(256).n)

    def test_build_key_from_components(self):
        key = build_key("61", "53", "17")
        self.assertEqual((key.n, key.e, key.d), (3233, 17, 2753))
        self.assertEqual(key.public_str(), "17, 3233")
        self.assertEqual(key.private_str(), "2753, 3233")

    def test_public_key_strips_private_part(self):
        public = build_key(61, 53, 17).public_key()
        self.assertFalse(public.has_private)
        self.assertIsNone(public.phi)

    def test_parse_public_key(self):
        for text in ("17, 3233", "(17, 3233)", "17 3233", " 17;3233 "):
            with self.subTest(text=text):
                self.assertEqual(parse_public_key(text), RSAKey(n=3233, e=17))


class TestXmlExport(unittest.TestCase):
    def test_public_xml_roundtrip(self):
        key = generate_keypair(512)
        xml = key.to_xml(include_private=False)
        self.assertIn("<Modulus>", xml)
        self.assertNotIn("<D>", xml)
        restored = RSAKey.from_xml(xml)
        self.assertEqual(restored, key.public_key())

    def test_private_xml_roundtrip(self):
        key = generate_keypair(512)
        xml = key.to_xml(include_private=True)
        for tag in ("<P>", "<Q>", "<DP>", "<DQ>", "<InverseQ>", "<D>"):
            self.assertIn(tag, xml)
        self.assertEqual(RSAKey.from_xml(xml), key)

    def test_wiki_public_xml(self):
        # 3233 = 0x0CA1 -> "DKE=", 17 = 0x11 -> "EQ=="
        xml = build_key(61, 53, 17).to_xml()
        self.assertEqual(xml, "<RSAKeyValue><Modulus>DKE=</Modulus><Exponent>EQ==</Exponent></RSAKeyValue>")

    def test_invalid_xml(self):
        for bad in ("", "not xml", "<Other/>", "<RSAKeyValue><Modulus>DKE=</Modulus></RSAKeyValue>",
                    "<RSAKeyValue><Modulus>!!</Modulus><Exponent>EQ==</Exponent></RSAKeyValue>"):
            with self.subTest(xml=bad):
                with self.assertRaises(ValueError):
                    RSAKey.from_xml(bad)

    def test_private_export_requires_private_key(self):
        with self.assertRaises(ValueError):
            build_key(61, 53, 17).public_key().to_xml(include_private=True)


if __name__ == "__main__":
    unittest.main()
