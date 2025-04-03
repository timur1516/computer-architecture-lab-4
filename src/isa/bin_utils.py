def extract_bits(binary: int, n: int) -> int:
    mask = (1 << n) - 1
    return binary & mask


def binary_to_signed_int(binary: int, n: int) -> int:
    value = extract_bits(binary, n)
    if value & (1 << (n - 1)):
        value -= (1 << n)
    return value


def is_correct_bin_size_signed(binary: int, n: int) -> bool:
    return -(1 << (n - 1)) <= binary < 1 << (n - 1)


def to_bin_word(binary: int) -> tuple[int, int, int, int]:
    return (binary >> 24) & 0xFF, (binary >> 16) & 0xFF, (binary >> 8) & 0xFF, binary & 0xFF
