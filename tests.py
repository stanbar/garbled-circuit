import unittest
from utils import gen_label, encode, decode, flip_coin, encrypt_xor, encrypt_hash, decrypt_hash, gen_prime, is_prime, xor_bytes
from algebra import PrimeCyclicGroup

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
            for value in (0,1):
                value_byte = int.to_bytes(value, kappa, 'big')+bytes(1)
                label = gen_label(kappa)

                encrypted = encrypt_xor(label, value_byte, kappa)
                decrypted = encrypt_xor(label, encrypted, kappa)
                print(f"XOR value_byte: {value_byte} encrypted: {encrypted} decrypted: {decrypted}")
                self.assertEqual(value_byte, decrypted)

        def test_encryption_hash(self):
            kappa = 1
            for index in range(10):
                for value in (0,1):
                    value_byte = int.to_bytes(value, kappa, 'big') + bytes(1)

                    key_one = gen_label(kappa)
                    key_two = gen_label(kappa)

                    iterations = 10
                    # encrypt x times
                    encrypted = encrypt_hash(index, key_one, key_two, value_byte, kappa)
                    for _ in range(iterations):
                        encrypted = encrypt_hash(index, key_one, key_two, encrypted, kappa)

                    # decrypt x times
                    decrypted = decrypt_hash(index, key_one, key_two, encrypted, kappa)
                    for _ in range(iterations):
                        decrypted = decrypt_hash(index, key_one, key_two, decrypted, kappa)

                    print(f"HASH: value_byte: {value_byte} encrypted: {encrypted} decrypted: {decrypted}")
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
    

class PrimeCyclicGroupTests(unittest.TestCase):

    def test_prime_cyclic_group_operator(self):
        group = PrimeCyclicGroup(5)
        result = group.mul(1, 5)
        self.assertEqual(result, 0)
        result = group.mul(3, 2)
        self.assertEqual(result, 1)
        result = group.pow(2, 3)
        self.assertEqual(result, 3)


    def test_group_generator(self):
        for prime in [i for i in range(20) if is_prime(i)]:
            group = PrimeCyclicGroup(prime)
            
            s = list(range(1, prime))
            generated = dict()
            i = 1
            while s:
                try:
                    x = group.pow(group.generator, i)
                    s.remove(x)
                    generated[x] = f"{group.generator}^{i} % {group.prime} = {x}"
                except ValueError:
                    pass

                i += 1

            # print(json.dumps(generated, indent=4, sort_keys=True))
            self.assertEqual(s, [])




if __name__ == '__main__':
    unittest.main()
