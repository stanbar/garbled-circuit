from utils import gen_label, encode, decode, encrypt, decrypt, flip_coin
from circuit import Circuit, Gate, Id, Label, GateFunctions

# name parameter is for testing purposes
GarbledTable = dict[tuple[int, int], bytes]

class GarbledGate():
    """A representation of a garbled gate. """

    gate_type: str
    encryption_method: str
    kappa: int
    output: int
    pbits: dict[Id, int]
    keys: dict[Id, tuple[bytes,bytes]]
    garbled_table: GarbledTable

    def __init__(self, gate:Gate, 
            pbits: dict[Id, int], 
            keys: dict[Id, tuple[bytes,bytes]], 
            encryption_method: str, 
            kappa: int):
        self.gate_type = gate.type
        self.output = gate.id
        self.inputs = gate.inputs
        self.pbits = pbits
        self.keys = keys
        self.encryption_method = encryption_method
        self.kappa = kappa
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
                msg = encode(key_out, encr_bit_out, self.kappa)

                garbled_table[(encr_bit_a, encr_bit_b)] = encrypt(self.output, key_a, key_b, msg, self.encryption_method, self.kappa)


        self.garbled_table = garbled_table


class GarbledCircuit():
    circuit: Circuit
    wires: list[Id]
    pbits: dict[Id, int]
    keys: dict[Id, tuple[bytes,bytes]]
    garbled_tables: dict[Id, GarbledTable]
    kappa: int
    encryp_method: str

    def __init__(self,circuit: Circuit, encryption_method: str, kappa: int):
        self.circuit = circuit
        self.kappa = kappa
        self.encryption_method = encryption_method

        self.populate_wires()
        self.generate_pbits()
        self.generate_keys()
        self.generate_garbled_tables()

    def populate_wires(self):
        """Populate list of wires' ids in this circuit."""
        wires = set()
        for gate in self.circuit.gates:
            wires.add(gate.id)
            wires.update(set(gate.inputs))
        self.wires = list(wires)
    
    def generate_keys(self):
        """Create pair of keys for each wire value, i.e. 0 and 1."""
        self.keys = {wire_id: (gen_label(self.kappa), gen_label(self.kappa)) for wire_id in self.wires}

    def generate_pbits(self):
        """Create a dict mapping each wire to a random p-bit."""
        self.pbits = {wire_id: flip_coin() for wire_id in self.wires}

    def generate_garbled_tables(self):
        """Create the garbled table of each gate."""
        self.garbled_tables = {gate.id: GarbledGate(gate, self.pbits, self.keys, self.encryption_method, self.kappa).garbled_table for gate in self.circuit.gates}

    def get_pbits_out(self):
        return {wire: self.pbits[wire] for wire in self.circuit.out}

    def get_pbits_alice(self):
        return {wire: self.pbits[wire] for wire in self.circuit.alice}

    def get_pbits_bob(self):
        return {wire: self.pbits[wire] for wire in self.circuit.bob}

    def get_garbled_tables(self):
        return self.garbled_tables


