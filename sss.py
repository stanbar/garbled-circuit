import secrets
import numpy as np
import sympy
import itertools


class SSS:
    """
    This class implements the Shamir Secret Sharing scheme.
    """
    key: int
    prime: int
    no_shares: int
    threshold: int
    coefficients: list[int]
    shares: list[int]

    def __init__(self, key: int, prime: int, no_shares: int, threshold: int, coefficients: list[int] = []):
        self.key = key
        self.prime = prime
        self.no_shares = no_shares
        self.threshold = threshold
        if coefficients:
            self.coefficients = coefficients
        else:
            self.coefficients = self.generate_coefficient()

        self.polynomial = self.coefficients + [self.key]
        self.shares = self.generate_shares()

    def generate_coefficient(self):
        """
        Generate a random coefficients for the polynomial.
        """
        return [secrets.randbelow(self.prime) for _ in range(self.threshold-1)]


    def generate_shares(self):
        shares = []
        for y in range(1, self.no_shares+1):
            shares.append(self.evaluate_polynomial(y))

        return shares

    def evaluate_polynomial(self, y: int):
        """
        Evaluate the polynomial at y.
        """
        return np.polyval(self.polynomial, y) % self.prime

    '''
        The following two functions are used to calculate the inverse modulo p
        of a number (we need it when we calculate the b values, to handle
        the denominator)
        
        Adapted from https://en.wikibooks.org/wiki/Algorithm_Implementation/Mathematics/Extended_Euclidean_algorithm
    '''
    def egcd(self, number1, number2):
        if number1 == 0:
            return (number2, 0, 1)
        else:
            g, y, x = self.egcd(number2 % number1, number1)
            return g, x - (number2 // number1) * y, y

    def modinv(self, number, m):
        g, x, y = self.egcd(number, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m

    def calculate_lagrange_basis_polynomial(self, x: int, x_values: list[int]):

        """
        Calculate the Lagrange basis polynomial for x.
        """
        acc = 1
        for element in x_values:
            if element != x:  # do not multiply the current x in the formula
                acc = acc * element
                if element - x >= 0:
                    inverse = self.modinv(element - x, self.prime)
                else:
                    inverse = self.modinv(self.prime - abs(element - x),
                                          self.prime)  # https://math.stackexchange.com/questions/355066/find-the-inverse-modulo-of-a-number-got-a-negative-result
                acc = acc * inverse
        return acc % self.prime

    def reconstruct_key(self, shares: list[tuple[int,int]]) -> int:
        """

        Reconstruct the key by
        1. calculating the Lagrange basis polynomials
        2. summing the product of basis polynomials with the actual polynomial evaluation i.e. Σ(basis_poly_i * y_i) mod p.


        """
        if len(shares) < self.threshold:
            raise ValueError("Not enough shares to reconstruct key.")
        else:
            x_values = [x for x, _ in shares]
            y_values = [y for _, y in shares]

            k = 0
            for index, x in enumerate(x_values):
                b = self.calculate_lagrange_basis_polynomial(x, x_values)
                k += b * y_values[index]

            return k % self.prime
            


if __name__ == "__main__":
    sss = SSS(20, 101, 6, 3)
    shares = sss.shares
    reconstructed_key = sss.reconstruct_key([(1,44), (2,2), (3,96)])
    assert reconstructed_key == sss.key
    reconstructed_key = sss.reconstruct_key([(4,23), (5,86), (6,83)])
    assert reconstructed_key == sss.key

    sss = SSS(91694388364660, 91994388364979, 5, 3, [4103884901909, 5481390490034])
    assert sss.polynomial == [4103884901909, 5481390490034, 91694388364660]
    assert sss.shares == [9285275391624, 27078320587385, 53079135586964, 87287720390361, 37709686632597]
    reconstructed_key = sss.reconstruct_key([(1, 9285275391624), (2, 27078320587385), (4, 87287720390361)])
    assert reconstructed_key == sss.key





