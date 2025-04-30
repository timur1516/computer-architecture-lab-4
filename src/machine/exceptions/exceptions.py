class SimulationError(Exception):
    pass


class EmptyInputBufferError(SimulationError):
    def __init__(self):
        super().__init__("Input buffer is empty!")


class ReadingFromOutputAddressError(SimulationError):
    def __init__(self):
        super().__init__("Reading from output address is forbidden!")


class WritingToInputAddressError(SimulationError):
    def __init__(self):
        super().__init__("Writing to input address is forbidden!")
