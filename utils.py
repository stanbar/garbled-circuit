from random import randint, getrandbits

def flip_coin() -> int:
    return randint(0,1)

def gen_label(kappa: int) -> int:
    return getrandbits(kappa-1)

def encode(label:int, pbit:int, kappa: int) -> int:
    assert label.bit_length() <= kappa - 1 # Key must be one bit smaller than kappa because it must fit pbit
    mask = (1 << kappa) - 1  # Mask of kappa 1s
    return (label << 1) & mask | pbit

def decode(value:int|bytes, kappa: int) -> tuple[int,int]:
    if isinstance(value, bytes):
        value = int.from_bytes(value, byteorder='big')

    assert value.bit_length() <= kappa
    return value >> 1, value & 1

def encrypt(key: int, value: bytes | int, kappa: int) -> bytes:
    if isinstance(value, bytes):
        assert len(value) <= kappa//8
        value = int.from_bytes(value, byteorder='big')
    elif isinstance(value,int):
        assert value.bit_length() <= kappa
        value = value


    result = value ^ key
    return int.to_bytes(result, kappa//8, 'big')
