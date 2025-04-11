from src.isa.instructions.b_instruction import BInstruction
from src.isa.instructions.i_instruction import IInstruction
from src.isa.instructions.instruction import Instruction
from src.isa.instructions.j_instruction import JInstruction
from src.isa.instructions.jr_instruction import JRInstruction
from src.isa.instructions.r_instruction import RInstruction
from src.isa.instructions.s_instruction import SInstruction
from src.isa.instructions.u_instruction import UInstruction
from src.isa.opcode import Opcode

opcode_to_instruction_type = {
    Opcode.LUI: UInstruction,

    Opcode.SW: SInstruction,

    Opcode.LW: IInstruction,
    Opcode.ADDI: IInstruction,

    Opcode.ADD: RInstruction,
    Opcode.SUB: RInstruction,
    Opcode.MUL: RInstruction,
    Opcode.DIV: RInstruction,
    Opcode.REM: RInstruction,
    Opcode.SLL: RInstruction,
    Opcode.SRL: RInstruction,
    Opcode.AND: RInstruction,
    Opcode.XOR: RInstruction,

    Opcode.BEQ: BInstruction,
    Opcode.BNE: BInstruction,
    Opcode.BGT: BInstruction,
    Opcode.BLT: BInstruction,

    Opcode.J: JInstruction,

    Opcode.JR: JRInstruction,

    Opcode.HALT: Instruction,
    Opcode.RINT: Instruction
}
