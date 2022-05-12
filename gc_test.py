from circuit_generator import encrypt
from random import getrandbits

kappa = 16
key = getrandbits(kappa)
init_value_bytes = getrandbits(kappa).to_bytes(kappa//8, 'big')
init_value = int.from_bytes(init_value_bytes, 'big')

encrypted = encrypt(key,init_value_bytes,kappa)
print(f"Encrypted value: {encrypted}")
encrypted_int = int.from_bytes(encrypted, byteorder='big')
decrypted_bytes = encrypt(key, encrypted, kappa)

assert decrypted_bytes == init_value_bytes
decrypted_int = int.from_bytes(decrypted_bytes, byteorder='big')

assert decrypted_int == init_value
print("Test passed")
