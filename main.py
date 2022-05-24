from circuit import Circuit, Gate,  Id, Label, PBit
from garbled_circuit import GarbledTable, GarbledCircuit
from utils import decrypt, decode



def evaluate(circuit: Circuit, 
        garbled_tables: dict[Id, GarbledTable], 
        pbits_out: dict[Id, int], 
        a_inputs: dict[Id, tuple[Label, PBit]], 
        b_inputs: dict[Id, tuple[Label, PBit]], 
        encryption_method: str,
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
        msg = decrypt(gate.id, key_a, key_b, encr_msg, encryption_method, kappa)
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
    kappa = 1
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
        garbled_circuit = GarbledCircuit(circuit, "xor", kappa)

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

            result = evaluate(circuit, garbled_tables, pbits_out, a_inputs, b_inputs, "xor", kappa)

            # Format output
            str_bits_a = ' '.join(bits[:len(a_wires)])
            str_bits_b = ' '.join(bits[len(a_wires):])
            str_result = ' '.join([str(result[w]) for w in outputs])


            print(f"  Alice{a_wires} = {str_bits_a} "
                    f"Bob{b_wires} = {str_bits_b}  "
                    f"Outputs{outputs} = {str_result}")
