import unittest
from circuit_generator import encode, decode

class TestCircuitGenerator(unittest.TestCase):
    
        def test_encoding_decoding(self):
            kappa = 8
            label = (1 << kappa - 1) - 1 # maximum allowed label
            pbit = 1
            encoded = encode(label, pbit, kappa)
            decoded = decode(encoded, kappa)
            self.assertEqual((label, pbit), decoded)


        def test_encoding_too_large_key_fails(self):
            kappa = 8
            label = 1 << kappa
            pbit = 1
            self.assertRaises(AssertionError, encode, label, pbit, kappa)
            label = (1 << kappa) - 1
            self.assertRaises(AssertionError, encode, label, pbit, kappa)
            label = (1 << kappa - 1)
            self.assertRaises(AssertionError, encode, label, pbit, kappa)
    

if __name__ == '__main__':
    unittest.main()
