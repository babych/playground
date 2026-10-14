"""
Pascal Compiler - Lexer Module
Tokenizes Pascal source code into a stream of tokens
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    PROGRAM = auto()
    VAR = auto()
    BEGIN = auto()
    END = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    TO = auto()
    DOWNTO = auto()
    REPEAT = auto()
    UNTIL = auto()
    PROCEDURE = auto()
    FUNCTION = auto()
    INTEGER = auto()
    REAL = auto()
    BOOLEAN = auto()
    CHAR = auto()
    STRING = auto()
    ARRAY = auto()
    OF = auto()
    CONST = auto()
    TYPE = auto()
    RECORD = auto()
    CASE = auto()
    DIV = auto()
    MOD = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Identifiers and literals
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    REAL_LITERAL = auto()
    STRING_LITERAL = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL = auto()
    
    # Delimiters
    SEMICOLON = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    DOTDOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"

class Lexer:
    KEYWORDS = {
        'program': TokenType.PROGRAM,
        'var': TokenType.VAR,
        'begin': TokenType.BEGIN,
        'end': TokenType.END,
        'if': TokenType.IF,
        'then': TokenType.THEN,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'do': TokenType.DO,
        'for': TokenType.FOR,
        'to': TokenType.TO,
        'downto': TokenType.DOWNTO,
        'repeat': TokenType.REPEAT,
        'until': TokenType.UNTIL,
        'procedure': TokenType.PROCEDURE,
        'function': TokenType.FUNCTION,
        'integer': TokenType.INTEGER,
        'real': TokenType.REAL,
        'boolean': TokenType.BOOLEAN,
        'char': TokenType.CHAR,
        'string': TokenType.STRING,
        'array': TokenType.ARRAY,
        'of': TokenType.OF,
        'const': TokenType.CONST,
        'type': TokenType.TYPE,
        'record': TokenType.RECORD,
        'case': TokenType.CASE,
        'div': TokenType.DIV,
        'mod': TokenType.MOD,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        # Skip { } comments
        if self.current_char() == '{':
            self.advance()
            while self.current_char() and self.current_char() != '}':
                self.advance()
            if self.current_char() == '}':
                self.advance()
            return True
        
        # Skip (* *) comments
        if self.current_char() == '(' and self.peek_char() == '*':
            self.advance()
            self.advance()
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == ')':
                    self.advance()
                    self.advance()
                    break
                self.advance()
            return True
        
        # Skip // comments
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            return True
        
        return False
    
    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        num_str = ''
        is_real = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                # Check for .. (range operator)
                if self.peek_char() == '.':
                    break
                if is_real:
                    raise SyntaxError(f"Invalid number at {self.line}:{self.column}")
                is_real = True
            num_str += self.current_char()
            self.advance()
        
        if is_real:
            return Token(TokenType.REAL_LITERAL, float(num_str), start_line, start_column)
        else:
            return Token(TokenType.INTEGER_LITERAL, int(num_str), start_line, start_column)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_column = self.column
        identifier = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()
        
        identifier_lower = identifier.lower()
        token_type = self.KEYWORDS.get(identifier_lower, TokenType.IDENTIFIER)
        value = identifier if token_type == TokenType.IDENTIFIER else identifier_lower
        
        return Token(token_type, value, start_line, start_column)
    
    def read_string(self) -> Token:
        start_line = self.line
        start_column = self.column
        quote_char = self.current_char()
        self.advance()
        
        string_value = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    escape_char = self.current_char()
                    if escape_char == 'n':
                        string_value += '\n'
                    elif escape_char == 't':
                        string_value += '\t'
                    elif escape_char == 'r':
                        string_value += '\r'
                    else:
                        string_value += escape_char
                    self.advance()
            else:
                string_value += self.current_char()
                self.advance()
        
        if self.current_char() != quote_char:
            raise SyntaxError(f"Unterminated string at {start_line}:{start_column}")
        
        self.advance()
        return Token(TokenType.STRING_LITERAL, string_value, start_line, start_column)
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if self.pos >= len(self.source):
                break
            
            if self.skip_comment():
                continue
            
            char = self.current_char()
            line = self.line
            column = self.column
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Strings
            if char in ('"', "'"):
                self.tokens.append(self.read_string())
                continue
            
            # Two-character operators
            if char == ':' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, ':=', line, column))
                continue
            
            if char == '<' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', line, column))
                continue
            
            if char == '>' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', line, column))
                continue
            
            if char == '<' and self.peek_char() == '>':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, '<>', line, column))
                continue
            
            if char == '.' and self.peek_char() == '.':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.DOTDOT, '..', line, column))
                continue
            
            # Single-character operators and delimiters
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '=': TokenType.EQUAL,
                '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN,
                ';': TokenType.SEMICOLON,
                ':': TokenType.COLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
            }
            
            if char in single_char_tokens:
                self.advance()
                self.tokens.append(Token(single_char_tokens[char], char, line, column))
                continue
            
            raise SyntaxError(f"Unexpected character '{char}' at {line}:{column}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
