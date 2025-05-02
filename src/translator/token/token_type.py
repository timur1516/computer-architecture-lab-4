from enum import Enum


class TokenType(str, Enum):
    NUMBER = "NUMBER"
    EXTENDED_NUMBER = "EXTENDED_NUMBER"
    SYMBOL = "SYMBOL"
    LITERAL = "LITERAL"

    BEGIN_INT = "begin_int"
    END_INT = "end_int"
    ENABLE_INT = "en_int"
    DISABLE_INT = "di_int"

    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"

    D_PLUS = "2+"
    D_MUL = "2*"

    AND = "and"
    OR = "or"
    XOR = "xor"
    NOT = "not"

    DUP = "dup"
    DROP = "drop"
    SWAP = "swap"

    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    PRINT = "print"
    READ = "read"

    STR_LITERAL_SEP = '"'

    STORE = "store"
    LOAD = "load"

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

    EOF = "EOF"
