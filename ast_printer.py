from lox_ast import Expr, Binary, Grouping, Literal, Unary
from lex_token import Token
from token_type import TokenType


def ast_print(expr: Expr) -> str:
    match expr:
        case Binary(left, operator, right):
            return f"({operator.lexeme} {ast_print(left)} {ast_print(right)})"

        case Grouping(expression):
            return f"( {ast_print(expression)} )"

        case Literal(value):
            return str(value)

        case Unary(operator, right):
            return f"({operator.lexeme} {ast_print(right)})"

        case _:
            return "Unknown"


if __name__ == "__main__":
    expr = Binary(
        Literal(123),
        Token(TokenType.PLUS, "+", None, 1),
        Literal(456)
    )

    print(ast_print(expr))