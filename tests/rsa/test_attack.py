import unittest

from cipher_labs.core.ciphers.rsa import RSAAttack, RSACipher, RSAKey, build_key, generate_keypair


class TestFactorization(unittest.TestCase):
    def test_wiki_modulus(self):
        self.assertEqual(RSAAttack.factorize(3233), (53, 61))

    def test_generated_moduli(self):
        for bits in (16, 32, 48, 64):
            with self.subTest(bits=bits):
                key = generate_keypair(bits)
                self.assertEqual(RSAAttack.factorize(key.n), (min(key.p, key.q), max(key.p, key.q)))

    def test_prime_modulus_rejected(self):
        with self.assertRaises(ValueError):
            RSAAttack.factorize(7919)

    def test_timeout(self):
        key = generate_keypair(512)
        with self.assertRaises(TimeoutError):
            RSAAttack.factorize(key.n, timeout=0.2)


class TestRecoverPrivateKey(unittest.TestCase):
    def test_wiki_example(self):
        result = RSAAttack.recover_private_key(RSAKey(n=3233, e=17))
        self.assertEqual((result.p, result.q, result.key.d), (53, 61, 2753))
        self.assertEqual(RSACipher("numbers").decrypt("2790", result.key), "65")

    def test_decrypts_intercepted_text(self):
        victim = generate_keypair(64)
        intercepted = RSACipher("text").encrypt("Атака вдалася!", victim)
        result = RSAAttack.recover_private_key(victim.public_key())
        self.assertEqual(result.key.d, victim.d)
        self.assertEqual(RSACipher("text").decrypt(intercepted, result.key), "Атака вдалася!")

    def test_large_key_reports_failure(self):
        with self.assertRaises(ValueError):
            RSAAttack.recover_private_key(generate_keypair(512).public_key(), timeout=0.2)

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            RSAAttack.recover_private_key("17, 3233")

    def test_build_key_matches_attack(self):
        key = build_key(61, 53, 17)
        recovered = RSAAttack.recover_private_key(key.public_key()).key
        self.assertEqual((recovered.n, recovered.e, recovered.d), (key.n, key.e, key.d))


if __name__ == "__main__":
    unittest.main()
