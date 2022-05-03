import hashlib
from typing import NamedTuple
import random
from itertools import product

kappa = 8
X = [0,1]
X_size = len(X)

def encrypt(key: bytes, value:int):
    return int.from_bytes(key, byteorder="big") ^ value

def H(x,y): 
    return hashlib.sha256((str(x) + str(y)).encode()).digest()

class Wire(NamedTuple):
    value: int
    label: int
    select_bit: int

def generate_circuit():
    s = random.choice([0,1])
    labels_wire_a = [
            Wire(0, random.getrandbits(kappa), s), 
            Wire(1, random.getrandbits(kappa), 1-s), 
            ]
    sorted_labels_wire_a = sorted(labels_wire_a, key=lambda x: x.select_bit)

    s = random.choice([0,1])
    labels_wire_b = [
            Wire(0, random.getrandbits(kappa), s), 
            Wire(1, random.getrandbits(kappa), 1-s), 
            ]
    sorted_labels_wire_b = sorted(labels_wire_b, key=lambda x: x.select_bit)

    s = random.choice([0,1])
    labels_wire_c = [
            Wire(0, random.getrandbits(kappa), s), 
            Wire(1, random.getrandbits(kappa), 1-s), 
            ]
    sorted_labels_wire_c = sorted(labels_wire_c, key=lambda x: x.select_bit)

    print(f'labels_a', labels_wire_a)
    print(f'labels_b', labels_wire_b)
    print(f'labels_c', labels_wire_c)

    functionality = lambda a,b : int(a > b)


    e_table = [
            encrypt(H(wire_a.label,wire_b.label), functionality(wire_a.value,wire_b.value)) for wire_a, wire_b in product(sorted_labels_wire_a,sorted_labels_wire_b)
            ]

    print(f'e_table {e_table}')

    out_decoding_table = [
            encrypt(H(wire_c.label, "out"), wire_c.value) for wire_c in sorted_labels_wire_c
            ]

    print(f'out_decoding_table {out_decoding_table}')

    dec_table = [
            encrypt(
                H(wire_a.label,wire_b.label), 
                e_table[len(X)*wire_a.select_bit + wire_b.select_bit]
                ) for wire_a, wire_b in product(sorted_labels_wire_a,sorted_labels_wire_b) 
            ]


    print(f'dec_table: {dec_table}')

    alice_wealth = random.randint(0, X_size-1)
    print(alice_wealth)

    return (
            labels_wire_a,
            labels_wire_b,
            labels_wire_c,
            e_table,
            out_decoding_table,
            )

