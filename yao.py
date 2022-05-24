from circuit import Circuit, Id, Label
from garbled_circuit import GarbledTable
from utils import decrypt, decode


def evaluate(circuit: Circuit, 
        garbled_tables: dict[Id, GarbledTable], 
        pbits_out: dict[Id, int], 
        a_inputs: dict[Id, tuple[Label, int]], 
        b_inputs: dict[Id, tuple[Label, int]], 
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

