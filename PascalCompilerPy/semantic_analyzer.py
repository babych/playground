"""
Pascal Compiler - Semantic Analyzer Module
Performs semantic analysis including type checking and symbol table management
"""

from typing import Dict, Optional, List, Any
from ast_nodes import *

class Symbol:
    def __init__(self, name: str, symbol_type: str, data_type: Optional[str] = None):
        self.name = name
        self.symbol_type = symbol_type  # 'variable', 'constant', 'procedure', 'function', 'parameter'
        self.data_type = data_type
        self.value = None
        self.parameters = []
        self.return_type = None

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
        
        # Initialize built-in types and functions
        if parent is None:
            self._init_builtins()
    
    def _init_builtins(self):
        # Built-in types
        for type_name in ['integer', 'real', 'boolean', 'char', 'string']:
            self.define(Symbol(type_name, 'type', type_name))
        
        # Built-in procedures
        self.define(Symbol('writeln', 'procedure'))
        self.define(Symbol('write', 'procedure'))
        self.define(Symbol('readln', 'procedure'))
        self.define(Symbol('read', 'procedure'))
    
    def define(self, symbol: Symbol):
        self.symbols[symbol.name.lower()] = symbol
    
    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        name_lower = name.lower()
        if name_lower in self.symbols:
            return self.symbols[name_lower]
        if not current_scope_only and self.parent:
            return self.parent.lookup(name)
        return None
    
    def exists(self, name: str, current_scope_only: bool = False) -> bool:
        return self.lookup(name, current_scope_only) is not None

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors: List[str] = []
        self.current_function = None
    
    def error(self, message: str):
        self.errors.append(message)
    
    def analyze(self, program: Program):
        self.visit_program(program)
        
        if self.errors:
            raise SemanticError('\n'.join(self.errors))
    
    def visit_program(self, node: Program):
        # Register all declarations first
        for decl in node.declarations:
            self.visit_declaration(decl, define_only=True)
        
        # Then analyze their bodies
        for decl in node.declarations:
            if isinstance(decl, (ProcedureDeclaration, FunctionDeclaration)):
                self.visit_declaration(decl, define_only=False)
        
        # Analyze main block
        self.visit_block(node.block)
    
    def visit_declaration(self, node: Declaration, define_only: bool = False):
        if isinstance(node, VarDeclaration):
            self.visit_var_declaration(node)
        elif isinstance(node, ConstDeclaration):
            self.visit_const_declaration(node)
        elif isinstance(node, ProcedureDeclaration):
            self.visit_procedure_declaration(node, define_only)
        elif isinstance(node, FunctionDeclaration):
            self.visit_function_declaration(node, define_only)
    
    def visit_var_declaration(self, node: VarDeclaration):
        type_name = self.get_type_name(node.type_spec)
        
        # Check if type exists
        if not self.current_scope.lookup(type_name):
            self.error(f"Undefined type: {type_name}")
            return
        
        for var_name in node.var_names:
            if self.current_scope.exists(var_name, current_scope_only=True):
                self.error(f"Variable '{var_name}' already declared in this scope")
                continue
            
            symbol = Symbol(var_name, 'variable', type_name)
            self.current_scope.define(symbol)
    
    def visit_const_declaration(self, node: ConstDeclaration):
        # Analyze the value expression
        value_type = self.visit_expression(node.value)
        
        if self.current_scope.exists(node.name, current_scope_only=True):
            self.error(f"Constant '{node.name}' already declared in this scope")
            return
        
        symbol = Symbol(node.name, 'constant', value_type)
        self.current_scope.define(symbol)
    
    def visit_procedure_declaration(self, node: ProcedureDeclaration, define_only: bool):
        if define_only:
            # Just register the procedure name
            if self.current_scope.exists(node.name, current_scope_only=True):
                self.error(f"Procedure '{node.name}' already declared in this scope")
                return
            
            symbol = Symbol(node.name, 'procedure')
            symbol.parameters = node.parameters
            self.current_scope.define(symbol)
        else:
            # Analyze the procedure body
            # Create new scope
            procedure_scope = SymbolTable(self.current_scope)
            old_scope = self.current_scope
            self.current_scope = procedure_scope
            
            # Add parameters to scope
            for param in node.parameters:
                type_name = self.get_type_name(param.type_spec)
                param_symbol = Symbol(param.name, 'parameter', type_name)
                self.current_scope.define(param_symbol)
            
            # Analyze declarations and block
            for decl in node.declarations:
                self.visit_declaration(decl)
            
            self.visit_block(node.block)
            
            # Restore scope
            self.current_scope = old_scope
    
    def visit_function_declaration(self, node: FunctionDeclaration, define_only: bool):
        if define_only:
            # Just register the function name
            if self.current_scope.exists(node.name, current_scope_only=True):
                self.error(f"Function '{node.name}' already declared in this scope")
                return
            
            return_type = self.get_type_name(node.return_type)
            symbol = Symbol(node.name, 'function', return_type)
            symbol.parameters = node.parameters
            symbol.return_type = return_type
            self.current_scope.define(symbol)
        else:
            # Analyze the function body
            function_scope = SymbolTable(self.current_scope)
            old_scope = self.current_scope
            old_function = self.current_function
            self.current_scope = function_scope
            self.current_function = node.name
            
            # Add function name as variable (for return value assignment)
            return_type = self.get_type_name(node.return_type)
            func_var = Symbol(node.name, 'variable', return_type)
            self.current_scope.define(func_var)
            
            # Add parameters to scope
            for param in node.parameters:
                type_name = self.get_type_name(param.type_spec)
                param_symbol = Symbol(param.name, 'parameter', type_name)
                self.current_scope.define(param_symbol)
            
            # Analyze declarations and block
            for decl in node.declarations:
                self.visit_declaration(decl)
            
            self.visit_block(node.block)
            
            # Restore scope
            self.current_scope = old_scope
            self.current_function = old_function
    
    def visit_block(self, node: Block):
        for statement in node.statements:
            self.visit_statement(statement)
    
    def visit_statement(self, node: Statement):
        if isinstance(node, AssignmentStatement):
            self.visit_assignment_statement(node)
        elif isinstance(node, IfStatement):
            self.visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            self.visit_while_statement(node)
        elif isinstance(node, ForStatement):
            self.visit_for_statement(node)
        elif isinstance(node, RepeatStatement):
            self.visit_repeat_statement(node)
        elif isinstance(node, CompoundStatement):
            self.visit_compound_statement(node)
        elif isinstance(node, ProcedureCallStatement):
            self.visit_procedure_call_statement(node)
        elif isinstance(node, WritelnStatement):
            for expr in node.expressions:
                self.visit_expression(expr)
        elif isinstance(node, WriteStatement):
            for expr in node.expressions:
                self.visit_expression(expr)
        elif isinstance(node, ReadlnStatement):
            for var in node.variables:
                self.visit_expression(var)
    
    def visit_assignment_statement(self, node: AssignmentStatement):
        var_type = self.visit_expression(node.variable)
        expr_type = self.visit_expression(node.expression)
        
        # Type checking
        if var_type and expr_type:
            if not self.types_compatible(var_type, expr_type):
                self.error(f"Type mismatch in assignment: cannot assign {expr_type} to {var_type}")
    
    def visit_if_statement(self, node: IfStatement):
        cond_type = self.visit_expression(node.condition)
        if cond_type and cond_type != 'boolean':
            self.error(f"Condition must be boolean, got {cond_type}")
        
        self.visit_statement(node.then_statement)
        if node.else_statement:
            self.visit_statement(node.else_statement)
    
    def visit_while_statement(self, node: WhileStatement):
        cond_type = self.visit_expression(node.condition)
        if cond_type and cond_type != 'boolean':
            self.error(f"Condition must be boolean, got {cond_type}")
        
        self.visit_statement(node.body)
    
    def visit_for_statement(self, node: ForStatement):
        # Check loop variable
        var_symbol = self.current_scope.lookup(node.variable)
        if not var_symbol:
            self.error(f"Undefined variable: {node.variable}")
        elif var_symbol.data_type != 'integer':
            self.error(f"For loop variable must be integer, got {var_symbol.data_type}")
        
        start_type = self.visit_expression(node.start_value)
        end_type = self.visit_expression(node.end_value)
        
        if start_type != 'integer':
            self.error(f"For loop start value must be integer, got {start_type}")
        if end_type != 'integer':
            self.error(f"For loop end value must be integer, got {end_type}")
        
        self.visit_statement(node.body)
    
    def visit_repeat_statement(self, node: RepeatStatement):
        for stmt in node.statements:
            self.visit_statement(stmt)
        
        cond_type = self.visit_expression(node.condition)
        if cond_type and cond_type != 'boolean':
            self.error(f"Condition must be boolean, got {cond_type}")
    
    def visit_compound_statement(self, node: CompoundStatement):
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_procedure_call_statement(self, node: ProcedureCallStatement):
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            self.error(f"Undefined procedure: {node.name}")
            return
        
        if symbol.symbol_type != 'procedure':
            self.error(f"'{node.name}' is not a procedure")
            return
        
        # Type check arguments
        for arg in node.arguments:
            self.visit_expression(arg)
    
    def visit_expression(self, node: Expression) -> Optional[str]:
        if isinstance(node, IntegerLiteral):
            return 'integer'
        
        elif isinstance(node, RealLiteral):
            return 'real'
        
        elif isinstance(node, StringLiteral):
            return 'string'
        
        elif isinstance(node, BooleanLiteral):
            return 'boolean'
        
        elif isinstance(node, Variable):
            symbol = self.current_scope.lookup(node.name)
            if not symbol:
                self.error(f"Undefined variable: {node.name}")
                return None
            
            if node.index:
                # Array access - check index type
                index_type = self.visit_expression(node.index)
                if index_type != 'integer':
                    self.error(f"Array index must be integer, got {index_type}")
            
            return symbol.data_type
        
        elif isinstance(node, BinaryOp):
            left_type = self.visit_expression(node.left)
            right_type = self.visit_expression(node.right)
            
            return self.check_binary_op(node.operator, left_type, right_type)
        
        elif isinstance(node, UnaryOp):
            operand_type = self.visit_expression(node.operand)
            
            if node.operator in ('+', '-'):
                if operand_type not in ('integer', 'real'):
                    self.error(f"Unary {node.operator} requires numeric operand")
                return operand_type
            elif node.operator == 'not':
                if operand_type != 'boolean':
                    self.error(f"NOT requires boolean operand")
                return 'boolean'
        
        elif isinstance(node, FunctionCall):
            symbol = self.current_scope.lookup(node.name)
            if not symbol:
                self.error(f"Undefined function: {node.name}")
                return None
            
            if symbol.symbol_type != 'function':
                self.error(f"'{node.name}' is not a function")
                return None
            
            # Type check arguments
            for arg in node.arguments:
                self.visit_expression(arg)
            
            return symbol.return_type
        
        return None
    
    def check_binary_op(self, operator: str, left_type: Optional[str], 
                       right_type: Optional[str]) -> Optional[str]:
        if not left_type or not right_type:
            return None
        
        # Arithmetic operators
        if operator in ('+', '-', '*', '/'):
            if left_type in ('integer', 'real') and right_type in ('integer', 'real'):
                if left_type == 'real' or right_type == 'real':
                    return 'real'
                return 'integer'
            else:
                self.error(f"Operator {operator} requires numeric operands")
                return None
        
        # Integer division and modulo
        elif operator in ('div', 'mod'):
            if left_type == 'integer' and right_type == 'integer':
                return 'integer'
            else:
                self.error(f"Operator {operator} requires integer operands")
                return None
        
        # Comparison operators
        elif operator in ('=', '<>', '<', '<=', '>', '>='):
            if self.types_compatible(left_type, right_type):
                return 'boolean'
            else:
                self.error(f"Cannot compare {left_type} with {right_type}")
                return 'boolean'
        
        # Logical operators
        elif operator in ('and', 'or'):
            if left_type == 'boolean' and right_type == 'boolean':
                return 'boolean'
            else:
                self.error(f"Logical operator {operator} requires boolean operands")
                return 'boolean'
        
        return None
    
    def types_compatible(self, type1: str, type2: str) -> bool:
        if type1 == type2:
            return True
        # Allow integer to real conversion
        if (type1 == 'real' and type2 == 'integer') or \
           (type1 == 'integer' and type2 == 'real'):
            return True
        return False
    
    def get_type_name(self, type_spec: TypeSpec) -> str:
        if isinstance(type_spec, SimpleType):
            return type_spec.type_name
        elif isinstance(type_spec, ArrayType):
            element_type = self.get_type_name(type_spec.element_type)
            return f"array of {element_type}"
        elif isinstance(type_spec, RecordType):
            return "record"
        return "unknown"

class SemanticError(Exception):
    pass
