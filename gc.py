import hashlib
from typing import NamedTuple
import random
from itertools import product

kappa = 8
X = [0,1]
X_size = len(X)

def encrypt(key: int, value:int):
    return key ^ value


fun_table = [_a > _b for _a, _b in product(X, X)]
print(fun_table)


class Wire(NamedTuple):
    value: int
    label: int
    select_bit: int

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

H = lambda x,y: int.from_bytes(hashlib.sha256((str(x) + str(y)).encode()).digest(), byteorder="big")

e_table = [
        encrypt(H(labels_wire_a[value_a].label,labels_wire_b[value_b].label), functionality(value_a,value_b)) for value_a, value_b in product(X,X) 
        ]

print(e_table)

dec_table = [
        encrypt(
            H(labels_wire_a[value_a].label,labels_wire_b[value_b].label), 
            e_table[len(X)*value_a + value_b]
            ) for value_a, value_b in product(X,X) 
        ]

print(dec_table)

alice_wealth = random.randint(0, X_size-1)
print(alice_wealth)

bob_wealth = int(input(f"enter value in range 0 to %d: " % (X_size-1)))
print(bob_wealth)

print(fun_table[X_size*bob_wealth + alice_wealth])
