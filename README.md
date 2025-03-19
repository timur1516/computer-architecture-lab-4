# Forth. Транслятор и модель

---

- Выполнил: Ступин Тимур Русланович, P3208
- `forth | risc | harv | hw | tick | binary | trap | mem | pstr | prob2 | superscalar`

## Язык программирования

### Синтаксис

Расширенная форма Бэкуса-Наура:

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

### Семантика

- `+` -- сложить два верхних элемента стека и положить результат в стек. Операнды убираются из стека
- `-` -- вычесть первое значение в стеке из второго и положить результат в стек. Операнды убираются из стека
- `*` -- перемножить два верхних элемента стека и результат положить в стек. Операнды убираются из стека
- `/` -- разделить нацело второй элемент стека на первый и положить результат в стек. Операнды убираются из стека
- `dup` -- продублировать верхний элемент стека
- `drop` -- удалить верхний элемент стека
- `swap` -- поменять местами верхний элемент стека и элемент после него
- `<number>` -- положить значение `number` на вершину стека
- `=` -- сравнить на равенство первый и второй элементы стека и положить результат в стек. Операнды убираются из стека
- `>` -- проверить что второй элемент стека строго больше первого и положить результат в стек. Операнды убираются из
  стека
- `<` -- проверить что второй элемент стека строго меньше первого и положить результат в стек. Операнды убираются из
  стека
- `>=` -- проверить что второй элемент стека больше либо равен первого и положить результат в стек. Операнды убираются
  из
  стека
- `<=` -- проверить что второй элемент стека меньше либо равен первого и положить результат в стек. Операнды убираются
  из стека
- `.` -- взять верхний элемент стека и вывести его в стандартный поток вывода
- `,` -- прочитать значение из стандартного потока ввода и положить его в стек
- `!` -- взять верхний элемент стека и сохранить его по адресу хранящемуся во втором элементе стека. И значение и адрес
  убираются из стека
- `@` -- взять адрес из первого элемента стека и добавить значение, хранящееся по этому адрес в стек. Адрес убирается из
  стека
- `if <block> then` -- если значение верхнего элемента стека истинно, выполнить набор инструкций из `block`. Верхний
  элемент убирается из стека
- `if <block1> else <block2> then` -- если значение верхнего элемента стека истинно, выполнить набор инструкций из
  `block1`, иначе выполнить набор инструкция из `block2`. Верхний элемент убирается из стека
- `begin <block> until` -- если после того как выполнены инструкции из `block` верхний элемент стека не нулевой (true),
  то блок выполняется ещё раз. При проверке верхний элемент из стека
- `var <name>` -- объявить переменную с именем `name`. При этом переменная привязывается к конкретной ячейке памяти (
  аллокация)
- `: <name> <body> ;` -- создать объявление с именем `name` и содержимым `body`.
- `<definition-name>` -- на этапе компиляции данное значение заменяется блоком, соответствующим указанному объявлению
- `<variable-name>` -- положить на вершину стека адрес переменной с именем `variable-name`

#### Комментарии

TO BE DONE

#### Особенности реализации

- Циклы и условия могут быть только внутри определений (`definition`)
- В ситуациях когда происходят проверки на истинность за `false` принимается нулевое значение, а любое другое значение
  считается равным `true`
- Все определения (`definition`) заменяются на своё содержимое на этапе компиляции

#### Порядок выполнения

Программа выполняется последовательно, одна инструкция за другой

#### Память

- Распределяется статически на этапе трансляции
- Стек является частью памяти данных, увеличивается вниз начиная с конца (от наибольшего адреса)

#### Области видимости

Все данные расположены в одной глобальной области видимости

#### Типизация, виды литералов

В языке определены два вида литералов:

- Строковые
- Целочисленные

Строковые литералы размечаются в памяти в формате Pascal-string, целочисленные загружаются прямой загрузкой. Типизация
отсутствует, так как переменные вводимые пользователем являются указателями на ячейку памяти и не привязаны к типу.

## Организация памяти

- Гарвардская архитектура
- Размер машинного слова:

  - Память команд: 32 бита
  - Память данных: 32 бита

- Имеет линейное адресное пространство
- В памяти данных хранятся статические строки и переменные
- В памяти команд хранятся инструкции для выполнения
- Взаимодействие с памятью происходит через инструкции `!` и `@`
- Виды адресации:

  - Прямая абсолютная
  - Косвенная



