from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.util.binary import extract_bits


class Instruction:
    """Общий класс инструкции

    Эти инструкции не принимают аргументов, только `opcode`. Например `halt`, `rint`.

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
    "код операции, 7 бит"

    def __init__(self, opcode: Opcode):
        self.opcode = opcode

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
