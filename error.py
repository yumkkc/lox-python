from lex_token import Token
from token_type import TokenType

had_error = False
had_run_time = False

def error (line: int, message: str):
    report(line, "", message)

def parse_error(token: Token, message: str):
    if (token.token_type == TokenType.EOF):
        report (token.line, " at end", message)
    else:
        report (token.line, f" at '{token.lexeme}'", message)

def run_time_error (error):
    global had_run_time
    print(f"[Line {error.token.line}]{error.message}\n")
    had_run_time = True


def report(line: int, where: str, message: str):
    global had_error
    print(f"[line {line} ] Error {where} : {message}")
    had_error = True

class ParseError(RuntimeError):
    pass

class LoxRuntimeError(RuntimeError):
    def __init__(self, token, message):
        super().__init__(message)
        self.message = message
        self.token = token
