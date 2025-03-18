# Forth. Транслятор и модель

---

- Выполнил: Ступин Тимур Русланович
- `forth | risc | harv | hw | tick | binary | trap | mem | pstr | prob2 | superscalar`

## Язык программирования

```ebnf
program ::= term EOF

term ::= word
       | statement
       | term term

word ::= number
       | operation
       | symbol

symbol ::= defined-word
         | variable-name

operation ::= arithmetic-operation
            | stack-operation
            | logical-operation
            | io-operation
            | memory-operation

arithmetic-operation ::= "+" | "-" | "*" | "/"

stack-operation ::= "dup" | "drop" | "swap"

logical-operation ::= "=" | "!=" | ">" | ">=" | "<" | "<="

io-operation ::= "." | "emit" | ","

memory-operation ::= "!" | "@"

statement ::= definition-statement
            | declaration-statement

definition-statement ::= ":" defined-word (block | if-statement | loop-statement) ";"

declaration-statement ::= "var" variable-name

block ::= word
        | block block

if-statement ::= "if" block ("then" | ("else" block "then"))

loop-statement ::= "begin" block "until"

```

Код выполняется последовательно. Операции:

- `+`