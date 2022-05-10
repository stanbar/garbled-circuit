import hashlib
from typing import NamedTuple
import random
from itertools import product

kappa = 8
X = [0,1]
X_size = len(X)

def encrypt(key: bytes, value:int):
    return int.from_bytes(key, byteorder="big") ^ value


fun_table = [_a > _b for _a, _b in product(X, X)]
print(fun_table)

class Gate(NamedTuple):
    id: int
    type: str
    inputs: list[int]

class Wire(NamedTuple):
    value: int
    label: int
    select_bit: int

class Circuit(NamedTuple):
    alice: list[int]
    bob: list[int]
    out: list[int]
    gates: list[Gate]

one_bit_comparator = Circuit(alice=[1], bob=[2], out=[3], gates=[Gate(3, "CMP", [1,2])])


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

H = lambda x,y: hashlib.sha256((str(x) + str(y)).encode()).digest()

e_table = [
        encrypt(H(wire_a.label,wire_b.label), functionality(wire_a.value,wire_b.value)) for wire_a, wire_b in product(sorted_labels_wire_a,sorted_labels_wire_b)
        ]

print(f'e_table {e_table}')

out_decoding_table = [
        encrypt(H(wire_c.label, "out")[:1], wire_c.value) for wire_c in sorted_labels_wire_c
        ]

print(f'out_decoding_table {out_decoding_table}')

dec_table = [
        encrypt(
            H(wire_a.label,wire_b.label), 
            e_table[len(X)*wire_a.select_bit + wire_b.select_bit]
            ) for wire_a, wire_b in product(sorted_labels_wire_a,sorted_labels_wire_b) 
        ]

print(dec_table)

alice_wealth = random.randint(0, X_size-1)
print(alice_wealth)

bob_wealth = int(input(f"enter value in range 0 to %d: " % (X_size-1)))
print(bob_wealth)

print(fun_table[X_size*bob_wealth + alice_wealth])
