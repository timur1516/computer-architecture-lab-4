import json
from typing import List

from src.isa.instructions.instruction import Instruction
from src.isa.memory_config import DATA_AREA_START_ADDR
from src.isa.opcode import binary_to_opcode
from src.isa.opcode_to_instruction_map import opcode_to_instruction_type
from src.isa.util.binary import int_to_bin_word, bytes_to_int_array, extract_bits


def to_bytes(code: List[Instruction],
             data: List[int],
             is_interrupts_enabled: bool,
             interrupt_handler_address: int) -> bytes:
    binary_code = bytearray()

    binary_code.extend(int_to_bin_word(int(is_interrupts_enabled)))

    binary_code.extend(int_to_bin_word(interrupt_handler_address))

    data_len = len(data)
    binary_code.extend(int_to_bin_word(data_len))

    for word in data:
        binary_code.extend(int_to_bin_word(word))

    for instr in code:
        binary_instr = instr.to_binary()
        binary_code.extend(int_to_bin_word(binary_instr))

    return bytes(binary_code)


def to_hex(binary_code: bytes) -> str:
    result = []
    data_address = DATA_AREA_START_ADDR
    instruction_address = 0

    word_list = bytes_to_int_array(binary_code)

    is_interrupts_enabled = bool(word_list[0])

    result.append(f'is interrupts enabled: {is_interrupts_enabled}')

    interrupt_handler_address = word_list[1]

    result.append(f'interrupt handler address: {interrupt_handler_address}')

    data_len = word_list[2]

    result.append(f'data')

    for word in word_list[3:data_len + 3]:
        hex_word = f'{word:08X}'
        bin_word = f'{word:032b}'
        line = f'{data_address:3} - {hex_word} - {bin_word}'

        result.append(line)
        data_address += 1

    result.append(f'instructions')

    for word in word_list[data_len + 3:]:
        opcode_bin = extract_bits(word, 7)
        opcode = binary_to_opcode[opcode_bin]

        instruction_type = opcode_to_instruction_type[opcode]
        instruction = instruction_type.from_binary(word)

        hex_word = f'{word:08X}'
        bin_word = f'{word:032b}'
        line = f'{instruction_address:3} - {hex_word} - {bin_word} - {str(instruction)}'

        result.append(line)
        instruction_address += 1

    return "\n".join(result)


def from_bytes(binary_code) -> (List[Instruction], List[int], int, bool):
    instructions = []
    data = []

    word_list = bytes_to_int_array(binary_code)

    is_interrupts_enabled = bool(word_list[0])

    interrupt_handler_address = word_list[1]

    data_len = word_list[2]

    for word in word_list[3:data_len + 3]:
        data.append(word)

    for word in word_list[data_len + 3:]:
        opcode_bin = extract_bits(word, 7)
        opcode = binary_to_opcode[opcode_bin]

        instruction_type = opcode_to_instruction_type[opcode]
        instruction = instruction_type.from_binary(word)

        instructions.append(instruction)

    return instructions, data, interrupt_handler_address, is_interrupts_enabled


def write_json(filename: str,
               code: List[Instruction],
               data_memory: List[int],
               is_interrupts_enabled: bool,
               interrupt_handler_address: int):
    data_address = DATA_AREA_START_ADDR
    instruction_address = 0
    data_buf = []
    instructions_buf = []

    for word in enumerate(data_memory):
        data_buf.append(json.dumps({"address": data_address, "word": word}))
        data_address += 1

    for i, instr in enumerate(code):
        instructions_buf.append(json.dumps({"address": instruction_address, **instr.to_json()}))
        instruction_address += 1

    with open(filename, "w", encoding="utf-8") as file:
        file.write(
            f'''{{
    "is_interrupts_enabled": {str.lower(str(is_interrupts_enabled))},
    "interrupt_handler_address": {interrupt_handler_address},
    "data": [
        {",\n\t\t".join(data_buf)}
    ],
    "instructions": [
        {",\n\t\t".join(instructions_buf)}
    ]
}}''')
