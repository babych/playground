"""
Pascal Compiler - AST Node Definitions
Defines all Abstract Syntax Tree node types
"""

from dataclasses import dataclass
from typing import List, Optional, Any

# Base AST Node
@dataclass
class ASTNode:
    pass

# Program structure
@dataclass
class Program(ASTNode):
    name: str
    declarations: List['Declaration']
    block: 'Block'

@dataclass
class Block(ASTNode):
    statements: List['Statement']

# Declarations
@dataclass
class Declaration(ASTNode):
    pass

@dataclass
class VarDeclaration(Declaration):
    var_names: List[str]
    type_spec: 'TypeSpec'

@dataclass
class ConstDeclaration(Declaration):
    name: str
    value: 'Expression'

@dataclass
class ProcedureDeclaration(Declaration):
    name: str
    parameters: List['Parameter']
    declarations: List[Declaration]
    block: Block

@dataclass
class FunctionDeclaration(Declaration):
    name: str
    parameters: List['Parameter']
    return_type: 'TypeSpec'
    declarations: List[Declaration]
    block: Block

@dataclass
class Parameter(ASTNode):
    name: str
    type_spec: 'TypeSpec'
    is_var: bool = False

# Type specifications
@dataclass
class TypeSpec(ASTNode):
    pass

@dataclass
class SimpleType(TypeSpec):
    type_name: str  # integer, real, boolean, char, string

@dataclass
class ArrayType(TypeSpec):
    index_type: TypeSpec
    element_type: TypeSpec

@dataclass
class RecordType(TypeSpec):
    fields: List[VarDeclaration]

# Statements
@dataclass
class Statement(ASTNode):
    pass

@dataclass
class AssignmentStatement(Statement):
    variable: 'Variable'
    expression: 'Expression'

@dataclass
class IfStatement(Statement):
    condition: 'Expression'
    then_statement: Statement
    else_statement: Optional[Statement] = None

@dataclass
class WhileStatement(Statement):
    condition: 'Expression'
    body: Statement

@dataclass
class ForStatement(Statement):
    variable: str
    start_value: 'Expression'
    end_value: 'Expression'
    body: Statement
    downto: bool = False

@dataclass
class RepeatStatement(Statement):
    statements: List[Statement]
    condition: 'Expression'

@dataclass
class CompoundStatement(Statement):
    statements: List[Statement]

@dataclass
class ProcedureCallStatement(Statement):
    name: str
    arguments: List['Expression']

@dataclass
class WritelnStatement(Statement):
    expressions: List['Expression']

@dataclass
class WriteStatement(Statement):
    expressions: List['Expression']

@dataclass
class ReadlnStatement(Statement):
    variables: List['Variable']

# Expressions
@dataclass
class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression

@dataclass
class IntegerLiteral(Expression):
    value: int

@dataclass
class RealLiteral(Expression):
    value: float

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class BooleanLiteral(Expression):
    value: bool

@dataclass
class Variable(Expression):
    name: str
    index: Optional[Expression] = None  # For array access
    field: Optional[str] = None  # For record field access

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]
