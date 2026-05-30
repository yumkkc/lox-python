from lex_token import Token
from error import LoxRuntimeError
from typing import Any

class Environment:
    def __init__(self):
        self.values = {}

    def define(self, key: Token, val: Any):
        self.values[key.lexeme] = val

    def retrive(self, key: Token) -> Any:
        if key.lexeme not in self.values:
            raise LoxRuntimeError (key, f"{key.lexeme} not defined")
        
        return self.values[key.lexeme]
    
    def assign (self, name, value):
        if name.lexeme in self.values:
            self.values.put(name.lexeme, value)
            return 
        
        raise LoxRuntimeError(name, f"Undefined varibale '{name.lexeme}'.")
        