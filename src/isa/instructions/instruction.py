from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.util.binary import extract_bits


class Instruction:
    """Общий класс инструкции

    Эти инструкции не принимают аргументов, только `opcode`. Например: `halt`, `rint`.

    Дополнительно каждая инструкция содержит адрес, который записывается в бинарный файл

    Структура инструкции:

    ```plaintext
    ┌────────────────────────────────────────────────────────────┬────────┐
    │                           31...7                           │  6..0  │
    ├────────────────────────────────────────────────────────────┼────────┤
    │                             imm                            │ opcode │
    └────────────────────────────────────────────────────────────┴────────┘
    ```
    """

    opcode = None
    "Код операции, 7 бит"

    address = None
    "Адрес инструкции. B случае если не указывать сразу, инициализируется нулём"

    def __init__(self, opcode: Opcode, address: int = 0):
        self.opcode = opcode
        self.address = address

    def to_binary(self) -> int:
        """Преобразование инструкции в бинарное представление"""
        return opcode_to_binary[self.opcode]

    @staticmethod
    def from_binary(binary: int) -> "Instruction":
        """Получение объекта инструкции из бинарного представления"""
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        return Instruction(opcode)

    def to_json(self) -> dict:
        """Преобразование инструкции в json словарь"""
        return {"opcode": str(self.opcode)}

    def __str__(self) -> str:
        return str(self.opcode)
