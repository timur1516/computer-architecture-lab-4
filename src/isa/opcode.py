from enum import Enum


class Opcode(Enum):
    LUI = 'lui'

    SW = 'sw'
    LW = 'lw'

    ADDI = 'addi'

    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    DIV = 'div'
    REM = 'rem'
    SLL = 'sll'
    SRL = 'srl'
    AND = 'and'
    OR = 'or'
    XOR = 'xor'

    BEQ = 'beq'
    BNE = 'bne'
    BGT = 'bgt'
    BLT = 'blt'

    J = 'j'
    JR = 'jr'

    HALT = 'halt'
    RINT = 'rint'

    def __str__(self) -> str:
        return self.value


opcode_to_binary = {op: i + 1 for i, op in enumerate(Opcode)}
binary_to_opcode = {i + 1: op for i, op in enumerate(Opcode)}
