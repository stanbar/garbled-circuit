from random import randint, getrandbits 
from hashlib import sha512
from secrets import token_bytes
from math import ceil

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
        return decrypt_hash(index, key_one, key_two, value, kappa)
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
    result = int.from_bytes(key, byteorder='big') ^ int.from_bytes(value, byteorder='big')
    return result.to_bytes(kappa*2, 'big', signed=False)

def encrypt_hash(index: int, key_one: bytes, key_two: bytes, value: bytes, kappa: int) -> bytes:
    key_preimage = index.to_bytes(ceil(index.bit_length()/8), 'big') + key_one + key_two
    key = sha512(key_preimage).digest()[:kappa//8]
    key_int = int.from_bytes(key, byteorder='big')
    result = int.from_bytes(value, byteorder='big') + key_int
    return result.to_bytes(kappa, 'big')

def decrypt_hash(index: int, key_one: bytes, key_two: bytes, value: bytes, kappa: int) -> bytes:
    key_preimage = index.to_bytes(ceil(index.bit_length()/8), 'big') + key_one + key_two
    key = sha512(key_preimage).digest()[:kappa//8]
    key_int = int.from_bytes(key, byteorder='big')
    result = int.from_bytes(value, 'big') - key_int
    return result.to_bytes(kappa, 'big')
