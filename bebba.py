import sys
from scanner import Scanner
from error import *
from parser import Parser
import ast_printer
from interpreter import ast_interpret


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
            self.run(content)
            if (had_error):
                sys.exit(65)
            if(had_run_time):
                sys.exit(70)

    def run(self, content):
        lexer = Scanner(content)
        lexer.scan_tokens()
        parser = Parser(lexer.tokens)
        stmts = parser.parse()
        if (had_error or had_run_time):
            return
        ast_interpret(stmts)


    def main(self, args: list):
        if len(args) <= 1:
            self.run_prompt()
        else:
            self.run_file (args[1])


if __name__ == "__main__":
    lox = Lox()
    lox.main(sys.argv)

