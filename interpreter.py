import random
from typing import Any, List
import lox_callable
from error import LoxRuntimeError, run_time_error
from lox_ast import (Expr, Binary, Function, Grouping, Literal, Unary,
                     Expression, Print, Stmt, VarDecl, Variable,
                     Assignment, Block, If, Logical, While, Caller, Return)
from lex_token import Token
from token_type import TokenType
from utils import stringify
from environment import Environment
import primitive_functions as pf


class Interpreter:
    _global_env = Environment()
    env = _global_env
    _function_counter = 0
    env.define("clock", pf.Clock)
    in_function = False

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
            
            case Logical(left, op, right):
                left_value = self.interpret(left)
                left_value_truth = self._is_truthy(left_value)
                if op.token_type == TokenType.OR:
                   if left_value_truth:
                       return left_value
                else:
                    if not left_value_truth:
                        return left_value
                return self.interpret(right)

            case Print(expr):
                print(stringify(self.interpret(expr)))
                return None

            case Block(stmts):
                return self._execute_block(stmts, Environment(enclosing=self.env))  # fixed: new scope
            
            case If (condition, then_block, else_block):
                self._execute_if(condition, then_block, else_block)

            case While(condition, body):
                while (self._is_truthy(self.interpret(condition))):
                    self.interpret(body)
                return None

            case VarDecl(iden, initializer):
                value = self.interpret(initializer) if initializer is not None else None
                self.env.define(iden.lexeme, value)
                return None

            case Caller(callee, arguments, paren):
                callee = self.interpret(callee)()
                argument_list = []
                for argument in arguments:
                    argument_list.append(self.interpret(argument))

                if not isinstance(callee, lox_callable.LoxCallable):
                    raise LoxRuntimeError(paren,  "Not callable expression")
                
                if(callee.arity() != len(arguments)):
                    raise LoxRuntimeError(paren, "Arguments doesn't match for function")
                
                return callee.call(self, argument_list)

            case Function(name, body, params):
                self._define_function(name, body, params)
                return None

            case Return (expr):
                return_value = self.interpret(expr)
                return return_value

    def _execute_block(self, stmts: List[Stmt], env: Environment):
        """Run a block inside a given environment, restoring the previous one after."""
        previous = self.env
        final_val = None
        try:
            self.env = env
            for stmt in stmts:
                final_val = self.interpret(stmt)
        finally:
            self.env = previous 
            return final_val

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
    
    def _execute_if(self, condition, if_block, then_block):
        condition_value = self.interpret(condition)
        if (self._is_truthy(condition_value)):
            self.interpret(if_block)
        elif then_block is not None:
            self.interpret(then_block)
        
        return None
    
    def _define_function(self, name, body, params):
        class_name = name.lexeme + str(self._function_counter)
        self._function_counter += 1
        class class_name(lox_callable.LoxCallable):
            def call(self, interpreter: Interpreter, arguments):
                #set arguments to formal params
                original_env = interpreter.env
                interpreter.env = Environment(original_env)
                interpreter.in_function = True
                for i, arg in enumerate(arguments):
                    interpreter.env.define(params[i].lexeme, arg)
                return_val = interpreter.interpret(body)
                interpreter.env = original_env
                interpreter.in_function = False
                return return_val
            def arity(self):
                return len(params)
        self.env.define(name.lexeme, class_name)



def ast_interpret(stmts: List[Stmt]):
    interpreter = Interpreter()
    try:
        for stmt in stmts:
            interpreter.interpret(stmt)
        return interpreter.env
    except LoxRuntimeError as e:
        run_time_error(e)