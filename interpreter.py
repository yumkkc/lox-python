from typing import Any, List, Union

from error import LoxRuntimeError, run_time_error
from lox_ast import Expr, Binary, Grouping, Literal, Unary, Expression, Print, Stmt, VarDecl, Variable
from lex_token import Token
from token_type import TokenType
from utils import stringify
from environment import Environment

env = Environment()

def interpret(tree: Union[Expr, Stmt]):
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
        case Variable (iden):
            return env.retrive(iden)
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
                    if isinstance(left, float) and isinstance(right, float):
                        return float(left) * float(right)
                    if isinstance(left, str) and isinstance (right, float):
                        return str(left) * int(right)
                    raise LoxRuntimeError(op, "Operands must be two number or a string * number")
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
        case Expression (expr):
            interpret(expr)
            return None
        case Print (expr):
            expr_value = interpret(expr)
            print(stringify(expr_value))
            return None
        
        case VarDecl(iden, initializer):
            if initializer is not None:
                initializer = interpret(initializer)
            
            env.define(iden, initializer)
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
    if (isinstance(left, float)) and (isinstance(right, float)):
        return 
    raise LoxRuntimeError(op, "Operand must be a number")
        

def ast_interpret(stmts: List[Stmt]):
    try:
        for statement in stmts:
            interpret(statement)
    except LoxRuntimeError as e:
        run_time_error(e)
