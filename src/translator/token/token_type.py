from enum import Enum


class TokenType(str, Enum):
    """Типы токенов"""

    NUMBER = "NUMBER"
    EXTENDED_NUMBER = "EXTENDED_NUMBER"
    SYMBOL = "SYMBOL"
    LITERAL = "LITERAL"

    BEGIN_INT = "begin_int"
    END_INT = "end_int"

    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    MOD = "mod"
    NEG = "neg"
    ABS = "abs"

    D_PLUS = "2+"
    D_MUL = "2*"
    D_MINUS = "2-"
    D_NEG = "2neg"
    D_ABS = "2abs"

    AND = "and"
    OR = "or"
    XOR = "xor"
    NOT = "not"

    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    DUP = "dup"
    DROP = "drop"
    SWAP = "swap"
    OVER = "over"

    D_DUP = "2dup"
    D_DROP = "2drop"
    D_SWAP = "2swap"
    D_OVER = "2over"

    STORE = "store"
    LOAD = "load"

    D_STORE = "2store"
    D_LOAD = "2load"

    PRINT = "print"
    READ = "read"

    ENABLE_INT = "en_int"
    DISABLE_INT = "di_int"

    STR_LITERAL_SEP = '"'

    IF = "if"
    THEN = "then"
    ELSE = "else"
    BEGIN = "begin"
    UNTIL = "until"

    COLON = ":"
    SEMICOLON = ";"

    VAR = "var"
    D_VAR = "2var"
    STR = "str"
    ALLOC = "alloc"

    COMMENT_START = "\\"

    EOF = "EOF"
