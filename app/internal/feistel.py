import struct
import hashlib

MASK_32 = 0xFFFFFFFF
MASK_16 = 0xFFFF


def _round_function(value: int, key: bytes, round_no: int) -> int:
    data = struct.pack(">H", value) + key + bytes([round_no])
    digest = hashlib.blake2s(data, digest_size=2).digest()
    return struct.unpack(">H", digest)[0]


def feistel_encrypt(x: int, key: bytes, rounds: int = 4) -> int:
    left = (x >> 16) & MASK_16
    right = x & MASK_16

    for r in range(rounds):
        new_left = right
        new_right = left ^ _round_function(right, key, r)
        left, right = new_left, new_right

    return ((left << 16) | right) & MASK_32


def feistel_decrypt(x: int, key: bytes, rounds: int = 4) -> int:
    left = (x >> 16) & MASK_16
    right = x & MASK_16

    for r in reversed(range(rounds)):
        new_right = left
        new_left = right ^ _round_function(left, key, r)
        left, right = new_left, new_right

    return ((left << 16) | right) & MASK_32
