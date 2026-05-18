from lex_token import Token
from token_type import TokenType

def error (line: int, message: str):
    report(line, "", message)

def parse_error(token: Token, message: str):
    if (token.token_type == TokenType.EOF):
        report (token.line, " at end", message)
    else:
        report (token.line, f" at '{token.lexeme}'", message)


def report(line: int, where: str, message: str):
    print(f"[line {line} ] Error {where} : {message}")
    hadError = True

class ParseError(RuntimeError):
    pass