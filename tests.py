import unittest
from utils import gen_label, encode, decode, encrypt, decrypt, flip_coin, encrypt_xor, encrypt_hash, decrypt_hash
from random import getrandbits
from secrets import token_bytes

class TestCircuitGenerator(unittest.TestCase):
    
        def test_encoding_decoding(self):
            kappa = 1
            label = gen_label(kappa)
            for pbit in (0,1):
                encoded = encode(label, pbit, kappa)
                decoded = decode(encoded, kappa)
                self.assertEqual((label, pbit), decoded)

    
        def test_encryption_xor(self):
            kappa = 1
            for value in (1,2):
                value_byte = int.to_bytes(value, kappa+1, 'big')
                label = gen_label(kappa)

                encrypted = encrypt_xor(label, value_byte, kappa)
                decrypted = encrypt_xor(label, encrypted, kappa)
                self.assertEqual(value_byte, decrypted)

        def test_encryption_hash(self):
            kappa = 1
            for value in (1,2):
                value_byte = int.to_bytes(value, kappa+1, 'big')

                label = gen_label(kappa)

                encrypted = encrypt_xor(label, value_byte, kappa)
                decrypted = encrypt_xor(label, encrypted, kappa)
                self.assertEqual(value_byte, decrypted)



        def test_encoding_too_large_key_fails(self):
            kappa = 1
            label = gen_label(kappa*2)
            pbit = 1
            self.assertRaises(AssertionError, encode, label, pbit, kappa)
            label = gen_label(kappa*3)
            self.assertRaises(AssertionError, encode, label, pbit, kappa)
            label = gen_label(kappa*4)
            self.assertRaises(AssertionError, encode, label, pbit, kappa)
    

if __name__ == '__main__':
    unittest.main()
