from lox_ast import Expr, Binary, Unary, Literal, Grouping, Print, VarDecl, Variable, Assignment, Expression
from token_type import TokenType
from lex_token import Token
from error import ParseError, parse_error

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            statements = []
            while (not self.is_at_end()):
                statements.append(self.declarations())
            return statements
        except Exception as e:
            return []
        
    def declarations(self):
        if (self.match(TokenType.VAR)):
            return self.var_declarations(self.previous())

        return self.statement()
    
    def var_declarations(self, var_token):
        self.consume(TokenType.IDENTIFIER, f"Expected Identifier after {var_token.lexeme}")    
        iden = self.previous()
        initilizer = None
        if (self.match(TokenType.EQUAL)):
            initilizer = self.expression()
        self.consume(TokenType.SEMICOLON, f"Expected ; after {var_token.lexeme}")
        return VarDecl(iden, initilizer)
        
        
    def statement(self):
        if (self.match(TokenType.PRINT)):
            return self.print_statement(self.previous())

        return self.expression_statement()

    def print_statement(self, print_token: Token):
        expr = self.expression()        
        self.consume(TokenType.SEMICOLON, f"Expect ';' after {print_token.lexeme}")
        return Print(expr)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return Expression(expr)

    def expression(self):
        return self.assignment()
    
    # a = b = 3
    def assignment(self):
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assignment(name, value)
            
            self.error(equals, "Invalid assignment target.")
        return expr


    def equality(self) -> Expr:
        expr: Expr = self.comparision()

        while (self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.comparision()
            expr = Binary(expr, operator, right)

        return expr
    
    def comparision(self) -> Expr:
        expr: Expr = self.term()

        while (self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr
    
    def term(self) -> Expr:
        expr: Expr = self.factor()


        while (self.match(TokenType.MINUS, TokenType.PLUS)):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()

        while(self.match(TokenType.SLASH, TokenType.STAR)):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self) -> Expr:
        if (self.match(TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()    
            return Unary(operator, right)
        
        return self.primary()
    
    def primary(self):        
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.IDENTIFIER):
            return Variable (self.previous())
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if (self.match(TokenType.LEFT_PAREN)):
            expr = self.expression();
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression")
        

    # helpers
    def error(self, token, message) -> ParseError:
        parse_error(token, message)
        err = ParseError()
        return err

    def consume(self, token, error_message):
        if (self.check(token)):
            return self.advance()
        
        raise self.error(self.peek(), error_message)

    def match(self, *tokens) -> bool:
        for token in tokens:
            if (self.check(token)):
                self.advance()
                return True

        return False
    
    def check(self, token) -> bool:
        if (self.is_at_end()):
            return False
        
        return self.peek().token_type == token
    
    def advance(self):
        if (not self.is_at_end()):
            self.current += 1
            return self.previous()
        
    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def synchronize(self):
        self.advance()

        while (not self.is_at_end()):
            if (self.previous() == TokenType.SEMICOLON):
                return
            
            match (self.peek().token_type):
                case (
                    TokenType.CLASS 
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.FOR
                    | TokenType.IF
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ): 
                    return
            self.advance()


