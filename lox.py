import sys
from scanner import Scanner
from error import *
from parser import Parser
import ast_printer

hadError: bool = False

class Lox:
    def run_prompt(self):
        while True:
            print("> ", end="")
            code = input()
            self.run(code)
            hadError = False

    def run_file(self, file_name: str):
        with open(file_name, "r") as f:
            content = f.read()
            if (hadError):
                sys.exit(65)

    def run(self, content):
        lexer = Scanner(content)
        lexer.scan_tokens()
        parser = Parser(lexer.tokens)
        expr = parser.parse()
        print(ast_printer.ast_print(expr))
        if (hadError):
            return

    def main(self, args: list):
        if len(args) <= 1:
            self.run_prompt()
        else:
            self.run_file (args[1])


if __name__ == "__main__":
    lox = Lox()
    lox.main(sys.argv)

