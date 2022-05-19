from algebra import PrimeCyclicGroup 
import hashlib
import utils

# https://crypto.stanford.edu/pbc/notes/crypto/ot.html

class SenderOT():
    def __init__(self, group: PrimeCyclicGroup, msg1: bytes, msg2: bytes):
        self.G = group
        self.msg = (msg1, msg2)
        self.c = group.rand_int()

    def get_c(self) -> int:
        return self.c

    def get_encrypted_messages(self, pub_b: int) -> tuple[int, bytes, bytes]:
        k = self.G.rand_int()
        c1 = self.G.gen_pow(k)
        # k become private key
        # c1 become public key

        # Draw it out and understand
        # k is private 
        # PKb = g ^ k
        # k -> PKb is easy
        # PKb -> k is hard
        # R -> c is hard
        pub_p = self.G.mul(self.c, self.G.inv(pub_b))

        key_0 = self.G.pow(pub_b, k)
        e0 = utils.xor_bytes(self.msg[0], ot_hash(key_0,len(self.msg[0])))

        key_1 = self.G.pow(pub_p, k)
        e1 = utils.xor_bytes(self.msg[1], ot_hash(key_1,len(self.msg[1])))

        return (c1, e0, e1)

class ReceiverOT():
    def __init__(self, group: PrimeCyclicGroup, b: int):
        self.G = group
        self.x = group.rand_int()
        self.b = b

    def get_pub_key(self, c: int) -> int:
        pub_0 = self.G.pow(self.G.generator, self.x) # PK0 = g ^ x
        pub_1 = self.G.mul(c, self.G.inv(pub_0)) # PK1 = c * PK0^-1 = c * g^x^-1 = c * g^-x
        return (pub_0, pub_1)[self.b]

    def decrypt_one_message(self, c1: int, e0: bytes, e1: bytes) -> bytes:
        e = (e0, e1)
        key = self.G.pow(c1, self.x)
        key_hash = ot_hash(key, len(e[self.b]))
        msg_picked = utils.xor_bytes(e[self.b], key_hash)
        return msg_picked




def ot_hash(pub_key, msg_length):
    """Hash function for OT keys."""
    key_length = (pub_key.bit_length() + 7) // 8  # key length in bytes
    bytes = pub_key.to_bytes(key_length, byteorder="big")
    return hashlib.shake_256(bytes).digest(msg_length)

