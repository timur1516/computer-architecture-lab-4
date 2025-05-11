from enum import Enum


class Register(Enum):
    """Регистры процессора"""

    T0 = "t0"
    T1 = "t1"
    T2 = "t2"
    T3 = "t3"
    SP = "sp"
    ZERO = "zero"

    def __str__(self) -> str:
        return self.value


register_to_binary = {rg: i + 1 for i, rg in enumerate(Register)}
"Вспомогательный словарь, для преобразования объектов регистров в бинарное представление"

binary_to_register = {i + 1: rg for i, rg in enumerate(Register)}
"Вспомогательный словарь, для преобразования бинарное представление регистров в объекты"
