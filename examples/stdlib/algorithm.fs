\ В данном файле приведена реализация различных алгоритмов

\ ============================================================================================================================

\ Подключение необходимых библиотек
#include "buffer.fs"

\ ============================================================================================================================

\ Вспомогательные переменные
var i
var j
var n
var array_

\ ============================================================================================================================

\ Сортировка пузырьком
\ Выполняет сортировку массива данных по возрастанию
\ --------------------------------------------------------------------
\   ... addr        --->        ...
\ --------------------------------------------------------------------
: bubble_sort
    array_ swap store                                   \ Сохранили адрес массива в переменную
                                                        \ сделано для удобства, чтобы не извращаться со стеком

    n                                                   \ Сохранили длину массива
        array_ load buffer_len
    store

    i 0 store begin i load n load < if                  \ for i in range(0, n)
        j 0 store begin j load n load 1 - < if          \ for j in range(0, n - 1)

        array_ load j load + 1 + load                   \ array[j]
        array_ load j load + 2 + load                   \ array[j + 1]
        > if                                            \ if array[j] > array[j + 1]

            array_ load j load + 1 + load               \ array[j]
            array_ load j load + 2 + load               \ array[j + 1]
            array_ load j load + 1 + swap store         \ array[j] = array[j + 1]
            array_ load j load + 2 + swap store         \ array[j + 1] = array[j]

        then

        j j load 1 + store 1 else 0 then until
    i i load 1 + store 1 else 0 then until
;