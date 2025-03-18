from lexer import Lexer
from parser import Parser


def main():
    text = '''
            : a 1 2 - + ;
            : b begin 1 3 a until ;
            : c if 1 * / b then ;
            : d if 2 else . c then ; 
            var x d
            123 x !
            '''
    prog = Parser(Lexer(text)).parse()
    for l in prog:
        print(l)


if __name__ == '__main__':
    main()
