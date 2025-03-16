from lexer import Lexer
from parser import Parser


def main():
    text = '''
            : a 1 2 - + ;
            begin 1 3 a until
            if 1 * / then
            if 2 else . then 
            var x
            123 x !
            '''
    Parser(Lexer(text)).parse()


if __name__ == '__main__':
    main()
