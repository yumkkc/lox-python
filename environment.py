from lex_token import Token
from error import LoxRuntimeError
from typing import Any

class Environment:
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, key: str, val: Any):
        self.values[key] = val

    def retrive(self, key: Token) -> Any:
        if key.lexeme not in self.values:
            # if not in this environment, see in above
            if self.enclosing != None:
                return self.enclosing.retrive(key)
            
            raise LoxRuntimeError (key, f"{key.lexeme} not defined")
        
        return self.values[key.lexeme]
    
    def assign (self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return 
        
        if self.enclosing != None:
            return self.enclosing.assign(name, value)
        
        raise LoxRuntimeError(name, f"Undefined varibale '{name.lexeme}'.")
