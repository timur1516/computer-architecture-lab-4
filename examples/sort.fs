#include "stdlib/buffer.fs"
#include "stdlib/io.fs"

var i
var j
var n
alloc array 50

: bubble_sort

    n                                                   \ Сохранили длину массива
        array buffer_len
    store

    i 0 store begin i load n load < if                  \ for i in range(0, n)
        j 0 store begin j load n load 1 - < if          \ for j in range(0, n - 1)

        array j load + 1 + load                         \ array[j]
        array j load + 2 + load                         \ array[j + 1]
        > if                                            \ if array[j] > array[j + 1]

            array j load + 1 + load                     \ array[j]
            array j load + 2 + load                     \ array[j + 1]
            array j load + 1 + swap store               \ array[j] = array[j + 1]
            array j load + 2 + swap store               \ array[j + 1] = array[j]

        then

        j j load 1 + store 1 else 0 then until
    i i load 1 + store 1 else 0 then until
;

array read_array
bubble_sort
array print_buffer