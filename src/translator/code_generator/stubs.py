from src.isa.opcode_ import Opcode
from src.isa.register import Register

"""Здесь содержаться описания заглушек, используемых в ходе генерации инструкций"""


class Stub:
    """Базовый класс для заглушек"""

    address = None
    "Адрес заглушки. По умолчанию 0"

    size = None
    "To количество инструкций которое будет занимать заглушка после замены"

    def __init__(self, size, address: int = 0):
        self.size = size
        self.address = address


class LabelStub(Stub):
    """Заглушка-метка. Используется при генерации блоков условных переходов и циклов"""

    def __init__(self):
        super().__init__(0)


class BranchStub(Stub):
    """Заглушка для инструкций условного перехода"""

    opcode = None
    "Код операции, 7 бит"

    rs1 = None
    "Код регистра первого операнда, 5 бит"

    rs2 = None
    "Код регистра второго операнда, 5 бит"

    label = None
    "Метка на которую выполняется переход"

    address = None
    "Адрес заглушки. По умолчанию 0"

    def __init__(self, opcode: Opcode, rs1: Register, rs2: Register, label: LabelStub):
        super().__init__(1)
        self.opcode = opcode
        self.rs1 = rs1
        self.rs2 = rs2
        self.label = label


class JumpStub(Stub):
    """Заглушка для инструкции безусловного перехода"""

    label = None
    "Метка на которую выполняется переход"

    def __init__(self, label: LabelStub):
        super().__init__(1)
        self.label = label
