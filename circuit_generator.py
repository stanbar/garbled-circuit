from typing import NamedTuple
from random import random

Id = int

class Wire(NamedTuple):
    value: int
    label: int
    select_bit: int


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


class Circuit():
    alice: list[int]
    bob: list[int]
    out: list[int]
    gates: list[Gate]
    wires: list[Wire]
    pbits: dict[Wire, int] = {}
    keys: dict[Id, tuple[int,int]] = {}
    garbled_tables: dict[Wire, int] = {}

    def __init__(self, alice: list[int], bob: list[int], out: list[int], gates: list[Gate], kappa: int):
        self.alice = alice
        self.bob = bob
        self.out = out
        self.gates = gates

        self.populate_wires()
        self.generate_pbits()
        self.generate_keys(kappa)


    def populate_wires(self):
        wires = set()
        for gate in self.gates:
            wires.add(gate.id)
            wires.update(set(gate.inputs))
        self.wires = list(wires)

    
    def generate_keys(self, kappa: int):
        self.keys = {id: (random.getrandbits(kappa), random.getrandbits(kappa)) for (id) in self.wires}



    def generate_pbits(self):
        self.pbits = {id: random.randint(0, 1) for (id) in self.wires}

one_bit_comparator = Circuit(alice=[1], bob=[2], out=[3], gates=[Gate(3, "CMP", [1,2])])

