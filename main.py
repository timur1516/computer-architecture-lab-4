from interpreter import Interpreter


def main():
    interpreter = Interpreter()
    while True:
        text = input()
        try:
            interpreter.interpret(text)
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    main()
