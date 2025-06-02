from enum import Enum


class Opcode(Enum):
    """Opcode инструкций"""

    LUI = "lui"

    LW = "lw"
    ADDI = "addi"

    ADD = "add"
    ADC = "adc"
    SUB = "sub"
    MUL = "mul"
    MULH = "mulh"
    DIV = "div"
    REM = "rem"
    SLL = "sll"
    SRL = "srl"
    AND = "and"
    OR = "or"
    XOR = "xor"

    SW = "sw"
    BEQ = "beq"
    BNE = "bne"
    BGT = "bgt"
    BLT = "blt"

    J = "j"
    JR = "jr"

    HALT = "halt"
    RINT = "rint"
    EINT = "eint"
    DINT = "dint"

    def __str__(self) -> str:
        return self.value


opcode_to_binary = {op: i for i, op in enumerate(Opcode)}
"Вспомогательный словарь, для преобразования opcode в бинарное представление"

binary_to_opcode = {i: op for i, op in enumerate(Opcode)}
"Вспомогательный словарь, для преобразования бинарного представления opcode в объект"
