from utils import gen_prime, randint
import numpy as np
import sympy

PRIME_BITS=64

class PrimeCyclicGroup:
    """Cyclic abelian group of prime order 'prime'."""
    def __init__(self, prime=None):
        self.prime = prime or gen_prime(num_bits=PRIME_BITS)
        self.prime_m1 = self.prime - 1
        self.prime_m2 = self.prime - 2
        self.generator = self.find_generator()


    def add(self, a:int, b:int):
        "Add two elements." ""
        return (a + b) % self.prime

    def mul(self, a:int, b:int):
        "Multiply two elements." ""
        return (a * b) % self.prime

    def pow(self, base:int, exp:int):
        "Compute nth power of an element." ""
        return pow(base, exp, self.prime)

    def gen_pow(self, exponent):  # generator exponentiation
        "Compute nth power of a generator." ""
        return pow(self.generator, exponent, self.prime)

    def inv(self, a:int):
        "Compute multiplicative inverse of an element." ""
        if a < 0:
            return pow(self.prime - a, self.prime_m2, self.prime)
        else:
            return pow(a, self.prime_m2, self.prime)


    def polyeval(self,polynomial: list[int],  y: int):
        return np.polyval(polynomial, y) % self.prime

    def rand_int(self):  # random int in [1, prime-1]
        "Return an random int in [1, prime - 1]." ""
        return randint(1, self.prime_m1)

    def find_generator(self) -> int:  # find random generator for group
        """Find a random generator for the group."""
        factors = sympy.primefactors(self.prime_m1)

        while True:
            candidate = self.rand_int()
            for factor in factors:
                if 1 == self.pow(candidate, self.prime_m1 // factor):
                    break
            else:
                return candidate
    
