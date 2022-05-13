from typing import NamedTuple

Id = int
Label = int
PBit = int

class Gate(NamedTuple):
    id: Id
    type: str
    inputs: list[Id]

class Wire(NamedTuple):
    id: Id
    value: int
    label: int
    select_bit: int

class Circuit(NamedTuple):
    name: str
    alice: list[Id]
    bob: list[Id]
    out: list[Id]
    gates: list[Gate]

GateFunctions = {
    'AND': lambda x, y: x and y,
    'OR': lambda x, y: x or y,
    'NOT': lambda x: not x,
    'XOR': lambda x, y: x ^ y,
    'NAND':  lambda x, y: not (x and y),
    'NOR': lambda x, y: not (x or y),
    'XNOR':  lambda x, y: not (x ^ y),
    'GEQ': lambda x, y: x > y,
    'LEQ': lambda x, y: x < y,
}

