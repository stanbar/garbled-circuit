import random
from itertools import product

kappa = 8

X = range(0,4)
X_size = len(X)

def encrypt(key: int, value:int):
    return key ^ value



fun_table = [_a > _b for _a, _b in product(X, X)]
print(fun_table)


a_keys = [random.getrandbits(kappa) for _ in range(X_size)]
b_keys = [random.getrandbits(kappa) for _ in range(X_size)]
print(f'Keys_a', a_keys)
print(f'Keys_b', b_keys)

enc_table = [encrypt(b_keys[i], encrypt(a_keys[j], fun_table[X_size*i + j])) for i, j in product(X, X)]
dec_table = [encrypt(b_keys[i],encrypt(a_keys[j], enc_table[X_size*i + j])) for i, j in product(X, X)]

print(enc_table)
print(dec_table)

alice_wealth = random.randint(0, X_size-1)
print(alice_wealth)

bob_wealth = int(input(f"enter value in range 0 to %d: " % (X_size-1)))
print(bob_wealth)

print(fun_table[X_size*bob_wealth + alice_wealth])
