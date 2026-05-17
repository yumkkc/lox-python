from typing import *
from lex_token import Token
from token_type import TokenType
from error import *


keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}

class Scanner():
    def __init__(self, source: str):
        self.source = source
        self.line = 1
        self.current = 0
        self.start = 0
        self.source_length = len(source)
        self.tokens: List[Token] = []

    def scan_tokens(self):
        while (not self.is_at_end()):
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(TokenType.EOF)
            
    def scan_token(self):
        word = self.advance()
        match word:
            case "(":
                self.add_token(TokenType.LEFT_PAREN, word)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN, word)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE, word)
            case "{":
                self.add_token(TokenType.LEFT_BRACE, word)
            case ",":
                self.add_token(TokenType.COMMA, word)
            case "-":
                self.add_token(TokenType.MINUS, word)
            case "+":
                self.add_token(TokenType.PLUS, word)
            case ";":
                self.add_token(TokenType.SEMICOLON, word)
            case "*":
                self.add_token(TokenType.STAR, word)

            #one to two character tokens
            case "!":
                self.add_token(TokenType.BANG_EQUAL, self.advance()) if self.match("=") else self.add_token(TokenType.BANG, word)
            case "=":
                self.add_token(TokenType.EQUAL_EQUAL, self.advance()) if self.match("=") else self.add_token(TokenType.EQUAL, word)
            case ">":
                self.add_token(TokenType.GREATER_EQUAL, self.advance()) if self.match("=") else self.add_token(TokenType.GREATER, word)
            case "<":
                self.add_token(TokenType.LESS_EQUAL, self.advance()) if self.match("=") else self.add_token(TokenType.LESS, word)

            case "/":
                if self.match("/"):
                    while (self.look() != "\n" and not self.is_at_end()):
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH, word)

            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1

            case '"':
                self.string()
            case _:
                if (word.isdigit()):
                    self.digit(word)
                elif (word.isalpha()):
                    self.identifier(word)
                else:
                    error(self.line, "Unexpected character.")


    def add_token(self, type: TokenType, lexeme: str, literal: str = ""):
        token = Token(type, lexeme, literal, self.line)
        self.tokens.append(token)

    def advance(self):
        self.current += 1
        return self.source[self.start:self.current]
    
    def look(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def is_at_end(self):
        return self.current >= self.source_length
    
    def match (self, expected: str) -> bool:
        if self.is_at_end():
            return False
        return (self.source[self.current] == expected)
    
    def string(self):
        while (self.look() != '"'):
            if (self.is_at_end()):
                error(self.line, "Unterminated String")
                return
            self.advance()
        cur_string = self.advance().strip('"')
        self.add_token(TokenType.STRING, cur_string, cur_string)

    def digit(self, word):
        while (self.look().isdigit()):
            word = self.advance()

        if (self.match (".")):
            self.advance()
            while (self.look().isdigit()):
                word = self.advance()
        self.add_token(TokenType.NUMBER, word, float(word))

    def identifier(self, word):
        while (self.look().isalnum()):
            word = self.advance()

        reserved = keywords.get(word, None)
        if reserved:
            self.add_token(reserved, word)
        else:
            self.add_token(TokenType.IDENTIFIER, word)
            
