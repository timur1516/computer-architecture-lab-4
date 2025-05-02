from src.translator.token.token_type import TokenType

memory_operation_start_tokens = [TokenType.STORE, TokenType.LOAD, TokenType.STR_LITERAL_SEP]

io_operation_start_tokens = [TokenType.PRINT, TokenType.READ]

interrupt_operation_start_token = [TokenType.ENABLE_INT, TokenType.DISABLE_INT]

logical_operation_start_tokens = [
    TokenType.EQUALS,
    TokenType.NOT_EQUALS,
    TokenType.LESS,
    TokenType.GREATER,
    TokenType.LESS_EQUAL,
    TokenType.GREATER_EQUAL,
]
binary_operation_start_tokens = [TokenType.AND, TokenType.OR, TokenType.XOR, TokenType.NOT]
stack_operation_start_tokens = [TokenType.DUP, TokenType.DROP, TokenType.SWAP]
arithmetic_operation_start_token = [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]

extended_arithmetic_operation_start_token = [TokenType.D_PLUS, TokenType.D_MUL]

operation_start_tokens = (
    memory_operation_start_tokens
    + io_operation_start_tokens
    + logical_operation_start_tokens
    + stack_operation_start_tokens
    + arithmetic_operation_start_token
    + extended_arithmetic_operation_start_token
    + binary_operation_start_tokens
    + interrupt_operation_start_token
)

word_start_tokens = [TokenType.SYMBOL, TokenType.NUMBER, TokenType.EXTENDED_NUMBER, *operation_start_tokens]

declaration_start_tokens = [TokenType.VAR, TokenType.D_VAR, TokenType.STR, TokenType.ALLOC]

statement_start_tokens = [TokenType.COLON, TokenType.BEGIN_INT, *declaration_start_tokens]

statement_body_start_tokens = [TokenType.IF, TokenType.BEGIN, *word_start_tokens]

term_start_tokens = word_start_tokens + statement_start_tokens

program_start_tokens = term_start_tokens
