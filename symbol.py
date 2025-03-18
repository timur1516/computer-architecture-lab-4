from symbol_type import SymbolType


class Symbol:
    def __init__(self, name : str, _type : SymbolType, content = None):
        self.name = name
        self.type = _type
        self.content = content
