2var biggest_dword                                  \ 2^63 - 1
biggest_dword 9223372036854775807. 2store
biggest_dword 2load print print

2var smallest_dword                                 \ -2^63
smallest_dword -9223372036854775808. 2store
smallest_dword 2load print print

2147483647. 1. 2+ print print                       \ (2^31 - 1) + 1

-2147483648. 1. 2- print print                      \ (-2^31) - 1

2147483648. 2147483648. 2- print print              \ (2^31) - (2^31)

1073741824 4 2* print print                         \ (2^30) * 4

-2147483648 2 2* print print                        \ (-2^31) * 2

-2147483648 -2 2* print print                       \ (-2^31) * (-2)