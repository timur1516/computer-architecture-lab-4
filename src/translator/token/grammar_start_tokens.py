from src.translator.token.token_type import TokenType

"""Вспомогательные  списки для задания грамматики при парсинге"""

arithmetic_operation_start_token = [
    TokenType.PLUS,
    TokenType.MINUS,
    TokenType.MUL,
    TokenType.DIV,
    TokenType.MOD,
    TokenType.NEG,
    TokenType.ABS,
]

extended_arithmetic_operation_start_token = [
    TokenType.D_PLUS,
    TokenType.D_MUL,
    TokenType.D_MINUS,
    TokenType.D_NEG,
    TokenType.D_ABS,
]

binary_operation_start_tokens = [TokenType.AND, TokenType.OR, TokenType.XOR, TokenType.NOT]

logical_operation_start_tokens = [
    TokenType.EQUALS,
    TokenType.NOT_EQUALS,
    TokenType.LESS,
    TokenType.GREATER,
    TokenType.LESS_EQUAL,
    TokenType.GREATER_EQUAL,
]

stack_operation_start_tokens = [TokenType.DUP, TokenType.DROP, TokenType.SWAP, TokenType.OVER]

extended_stack_operation_start_tokens = [TokenType.D_DUP, TokenType.D_DROP, TokenType.D_SWAP, TokenType.D_OVER]

memory_operation_start_tokens = [TokenType.STORE, TokenType.LOAD]

extended_memory_operation_start_tokens = [TokenType.D_STORE, TokenType.D_LOAD]

io_operation_start_tokens = [TokenType.PRINT, TokenType.READ]

interrupt_operation_start_token = [TokenType.ENABLE_INT, TokenType.DISABLE_INT]

operation_start_tokens = [
    *arithmetic_operation_start_token,
    *extended_arithmetic_operation_start_token,
    *binary_operation_start_tokens,
    *logical_operation_start_tokens,
    *stack_operation_start_tokens,
    *extended_stack_operation_start_tokens,
    *memory_operation_start_tokens,
    *extended_memory_operation_start_tokens,
    *io_operation_start_tokens,
    *interrupt_operation_start_token,
]

declaration_start_tokens = [TokenType.VAR, TokenType.D_VAR, TokenType.STR, TokenType.ALLOC]

word_start_tokens = [TokenType.SYMBOL, TokenType.NUMBER, TokenType.EXTENDED_NUMBER, *operation_start_tokens]

statement_body_start_tokens = [TokenType.IF, TokenType.BEGIN, *word_start_tokens]

statement_start_tokens = [TokenType.COLON, *declaration_start_tokens, TokenType.BEGIN_INT]

term_start_tokens = word_start_tokens + statement_start_tokens

program_start_tokens = term_start_tokens
