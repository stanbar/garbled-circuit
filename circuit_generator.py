from typing import NamedTuple
from enum import Enum
from random import randint, getrandbits
import pickle

Id = int

class Gate(NamedTuple):
    id: int
    type: str
    inputs: list[int]

class Wire(NamedTuple):
    id: int
    value: int
    label: int
    select_bit: int

GateFunctions = {
    'AND': lambda x, y: x and y,
    'OR': lambda x, y: x or y,
    'NOT': lambda x: ~x,
    'XOR': lambda x, y: x ^ y,
    'NAND':  lambda x, y: ~(x and y),
    'NOR': lambda x, y: ~(x or y),
    'XNOR':  lambda x, y: ~(x ^ y),
    'GEQ': lambda x, y: x >= y,
    'LEQ': lambda x, y: x <= y,
}


def encrypt(key: int, value: bytes | int) -> int:
    if isinstance(value, bytes):
        result = int.from_bytes(value, byteorder='big') ^ key
    elif isinstance(value,int):
        result = value ^ key
    return result


class GarbledGate():
    """A representation of a garbled gate. """

    gate_type: str
    output: int
    pbits: dict[int, int]
    keys: dict[int, tuple[int,int]]
    garbled_table: dict

    def __init__(self, gate:Gate, pbits: dict[int, int], keys: dict[int, tuple[int,int]]):
        self.gate_type = gate.type
        self.output = gate.id
        self.inputs = gate.inputs
        self.pbits = pbits
        self.keys = keys
        self.gen_garbled_table()


    def gen_garbled_table(self):
        """Create the garbled table of a 2-input gate.
        Args:
            operator: The logical function of to the 2-input gate type.
        """
        in_a, in_b, out = self.inputs[0], self.inputs[1], self.output

        garbled_table = dict()
        # For each entry in the garbled table
        for encr_bit_a in (0, 1):
            for encr_bit_b in (0, 1):
                bit_a = encr_bit_a ^ self.pbits[in_a]
                bit_b = encr_bit_b ^ self.pbits[in_b]
                bit_out = int(GateFunctions[self.gate_type](bit_a, bit_b))
                encr_bit_out = bit_out ^ self.pbits[out]
                key_a = self.keys[in_a][bit_a]
                key_b = self.keys[in_b][bit_b]
                key_out = self.keys[out][bit_out]

                msg = pickle.dumps((key_out, encr_bit_out))
                garbled_table[(encr_bit_a, encr_bit_b)] = encrypt(key_a, encrypt(key_b, msg))


        self.garbled_table = garbled_table


        


class GarbledCircuit():
    alice: list[int]
    bob: list[int]
    out: list[int]
    gates: list[Gate]
    wires: list[Id]
    pbits: dict[Id, int]
    keys: dict[Id, tuple[int,int]]
    garbled_tables: dict[int, GarbledGate]

    def __init__(self, alice: list[Id], bob: list[Id], out: list[Id], gates: list[Gate], kappa: int):
        self.alice = alice
        self.bob = bob
        self.out = out
        self.gates = gates

        self.populate_wires()
        self.generate_pbits()
        self.generate_keys(kappa)
        self.generate_garbled_tables()


    def populate_wires(self):
        """Populate list of wires' ids in this circuit."""
        wires = set()
        for gate in self.gates:
            wires.add(gate.id)
            wires.update(set(gate.inputs))
        self.wires = list(wires)

    
    def generate_keys(self, kappa: int):
        """Create pair of keys for each wire value, i.e. 0 and 1."""
        self.keys = {wire_id: (getrandbits(kappa), getrandbits(kappa)) for wire_id in self.wires}

    def generate_pbits(self):
        """Create a dict mapping each wire to a random p-bit."""
        self.pbits = {wire_id: randint(0, 1) for wire_id in self.wires}

    def generate_garbled_tables(self):
        """Create the garbled table of each gate."""
        self.garbled_tables = {gate.id: GarbledGate(gate, self.pbits, self.keys) for gate in self.gates}



one_bit_comparator = GarbledCircuit(alice=[1], bob=[2], out=[3], gates=[Gate(3, "GEQ", [1,2])], kappa=8)

