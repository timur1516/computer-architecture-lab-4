from src.constants import MAX_NUMBER, MIN_NUMBER


class Data:
    """Единица данных

    Хранит в себе адрес в памяти данных и значение
    """

    address = None
    "Адрес в памяти данных. Инициализируется в конструкторе. По умолчанию 0"

    value = None
    "Значение ячейки данных. По умолчанию 0"

    def __init__(self, value: int = 0, address: int = 0):
        assert MIN_NUMBER <= value <= MAX_NUMBER, "Value out of range"
        assert 0 <= address, "Address out of range"

        self.value = value
        self.address = address
