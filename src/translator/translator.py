from __future__ import annotations

import os
import sys

from src.isa.data import Data
from src.isa.instructions.instruction import Instruction
from src.isa.util.data_translators import (
    to_bytes_data,
    to_bytes_instructions,
    to_hex_data,
    to_hex_instructions,
    to_json_data,
    to_json_instructions,
)
from src.translator.code_generator.code_generator import CodeGenerator
from src.translator.lexer.lexer import Lexer
from src.translator.parser.parser import Parser
from src.translator.preprocessor.include_preprocessor import IncludePreprocessor


def translate(text: str, src_file: str) -> (list[Instruction], list[Data]):
    """Основная функция трансляции

    Выполняет инициализацию препроцессора, лексера, парсера и генератора машинного кода, и их использование

    На выходе даёт массив инструкций, блок данных и информацию о прерываниях
    """
    text = IncludePreprocessor(text, src_file).preprocess()
    lexer = Lexer(text)
    parser = Parser(lexer)
    tree, symbol_table, literals = parser.parse()
    code_generator = CodeGenerator(tree, symbol_table, literals)
    program, data = code_generator.translate()

    return program, data


def main(src_file: str, instructions_file: str, data_file: str):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""

    with open(src_file, encoding="utf-8") as f:
        src = f.read()

    instructions, data = translate(src, src_file)

    binary_instructions = to_bytes_instructions(instructions)
    binary_data = to_bytes_data(data)

    hex_instructions = to_hex_instructions(binary_instructions)
    hex_data = to_hex_data(binary_data)

    os.makedirs(os.path.dirname(os.path.abspath(instructions_file)) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(data_file)) or ".", exist_ok=True)

    if instructions_file.endswith(".bin"):
        with open(instructions_file, "wb") as f:
            f.write(binary_instructions)

        with open(data_file, "wb") as f:
            f.write(binary_data)

        with open(instructions_file + ".hex", "w") as f:
            f.write(hex_instructions)

        with open(data_file + ".hex", "w") as f:
            f.write(hex_data)
    else:
        json_instructions = to_json_instructions(instructions)
        json_data = to_json_data(data)

        with open(instructions_file, "w") as f:
            f.write(json_instructions)

        with open(data_file, "w") as f:
            f.write(json_data)

    print("source LoC:", len(src.split("\n")), "code instr:", len(instructions))


if __name__ == "__main__":
    assert (
        len(sys.argv) == 4
    ), "Wrong arguments: translator.py <input_file> <target_instructions_file> <target_data_file>"
    _, source, target_instructions_file, target_data_file = sys.argv
    main(source, target_instructions_file, target_data_file)
