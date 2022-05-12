from typing import NamedTuple
from utils import gen_label, encode, decode, encrypt, flip_coin

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


# name parameter is for testing purposes
GarbledTable = dict[tuple[int, int], bytes]

class GarbledGate():
    """A representation of a garbled gate. """

    gate_type: str
    output: int
    pbits: dict[Id, int]
    keys: dict[Id, tuple[int,int]]
    garbled_table: GarbledTable

    def __init__(self, gate:Gate, pbits: dict[Id, int], keys: dict[Id, tuple[int,int]], kappa: int):
        self.gate_type = gate.type
        self.output = gate.id
        self.inputs = gate.inputs
        self.pbits = pbits
        self.keys = keys
        self.gen_garbled_table(kappa)


    def gen_garbled_table(self, kappa: int):
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

                msg = encode(key_out, encr_bit_out, kappa)

                garbled_table[(encr_bit_a, encr_bit_b)] = encrypt(key_a, encrypt(key_b, msg, kappa), kappa)


        self.garbled_table = garbled_table


class GarbledCircuit():
    circuit: Circuit
    wires: list[Id]
    pbits: dict[Id, int]
    keys: dict[Id, tuple[int,int]]
    garbled_tables: dict[Id, GarbledTable]

    def __init__(self,circuit: Circuit, kappa: int):
        self.circuit = circuit

        self.populate_wires()
        self.generate_pbits()
        self.generate_keys(kappa)
        self.generate_garbled_tables(kappa)

    def populate_wires(self):
        """Populate list of wires' ids in this circuit."""
        wires = set()
        for gate in self.circuit.gates:
            wires.add(gate.id)
            wires.update(set(gate.inputs))
        self.wires = list(wires)
    
    def generate_keys(self, kappa: int):
        """Create pair of keys for each wire value, i.e. 0 and 1."""
        self.keys = {wire_id: (gen_label(kappa), gen_label(kappa)) for wire_id in self.wires}

    def generate_pbits(self):
        """Create a dict mapping each wire to a random p-bit."""
        self.pbits = {wire_id: flip_coin() for wire_id in self.wires}

    def generate_garbled_tables(self, kappa):
        """Create the garbled table of each gate."""
        self.garbled_tables = {gate.id: GarbledGate(gate, self.pbits, self.keys, kappa).garbled_table for gate in self.circuit.gates}

    def get_pbits_out(self):
        return {wire: self.pbits[wire] for wire in self.circuit.out}

    def get_pbits_alice(self):
        return {wire: self.pbits[wire] for wire in self.circuit.alice}

    def get_pbits_bob(self):
        return {wire: self.pbits[wire] for wire in self.circuit.bob}

    def get_garbled_tables(self):
        return self.garbled_tables


def evaluate(circuit: Circuit, 
        garbled_tables: dict[Id, GarbledTable], 
        pbits_out: dict[Id, int], 
        a_inputs: dict[Id, tuple[Label, int]], 
        b_inputs: dict[Id, tuple[Label, int]], 
        kappa: int):
    """Evaluate yao circuit with given inputs.
    Args:
        circuit: A dict containing circuit spec.
        g_tables: The yao circuit garbled tables.
        pbits_out: The pbits of outputs.
        a_inputs: A dict mapping Alice's wires to (key, encr_bit) inputs.
        b_inputs: A dict mapping Bob's wires to (key, encr_bit) inputs.
    Returns:
        A dict mapping output wires with their result bit.
    """
    gates = circuit.gates  # dict containing circuit gates
    wire_outputs = circuit.out  # list of output wires
    wire_inputs = {}  # dict containing Alice and Bob inputs
    evaluation = {}  # dict containing result of evaluation

    wire_inputs.update(a_inputs)
    wire_inputs.update(b_inputs)

    # Iterate over all gates
    for gate in sorted(gates, key=lambda g: g.id):
        gate_id, gate_in, msg = gate.id, gate.inputs, None
        # Special case if it's a NOT gate
        key_a, encr_bit_a = wire_inputs[gate_in[0]]
        key_b, encr_bit_b = wire_inputs[gate_in[1]]
        encr_msg = garbled_tables[gate_id][(encr_bit_a, encr_bit_b)]
        msg = encrypt(key_b, encrypt(key_a, encr_msg, kappa), kappa)
        if msg:
            pickled = decode(msg, kappa)
            wire_inputs[gate_id] = pickled

    # After all gates have been evaluated, we populate the dict of results
    for out in wire_outputs:
        wire_input = wire_inputs[out][1]
        pbit_out = pbits_out[out]
        evaluation[out] = wire_input ^ pbit_out

    return evaluation


if __name__ == "__main__":
    kappa = 8
    circuits = [
        Circuit(name="XOR", alice=[1], bob=[2], out=[3], gates=[Gate(3, "XOR", [1,2])]),
        Circuit(name="AND", alice=[1], bob=[2], out=[3], gates=[Gate(3, "AND", [1,2])]),
        Circuit(name="GEQ", alice=[1], bob=[2], out=[3], gates=[Gate(3, "GEQ", [1,2])]),
        Circuit(name="LEQ", alice=[1], bob=[2], out=[3], gates=[Gate(3, "LEQ", [1,2])]),
        Circuit(name="LEQ", alice=[1], bob=[2], out=[3], gates=[Gate(3, "NAND", [1,2])]),
        Circuit(name="MILLIONERE", alice=[1,2], bob=[3,4], out=[13], gates=[
            Gate(5, "NAND", [3,4]),
            Gate(6, "AND", [1,5]),
            Gate(7, "AND", [1,2]),
            Gate(8, "NAND", [3,3]),
            Gate(9, "NAND", [4,4]),
            Gate(10, "OR", [2,9]),
            Gate(11, "AND", [8,10]),
            Gate(12, "OR", [6,7]),
            Gate(13, "OR", [11,12]),
        ])
    ]
    for circuit in circuits:
        garbled_circuit = GarbledCircuit(circuit, kappa)

        garbled_tables = garbled_circuit.get_garbled_tables()
        pbits_out = garbled_circuit.get_pbits_out()
        pbits = garbled_circuit.pbits

        a_wires = circuit.alice
        b_wires = circuit.bob
        keys = garbled_circuit.keys
        outputs = circuit.out


        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_inputs = {}  # map from Bob's wires to (key, encr_bit) inputs
        pbits_out = {w: pbits[w] for w in outputs}  # p-bits of outputs
        N = len(a_wires) + len(b_wires)


        print(f"============ {circuit.name} ============")
        # Generate all possible inputs for both Alice and Bob
        for bits in [format(n, 'b').zfill(N) for n in range(2**N)]:
            bits_a = [int(b) for b in bits[:len(a_wires)]]  # Alice's inputs
            bits_b = [int(b) for b in bits[N - len(b_wires):]]  # Bob's inputs

            # Map Alice's wires to (key, encr_bit)
            for i in range(len(a_wires)):
                a_inputs[a_wires[i]] = (keys[a_wires[i]][bits_a[i]],
                                        pbits[a_wires[i]] ^ bits_a[i])

            # Map Bob's wires to (key, encr_bit)
            for i in range(len(b_wires)):
                b_inputs[b_wires[i]] = (keys[b_wires[i]][bits_b[i]],
                                        pbits[b_wires[i]] ^ bits_b[i])

            result = evaluate(circuit, garbled_tables, pbits_out, a_inputs, b_inputs, kappa)

            # Format output
            str_bits_a = ' '.join(bits[:len(a_wires)])
            str_bits_b = ' '.join(bits[len(a_wires):])
            str_result = ' '.join([str(result[w]) for w in outputs])


            print(f"  Alice{a_wires} = {str_bits_a} "
                    f"Bob{b_wires} = {str_bits_b}  "
                    f"Outputs{outputs} = {str_result}")
