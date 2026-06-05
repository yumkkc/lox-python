from lox_ast import Expr, Binary, Unary, Literal, Grouping, Print, VarDecl, Variable, Assignment, Expression, Block, If, Logical, While, Caller
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
        
        if (self.match(TokenType.LEFT_BRACE)):
            return self.block_statement()
        
        if (self.match(TokenType.IF)):
            return self.if_statement()
        
        if (self.match(TokenType.WHILE)):
            return self.while_statement()
        
        if (self.match(TokenType.FOR)):
            return self.for_statement()

        return self.expression_statement()

    def print_statement(self, print_token: Token):
        expr = self.expression()        
        self.consume(TokenType.SEMICOLON, f"Expect ';' after {print_token.lexeme}")
        return Print(expr)

    def block_statement(self):
        block_stmts = []
        while (not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end()):
            block_stmts.append(self.declarations())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return Block(block_stmts)
    
    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "expected '(' after if statement")
        expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "expected ')' after if expression")
        true_stmt = self.statement()
        false_stmt = None
        if (self.match(TokenType.ELSE)):
            false_stmt = self.statement()
        
        return If(expr, true_stmt, false_stmt)
    
    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "expected '(' after while statement")
        cond = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "expected ')' after expression")
        body = self.statement()
        return While(cond, body)
    
    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "expected '(' after for statement")
        if (self.match(TokenType.VAR)):
            declaration = (self.var_declarations(self.previous()))
        elif (not self.match(TokenType.SEMICOLON)):
            declaration = self.expression_statement()
        else:
            declaration = None
            self.consume(TokenType.SEMICOLON, "expected ';'")

        condition = None
        if (not self.match(TokenType.SEMICOLON)):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "expected ';'")
        
        increment = None
        if (not self.match(TokenType.RIGHT_PAREN)):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "expected ')' after for loop")
        
        stmt = self.statement()
        if (increment is not None):
            body = Block([stmt, Expression(increment)])
        
        if condition is None:
            condition = Literal(True)

        body = While(condition, body)

        if (declaration != None):
            body = Block([declaration, body])
        
        return body
            

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return Expression(expr)

    def expression(self):
        return self.assignment()
    
    # a = b = 3
    def assignment(self):
        expr = self.or_expr()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assignment(name, value)
            
            self.error(equals, "Invalid assignment target.")
        return expr
    
    def or_expr(self):
        expr = self.and_expr()
        right_expr = None
        while (self.match(TokenType.OR)):
            op = self.previous()    
            right_expr = self.and_expr()
            expr =  Logical(expr, op, right_expr)
        return expr

    def and_expr(self):
        expr = self.equality()
        while(self.match(TokenType.AND)):
            op = self.previous()
            right_expr = self.equality()
            expr =  Logical(expr,op, right_expr)
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
        
        return self.caller()
    
    def caller(self):
        expr = self.primary()
        while True:
            if (self.match(TokenType.LEFT_PAREN)):
                expr = self.consume_function(expr)
            else:
                break
        return expr
    
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


    def consume_arguments(self, args: list):
        expr = self.expression()
        args.append(expr)
        if len(args) > 255:
            self.error(self.peek(), "Too many arguments. Cannot have more than 255")
        if (self.match(TokenType.COMMA)):
            return self.consume_arguments(args)
        return args

    def consume_function(self, callee):
        arguments = []
        if not self.match(TokenType.RIGHT_PAREN):
            arguments = self.consume_arguments(arguments)
            self.consume(TokenType.RIGHT_PAREN, "unclosed ')' in function call")
        return Caller(callee, arguments)

            


