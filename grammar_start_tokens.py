from token_type import TokenType

definition_statement_start_tokens = [TokenType.COLON]
declaration_statement_start_tokens = [TokenType.VAR]
loop_statement_start_tokens = [TokenType.BEGIN]
if_statement_start_tokens = [TokenType.IF]

statement_start_tokens = (definition_statement_start_tokens +
                          declaration_statement_start_tokens +
                          loop_statement_start_tokens +
                          if_statement_start_tokens)

memory_operation_start_tokens = [TokenType.STORE, TokenType.LOAD]
io_operation_start_tokens = [TokenType.PRINT, TokenType.EMIT, TokenType.READ]
logical_operation_start_tokens = [TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS, TokenType.GREATER,
                                  TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]
stack_operation_start_tokens = [TokenType.DUP, TokenType.DROP, TokenType.SWAP]
arithmetic_operation_start_token = [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]

operation_start_tokens = (memory_operation_start_tokens +
                          io_operation_start_tokens +
                          logical_operation_start_tokens +
                          stack_operation_start_tokens +
                          arithmetic_operation_start_token)

word_start_tokens = [TokenType.WORD, TokenType.NUMBER] + operation_start_tokens

term_start_tokens = (word_start_tokens +
                     statement_start_tokens)

program_start_tokens = term_start_tokens
