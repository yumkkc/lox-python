from dataclasses import dataclass
from typing import Any, List
from lex_token import Token

class Expr:
    pass

@dataclass
class Binary (Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass 
class Grouping (Expr):
    expression: Expr

@dataclass
class Literal (Expr):
    value: Any

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

# statements
class Stmt:
    pass

@dataclass
class Expression(Stmt):
    expression: Expr

@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class VarDecl():
    name: Token
    initializer: Expr

@dataclass    
class Variable ():
    name: Token


@dataclass
class Assignment ():
    name: Token
    value: Expr

@dataclass    
class Block ():
    statements : List[Stmt]

@dataclass
class If (Stmt):
    condition: Expr
    thenBranch: Stmt
    elseBranch: Stmt

@dataclass    
class Logical (Expr):
    left : Expr
    operator: Token
    right: Expr


@dataclass
class While (Stmt):
    condition: Expr
    body: Stmt

@dataclass    
class Caller (Expr):
    callee: Expr
    args: List[Expr]
    paren: Token