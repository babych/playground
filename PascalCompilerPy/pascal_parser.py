"""
Pascal Compiler - Parser Module
Parses tokens into an Abstract Syntax Tree
"""

from typing import List, Optional
from pascal_lexer import Token, TokenType
from ast_nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def current_token(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 1) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self) -> Token:
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name}, got {token.type.name} "
                f"at {token.line}:{token.column}"
            )
        return self.advance()
    
    def parse(self) -> Program:
        return self.parse_program()
    
    def parse_program(self) -> Program:
        self.expect(TokenType.PROGRAM)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEMICOLON)
        
        declarations = []
        while self.current_token().type in (TokenType.VAR, TokenType.CONST, 
                                           TokenType.PROCEDURE, TokenType.FUNCTION):
            declarations.extend(self.parse_declarations())
        
        block = self.parse_block()
        self.expect(TokenType.DOT)
        
        return Program(name, declarations, block)
    
    def parse_declarations(self) -> List[Declaration]:
        token = self.current_token()
        
        if token.type == TokenType.VAR:
            return self.parse_var_declarations()
        elif token.type == TokenType.CONST:
            return self.parse_const_declarations()
        elif token.type == TokenType.PROCEDURE:
            return [self.parse_procedure_declaration()]
        elif token.type == TokenType.FUNCTION:
            return [self.parse_function_declaration()]
        
        return []
    
    def parse_var_declarations(self) -> List[VarDeclaration]:
        self.expect(TokenType.VAR)
        declarations = []
        
        while self.current_token().type == TokenType.IDENTIFIER:
            var_names = [self.expect(TokenType.IDENTIFIER).value]
            
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                var_names.append(self.expect(TokenType.IDENTIFIER).value)
            
            self.expect(TokenType.COLON)
            type_spec = self.parse_type_spec()
            self.expect(TokenType.SEMICOLON)
            
            declarations.append(VarDeclaration(var_names, type_spec))
        
        return declarations
    
    def parse_const_declarations(self) -> List[ConstDeclaration]:
        self.expect(TokenType.CONST)
        declarations = []
        
        while self.current_token().type == TokenType.IDENTIFIER:
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUAL)
            value = self.parse_expression()
            self.expect(TokenType.SEMICOLON)
            
            declarations.append(ConstDeclaration(name, value))
        
        return declarations
    
    def parse_procedure_declaration(self) -> ProcedureDeclaration:
        self.expect(TokenType.PROCEDURE)
        name = self.expect(TokenType.IDENTIFIER).value
        
        parameters = []
        if self.current_token().type == TokenType.LPAREN:
            parameters = self.parse_parameters()
        
        self.expect(TokenType.SEMICOLON)
        
        declarations = []
        while self.current_token().type in (TokenType.VAR, TokenType.CONST):
            declarations.extend(self.parse_declarations())
        
        block = self.parse_block()
        self.expect(TokenType.SEMICOLON)
        
        return ProcedureDeclaration(name, parameters, declarations, block)
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        self.expect(TokenType.FUNCTION)
        name = self.expect(TokenType.IDENTIFIER).value
        
        parameters = []
        if self.current_token().type == TokenType.LPAREN:
            parameters = self.parse_parameters()
        
        self.expect(TokenType.COLON)
        return_type = self.parse_type_spec()
        self.expect(TokenType.SEMICOLON)
        
        declarations = []
        while self.current_token().type in (TokenType.VAR, TokenType.CONST):
            declarations.extend(self.parse_declarations())
        
        block = self.parse_block()
        self.expect(TokenType.SEMICOLON)
        
        return FunctionDeclaration(name, parameters, return_type, declarations, block)
    
    def parse_parameters(self) -> List[Parameter]:
        self.expect(TokenType.LPAREN)
        parameters = []
        
        if self.current_token().type != TokenType.RPAREN:
            while True:
                is_var = False
                if self.current_token().type == TokenType.VAR:
                    is_var = True
                    self.advance()
                
                param_names = [self.expect(TokenType.IDENTIFIER).value]
                
                while self.current_token().type == TokenType.COMMA:
                    self.advance()
                    param_names.append(self.expect(TokenType.IDENTIFIER).value)
                
                self.expect(TokenType.COLON)
                type_spec = self.parse_type_spec()
                
                for param_name in param_names:
                    parameters.append(Parameter(param_name, type_spec, is_var))
                
                if self.current_token().type != TokenType.SEMICOLON:
                    break
                self.advance()
        
        self.expect(TokenType.RPAREN)
        return parameters
    
    def parse_type_spec(self) -> TypeSpec:
        token = self.current_token()
        
        if token.type == TokenType.ARRAY:
            return self.parse_array_type()
        elif token.type in (TokenType.INTEGER, TokenType.REAL, TokenType.BOOLEAN, 
                           TokenType.CHAR, TokenType.STRING):
            type_name = token.value
            self.advance()
            return SimpleType(type_name)
        elif token.type == TokenType.IDENTIFIER:
            type_name = token.value
            self.advance()
            return SimpleType(type_name)
        
        raise SyntaxError(f"Expected type specification at {token.line}:{token.column}")
    
    def parse_array_type(self) -> ArrayType:
        self.expect(TokenType.ARRAY)
        self.expect(TokenType.LBRACKET)
        index_type = self.parse_type_spec()
        self.expect(TokenType.RBRACKET)
        self.expect(TokenType.OF)
        element_type = self.parse_type_spec()
        
        return ArrayType(index_type, element_type)
    
    def parse_block(self) -> Block:
        self.expect(TokenType.BEGIN)
        statements = self.parse_statement_list()
        self.expect(TokenType.END)
        
        return Block(statements)
    
    def parse_statement_list(self) -> List[Statement]:
        statements = []
        
        if self.current_token().type != TokenType.END:
            statements.append(self.parse_statement())
            
            while self.current_token().type == TokenType.SEMICOLON:
                self.advance()
                if self.current_token().type in (TokenType.END, TokenType.UNTIL):
                    break
                statements.append(self.parse_statement())
        
        return statements
    
    def parse_statement(self) -> Statement:
        token = self.current_token()
        
        if token.type == TokenType.BEGIN:
            return self.parse_compound_statement()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.REPEAT:
            return self.parse_repeat_statement()
        elif token.type == TokenType.IDENTIFIER:
            # Could be assignment or procedure call
            return self.parse_assignment_or_call()
        else:
            # Empty statement
            return CompoundStatement([])
    
    def parse_compound_statement(self) -> CompoundStatement:
        self.expect(TokenType.BEGIN)
        statements = self.parse_statement_list()
        self.expect(TokenType.END)
        
        return CompoundStatement(statements)
    
    def parse_if_statement(self) -> IfStatement:
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        then_statement = self.parse_statement()
        
        else_statement = None
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            else_statement = self.parse_statement()
        
        return IfStatement(condition, then_statement, else_statement)
    
    def parse_while_statement(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.DO)
        body = self.parse_statement()
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        self.expect(TokenType.FOR)
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        start_value = self.parse_expression()
        
        downto = False
        if self.current_token().type == TokenType.TO:
            self.advance()
        elif self.current_token().type == TokenType.DOWNTO:
            self.advance()
            downto = True
        else:
            raise SyntaxError(f"Expected TO or DOWNTO at {self.current_token().line}:{self.current_token().column}")
        
        end_value = self.parse_expression()
        self.expect(TokenType.DO)
        body = self.parse_statement()
        
        return ForStatement(variable, start_value, end_value, body, downto)
    
    def parse_repeat_statement(self) -> RepeatStatement:
        self.expect(TokenType.REPEAT)
        statements = self.parse_statement_list()
        self.expect(TokenType.UNTIL)
        condition = self.parse_expression()
        
        return RepeatStatement(statements, condition)
    
    def parse_assignment_or_call(self) -> Statement:
        name = self.expect(TokenType.IDENTIFIER).value
        
        if self.current_token().type == TokenType.ASSIGN:
            # Assignment
            self.advance()
            variable = Variable(name)
            
            # Handle array indexing
            if self.current_token().type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                variable.index = index
            
            expression = self.parse_expression()
            return AssignmentStatement(variable, expression)
        elif self.current_token().type == TokenType.LPAREN:
            # Procedure call
            arguments = self.parse_arguments()
            
            # Handle built-in procedures
            if name.lower() == 'writeln':
                return WritelnStatement(arguments)
            elif name.lower() == 'write':
                return WriteStatement(arguments)
            elif name.lower() == 'readln':
                variables = [arg for arg in arguments if isinstance(arg, Variable)]
                return ReadlnStatement(variables)
            
            return ProcedureCallStatement(name, arguments)
        else:
            # Procedure call without arguments or variable reference
            return ProcedureCallStatement(name, [])
    
    def parse_arguments(self) -> List[Expression]:
        self.expect(TokenType.LPAREN)
        arguments = []
        
        if self.current_token().type != TokenType.RPAREN:
            arguments.append(self.parse_expression())
            
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                arguments.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN)
        return arguments
    
    def parse_expression(self) -> Expression:
        return self.parse_simple_expression()
    
    def parse_simple_expression(self) -> Expression:
        left = self.parse_term()
        
        while self.current_token().type in (TokenType.EQUAL, TokenType.NOT_EQUAL,
                                           TokenType.LESS_THAN, TokenType.LESS_EQUAL,
                                           TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                                           TokenType.PLUS, TokenType.MINUS, TokenType.OR):
            operator = self.current_token().value
            self.advance()
            right = self.parse_term()
            left = BinaryOp(left, operator, right)
        
        return left
    
    def parse_term(self) -> Expression:
        left = self.parse_factor()
        
        while self.current_token().type in (TokenType.MULTIPLY, TokenType.DIVIDE,
                                           TokenType.DIV, TokenType.MOD, TokenType.AND):
            operator = self.current_token().value
            self.advance()
            right = self.parse_factor()
            left = BinaryOp(left, operator, right)
        
        return left
    
    def parse_factor(self) -> Expression:
        token = self.current_token()
        
        if token.type == TokenType.INTEGER_LITERAL:
            self.advance()
            return IntegerLiteral(token.value)
        
        elif token.type == TokenType.REAL_LITERAL:
            self.advance()
            return RealLiteral(token.value)
        
        elif token.type == TokenType.STRING_LITERAL:
            self.advance()
            return StringLiteral(token.value)
        
        elif token.type == TokenType.TRUE:
            self.advance()
            return BooleanLiteral(True)
        
        elif token.type == TokenType.FALSE:
            self.advance()
            return BooleanLiteral(False)
        
        elif token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            
            if self.current_token().type == TokenType.LPAREN:
                # Function call
                arguments = self.parse_arguments()
                return FunctionCall(name, arguments)
            elif self.current_token().type == TokenType.LBRACKET:
                # Array access
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                return Variable(name, index)
            else:
                # Simple variable
                return Variable(name)
        
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        elif token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT):
            operator = token.value
            self.advance()
            operand = self.parse_factor()
            return UnaryOp(operator, operand)
        
        raise SyntaxError(f"Unexpected token {token.type.name} at {token.line}:{token.column}")
