from circuit_generation import generate_circuit, Wire, encrypt, H
import random

class Alice():
    def produce_circuit(self):
        labels_wire_a, labels_wire_b, labels_wire_c, e_table, out_decoding_table = generate_circuit()
        self.labels_wire_a = labels_wire_a
        self.labels_wire_b = labels_wire_b
        self.labels_wire_c = labels_wire_c
        self.e_table = e_table
        self.out_decoding_table = out_decoding_table
        return self.labels_wire_a, self.labels_wire_b, self.labels_wire_c, self.e_table, self.out_decoding_table

    def chose_input(self) -> int:
        return random.choice([0, 1])

    def get_active_label_for_input(self, input: int) -> tuple[int, int]:
        return next((label, select_bit) for (value, label, select_bit) in labels_wire_a if input == value)

    def oblivious_transfer(self, input: int) -> tuple[int, int]:
        return next((label, select_bit) for (value, label, select_bit) in labels_wire_b if input == value)


class Bob():
    e_table: list[int]

    def accept_circuit(self, e_table: list[int], out_decoding_table: list[int]) -> None:
        self.e_table = e_table
        self.out_decoding_table = out_decoding_table


    def evaluate_circuit(self, label_wire_alice, select_bit_alice, label_wire_bob, select_bit_bob) -> int:
        print(f'select_bit_alice: {select_bit_alice}, label_wire_alice: {label_wire_alice}, select_bit_bob: {select_bit_bob}, label_wire_bob: {label_wire_bob}')
        return encrypt(H(label_wire_alice, label_wire_bob), self.e_table[2*select_bit_alice + select_bit_bob])


alice = Alice()
alice_input = alice.chose_input()
labels_wire_a, labels_wire_b, labels_wire_c, e_table, out_decoding_table = alice.produce_circuit()
label_for_alice_input, select_bit_for_alice_input = alice.get_active_label_for_input(alice_input)
print(f'alice chosen label {label_for_alice_input} and select_bit {select_bit_for_alice_input}')

bob = Bob()
bob.accept_circuit(e_table, out_decoding_table)

bob_input = int(input(f"enter value in range 0 to 1:"))
label_for_bob_input, select_bit_for_bob_input = alice.oblivious_transfer(bob_input)

value = bob.evaluate_circuit(label_for_alice_input, select_bit_for_alice_input, label_for_bob_input, select_bit_for_bob_input)
print(value)
