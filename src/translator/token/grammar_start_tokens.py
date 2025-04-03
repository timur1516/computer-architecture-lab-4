from src.translator.token.token_type import TokenType

statement_start_tokens = [TokenType.COLON, TokenType.VAR]

memory_operation_start_tokens = [TokenType.STORE, TokenType.LOAD]
io_operation_start_tokens = [TokenType.PRINT, TokenType.READ, TokenType.PRINT_STR_BEGIN]
logical_operation_start_tokens = [TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS, TokenType.GREATER,
                                  TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]
stack_operation_start_tokens = [TokenType.DUP, TokenType.DROP, TokenType.SWAP]
arithmetic_operation_start_token = [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]

operation_start_tokens = (memory_operation_start_tokens +
                          io_operation_start_tokens +
                          logical_operation_start_tokens +
                          stack_operation_start_tokens +
                          arithmetic_operation_start_token)

word_start_tokens = [TokenType.SYMBOL, TokenType.NUMBER] + operation_start_tokens

term_start_tokens = (word_start_tokens +
                     statement_start_tokens)

program_start_tokens = term_start_tokens
