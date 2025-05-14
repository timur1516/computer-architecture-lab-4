var sum_of_squares
var square_of_sum

: sum_sq
    0
    swap
    begin
        dup 0 != if
            swap
            over dup * +
            swap -1 +
            1
        else
            0
        then
    until
    drop
;

: sum
    0
    swap
    begin
        dup 0 != if
            swap
            over +
            swap -1 +
            1
        else
            0
        then
    until
    drop
;

sum_of_squares 0 store
square_of_sum 0 store

100 sum dup *
100 sum_sq
-

print