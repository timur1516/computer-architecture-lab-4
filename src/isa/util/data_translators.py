from __future__ import annotations

import json

from src.isa.data import Data
from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import binary_to_opcode
from src.isa.opcode_to_instruction_map import opcode_to_instruction_type
from src.isa.util.binary import bytes_to_int_array, extract_bits, int_to_bin_word

"""Функции, выполняющие преобразование между различными формами представления инструкций и данных"""


def to_bytes_instructions(instructions: list[Instruction]):
    """Преобразование набора инструкцию в массив байт

    Сначала записывается адрес, затем инструкция
    """

    binary_code = bytearray()

    for instr in instructions:
        binary_code.extend(int_to_bin_word(instr.address))
        binary_code.extend(int_to_bin_word(instr.to_binary()))

    return bytes(binary_code)


def to_bytes_data(data: list[Data]) -> bytes:
    """Преобразование данных в массив байт

    Сначала записывается адрес, затем значение
    """

    binary_code = bytearray()

    for element in data:
        binary_code.extend(int_to_bin_word(element.address))
        binary_code.extend(int_to_bin_word(element.value))

    return bytes(binary_code)


def to_hex_data(binary_data: bytes) -> str:
    """Преобразование бинарного представление данных в шестнадцатеричное представление"""

    result = []
    word_list = bytes_to_int_array(binary_data)

    for i in range(0, len(word_list) - 1, 2):
        address = word_list[i]
        word = word_list[i + 1]

        hex_word = f"{word:08X}"
        bin_word = f"{word:032b}"
        line = f"{address:3} - {hex_word} - {bin_word}"

        result.append(line)

    return "\n".join(result)


def to_hex_instructions(binary_instructions: bytes) -> str:
    """Преобразование бинарного представление инструкций в шестнадцатеричное представление"""

    result = []
    word_list = bytes_to_int_array(binary_instructions)

    for i in range(0, len(word_list) - 1, 2):
        address = word_list[i]
        word = word_list[i + 1]

        opcode_bin = extract_bits(word, 7)
        opcode = binary_to_opcode[opcode_bin]

        instruction_type = opcode_to_instruction_type[opcode]
        instruction = instruction_type.from_binary(word)

        hex_word = f"{word:08X}"
        bin_word = f"{word:032b}"
        line = f"{address:3} - {hex_word} - {bin_word} - {instruction!s}"

        result.append(line)

    return "\n".join(result)


def from_bytes_data(binary_data: bytes) -> list[Data]:
    """Преобразование бинарного представление данных в структурированный формат"""

    data = []
    word_list = bytes_to_int_array(binary_data)

    for i in range(0, len(word_list) - 1, 2):
        address = word_list[i]
        value = word_list[i + 1]

        data.append(Data(value, address))

    return data


def from_bytes_instructions(binary_instructions: bytes) -> list[Instruction]:
    """Преобразование бинарного представление инструкций в структурированный формат"""

    instructions = []
    word_list = bytes_to_int_array(binary_instructions)

    for i in range(0, len(word_list) - 1, 2):
        address = word_list[i]
        word = word_list[i + 1]

        opcode_bin = extract_bits(word, 7)
        opcode = binary_to_opcode[opcode_bin]

        instruction_type = opcode_to_instruction_type[opcode]
        instruction = instruction_type.from_binary(word)
        instruction.address = address

        instructions.append(instruction)

    return instructions


def to_json_data(data: list[Data]) -> str:
    """Преобразование данных в json строку"""

    return f'[{",\n".join([json.dumps({"address": element.address, "value": element.value}) for element in data])}]'


def to_json_instructions(instructions: list[Instruction]) -> str:
    """Преобразование инструкций в json строку"""

    return f'[{",\n".join([json.dumps(instr.to_json()) for instr in instructions])}]'
