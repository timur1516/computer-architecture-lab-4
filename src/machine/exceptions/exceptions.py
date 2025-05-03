"""Классы исключений при симуляции"""


class SimulationError(Exception):
    """Абстрактный класс исключение при симуляции"""

    pass


class EmptyInputBufferError(SimulationError):
    """Исключение возникающее при чтении из пустого входного буфера"""

    def __init__(self):
        super().__init__("Input buffer is empty!")


class ReadingFromOutputAddressError(SimulationError):
    """Исключение возникающее при чтении адреса выходного устройства"""

    def __init__(self):
        super().__init__("Reading from output address is forbidden!")


class WritingToInputAddressError(SimulationError):
    """Исключение возникающее при записи по адреса входного устройства"""

    def __init__(self):
        super().__init__("Writing to input address is forbidden!")
