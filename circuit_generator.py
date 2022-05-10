from typing import NamedTuple
from random import random

class Gate(NamedTuple):
    id: int
    type: str
    inputs: list[int]

    def __init__(self, id, type, inputs):
        operator = {
                'GEQ': lambda x: x[0] > x[1],
                'LEQ': lambda x: x[0] < x[1],
                'AND': lambda x: x[0] and x[1],
                'OR': lambda x: x[0] or x[1],
                'XOR': lambda x: x[0] ^ x[1],
                'NOT': lambda x: ~x[0],
                'NONE': lambda x: x[0]
        }[type]
        self.create_garbled_table(operator)

    def create_garbled_table(self, operator):
        out = operator(self.inputs)



class Wire(NamedTuple):
    value: int
    label: int
    select_bit: int

class Circuit():
    alice: list[int]
    bob: list[int]
    out: list[int]
    gates: list[Gate]
    wires: set[Wire]
    pbits: dict[Wire, int]

    def __init__(self, alice, bob, out, gates):
        self.generate_pbits()


    def generate_pbits(self):
        self.pbits = {wire: random.randint(0, 1) for wire in self.wires}

one_bit_comparator = Circuit(alice=[1], bob=[2], out=[3], gates=[Gate(3, "CMP", [1,2])])

