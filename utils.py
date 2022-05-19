from random import randint, getrandbits 
from hashlib import sha512
from secrets import token_bytes, randbits
from math import ceil
import operator

def flip_coin() -> int:
    return randint(0,1)

def gen_label(kappa: int) -> bytes:
    return token_bytes(kappa)

def encode(key:bytes, pbit:int, kappa: int) -> bytes:
    assert len(key) == kappa # Key must be one bit smaller than kappa because it must fit pbit
    assert pbit == 0 or pbit == 1
    # pad pbit with random bits
    
    pbit_padded = (getrandbits(7-1) << 1 | pbit).to_bytes(1, 'big')
    encoded = key + pbit_padded
    assert len(encoded) == kappa + 1
    return encoded

def decode(value:bytes, kappa: int) -> tuple[bytes, int]:
    label = value[:-1]
    assert len(label) == kappa
    pbit = value[-1] & 1

    assert pbit == 1 or pbit == 0
    return label, pbit

def encrypt(index:int, key_one: bytes, key_two: bytes, value: bytes, method: str, kappa: int) -> bytes:
    if method == 'xor':
        return encrypt_xor(key_two, encrypt_xor(key_one, value, kappa), kappa)
    elif method == 'hash':
        return encrypt_hash(index, key_one, key_two, value, kappa)
    else:
        raise Exception('Unknown method')

def decrypt(index:int, key_one: bytes, key_two: bytes, value: bytes, method: str, kappa: int) -> bytes:
    if method == 'xor':
        return encrypt_xor(key_two, encrypt_xor(key_one, value, kappa), kappa)
    elif method == 'hash':
        return encrypt_hash(index, key_one, key_two, value, kappa)
    else:
        raise Exception('Unknown method')

def encrypt_xor(key: bytes, value: bytes, kappa: int) -> bytes:
    assert len(key) == kappa
    assert len(value) == 2*kappa
    # the problem is that if key is kappa then the ciphertext is 2x kappa because of pbit
    key_int = int.from_bytes(key, byteorder='big')

    encrypted_value = int.from_bytes(value[:-1], byteorder='big')
    encrypted_pbit = value[-1]
    result = (key_int ^ encrypted_value) << 8 | (key_int ^ encrypted_pbit)
    return result.to_bytes(kappa+1, 'big')

def derive_key(index: int, key_one: bytes, key_two: bytes, kappa: int) -> int:
    assert len(key_one) == kappa
    assert len(key_two) == kappa
    key_preimage = index.to_bytes(ceil(index.bit_length()/8), 'big') + key_one + key_two
    key = sha512(key_preimage).digest()[:kappa+1]
    key_int = int.from_bytes(key, byteorder='big', signed=False)
    key_int = key_int >> 2
    return key_int 

def encrypt_hash(index: int, key_one: bytes, key_two: bytes, value: bytes, kappa: int) -> bytes:
    key_int = derive_key(index, key_one, key_two, kappa)
    value_int = int.from_bytes(value, byteorder='big')
    result = (value_int + key_int) % 62273
    # Does not work
    # print(f"key = {int(key_int)} value_int = {value_int} len(value) = {len(value)} result bitlen = {result.bit_length()} result = {result}")
    # The value overflows two byte integers
    # Possible solution? introduce modulo
    return result.to_bytes(kappa+1, 'big', signed=False)

def decrypt_hash(index: int, key_one: bytes, key_two: bytes, value: bytes, kappa: int) -> bytes:
    key_int = derive_key(index, key_one, key_two, kappa)
    result = (int.from_bytes(value, 'big') - key_int) % 62273
    # print(f"key = {int(key_int)} len(value) = {len(value)} result bitlen = {result.bit_length()}")
    return result.to_bytes(kappa+1, 'big', signed=False)

def gen_prime(num_bits: int) -> int:
    """Return random prime of bit size 'num_bits'"""
    r = randbits(num_bits)
    return next_prime(r)

def next_prime(n: int) -> int:
    if n % 2 == 0:
        n += 1
    while not is_prime(n):
        n += 2
    return n

def is_prime(n: int) -> bool:
    if n == 2:
        return True
    if n < 2 or n % 2 == 0:
        return False
    for _ in range(3, int(n**0.5)+1, 2):
        if n % _ == 0:
            return False
    return True

def xor_bytes(seq1: bytes, seq2: bytes):
    """XOR two byte sequence."""
    assert len(seq1) == len(seq2)
    return bytes(map(operator.xor, seq1, seq2))

