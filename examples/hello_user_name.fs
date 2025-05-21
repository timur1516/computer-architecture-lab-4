#include "stdlib/io.fs"

str     welcome_string      " What is your name?"
str     hello_string        " Hello, "
str     exclamation_mark    " !"
alloc   input_buffer        50

welcome_string print_buffer
10 print

input_buffer read_string

hello_string print_buffer
input_buffer print_buffer
exclamation_mark print_buffer