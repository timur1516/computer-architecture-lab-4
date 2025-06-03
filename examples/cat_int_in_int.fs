#include "stdlib/io.fs"

: endless_loop
    begin
      read_value
      print
      1
    until
;

endless_loop