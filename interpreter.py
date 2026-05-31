from typing import Any, List
from error import LoxRuntimeError, run_time_error
from lox_ast import (Expr, Binary, Grouping, Literal, Unary,
                     Expression, Print, Stmt, VarDecl, Variable,
                     Assignment, Block)
from lex_token import Token
from token_type import TokenType
from utils import stringify
from environment import Environment


class Interpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, tree):
        match tree:
            case Literal(value):
                return value

            case Grouping(expr):
                return self.interpret(expr)

            case Unary(op, right):
                value = self.interpret(right)
                match op.token_type:
                    case TokenType.MINUS:
                        self._check_number_unary(op, value)
                        return -float(value)
                    case TokenType.BANG:
                        return not self._is_truthy(value) 
                return None

            case Variable(iden):
                return self.env.retrive(iden)

            case Assignment(name, value):
                value = self.interpret(value)
                self.env.assign(name, value)
                return value

            case Binary(left, op, right):
                left = self.interpret(left)
                right = self.interpret(right)
                match op.token_type:
                    case TokenType.GREATER:
                        self._check_number(op, left, right)
                        return float(left) > float(right)
                    case TokenType.GREATER_EQUAL:
                        self._check_number(op, left, right)
                        return float(left) >= float(right)
                    case TokenType.LESS:
                        self._check_number(op, left, right)
                        return float(left) < float(right)
                    case TokenType.LESS_EQUAL:
                        self._check_number(op, left, right)
                        return float(left) <= float(right)
                    case TokenType.MINUS:
                        self._check_number(op, left, right)
                        return float(left) - float(right)
                    case TokenType.SLASH:
                        self._check_number(op, left, right)
                        return float(left) / float(right)
                    case TokenType.STAR:
                        if isinstance(left, float) and isinstance(right, float):
                            return float(left) * float(right)
                        if isinstance(left, str) and isinstance(right, float):
                            return str(left) * int(right)
                        raise LoxRuntimeError(op, "Operands must be two numbers or a string * number")
                    case TokenType.PLUS:
                        if isinstance(left, float) and isinstance(right, float):
                            return float(left) + float(right)
                        if isinstance(left, str) and isinstance(right, str):
                            return str(left) + str(right)
                        raise LoxRuntimeError(op, "Operands must be two numbers or strings")
                    case TokenType.BANG_EQUAL:
                        return left != right
                    case TokenType.EQUAL_EQUAL:
                        return left == right

            case Expression(expr):
                self.interpret(expr)
                return None

            case Print(expr):
                print(stringify(self.interpret(expr)))
                return None

            case Block(stmts):
                self._execute_block(stmts, Environment(enclosing=self.env))  # fixed: new scope
                return None

            case VarDecl(iden, initializer):
                value = self.interpret(initializer) if initializer is not None else None
                self.env.define(iden, value)
                return None

    def _execute_block(self, stmts: List[Stmt], env: Environment):
        """Run a block inside a given environment, restoring the previous one after."""
        previous = self.env
        try:
            self.env = env
            for stmt in stmts:
                self.interpret(stmt)
        finally:
            self.env = previous 

    def _is_truthy(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def _check_number_unary(self, op: Token, operand: Any):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(op, "Operand must be a number")

    def _check_number(self, op: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(op, "Operands must be numbers")


def ast_interpret(stmts: List[Stmt]):
    interpreter = Interpreter()
    try:
        for stmt in stmts:
            interpreter.interpret(stmt)
    except LoxRuntimeError as e:
        run_time_error(e)