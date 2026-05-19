from typing import Any

from error import LoxRuntimeError, run_time_error
from lox_ast import Expr, Binary, Grouping, Literal, Unary
from lex_token import Token
from token_type import TokenType

def interpret(tree: Expr):
    match tree:
        case Literal(value):
            return value    
        case Grouping(expr):
            return interpret(expr)
        case Unary(op, right):
            value = interpret(right)
            match op.token_type:
                case TokenType.MINUS:
                    checkNumberOperandUnary(op, value)
                    return -float(value)
                case TokenType.BANG:
                    return not is_truthy(right)
            return None
        case Binary(left, op, right):
            left = interpret(left)
            right = interpret(right)
            match (op.token_type):
                case TokenType.GREATER:
                    checkNumberOperand(op, left, right)
                    return float(left) > float(right)
                case TokenType.GREATER_EQUAL:
                    checkNumberOperand(op, left, right)
                    return float(left) >= float(right)
                case TokenType.LESS:
                    checkNumberOperand(op, left, right)
                    return float(left) < float(right)                
                case TokenType.LESS_EQUAL:
                    checkNumberOperand(op, left, right)
                    return float(left) <= float(right)                
                case TokenType.MINUS:
                    checkNumberOperand(op, left, right)
                    return float(left) - float(right)
                case TokenType.SLASH:
                    checkNumberOperand(op, left, right)
                    return float(left)/ float(right)
                case TokenType.STAR:
                    checkNumberOperand(op, left, right)
                    return float(left) * float(right)
                case TokenType.PLUS:
                    if isinstance(left, float) and isinstance(right, float):
                        return float(left) + float(right)
                    if isinstance(left, str) and isinstance(right, str):
                        return str(left) + str(right)
                    raise LoxRuntimeError(op, "Operands must be two number or strings")
                case TokenType.BANG_EQUAL:
                    return not (left == right)
                case TokenType.EQUAL_EQUAL:
                    return (left == right)
                
            return None
        
def is_truthy(value) -> bool:
    if value == None:
        return False
    if isinstance(value, bool):
        return bool(value)
    return True

def checkNumberOperandUnary(op: Token, operand: Any):
    if isinstance(operand, float):
        return 
    raise LoxRuntimeError(op, "Operand must be a number")


def checkNumberOperand(op: Token, left: Any, right: Any):
    print(left)
    print(right)
    if (isinstance(left, float)) and (isinstance(right, float)):
        return 
    raise LoxRuntimeError(op, "Operand must be a number")
        

def ast_interpret(expr: Expr):
    try:
        return interpret(expr)
    except LoxRuntimeError as e:
        run_time_error(e)
