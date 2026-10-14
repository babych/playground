"""
Pascal Compiler - Code Generator Module
Generates three-address intermediate code from the AST
"""

from typing import List, Dict, Optional, Any
from ast_nodes import *

class CodeGenerator:
    def __init__(self):
        self.code: List[str] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.string_literals: Dict[str, str] = {}
        self.string_counter = 0
    
    def new_temp(self) -> str:
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, instruction: str):
        self.code.append(instruction)
    
    def generate(self, program: Program) -> List[str]:
        self.visit_program(program)
        return self.code
    
    def visit_program(self, node: Program):
        self.emit(f"# Program: {node.name}")
        self.emit("# String literals")
        
        # Generate code for declarations
        for decl in node.declarations:
            self.visit_declaration(decl)
        
        self.emit("")
        self.emit("# Main program")
        self.emit("main:")
        
        # Generate code for main block
        self.visit_block(node.block)
        
        self.emit("halt")
        self.emit("")
        
        # Add string literal definitions
        if self.string_literals:
            self.emit("# String literal data")
            for label, value in self.string_literals.items():
                self.emit(f"{label}: .string \"{value}\"")
    
    def visit_declaration(self, node: Declaration):
        if isinstance(node, VarDeclaration):
            self.visit_var_declaration(node)
        elif isinstance(node, ConstDeclaration):
            self.visit_const_declaration(node)
        elif isinstance(node, ProcedureDeclaration):
            self.visit_procedure_declaration(node)
        elif isinstance(node, FunctionDeclaration):
            self.visit_function_declaration(node)
    
    def visit_var_declaration(self, node: VarDeclaration):
        for var_name in node.var_names:
            self.emit(f"# Variable: {var_name}")
    
    def visit_const_declaration(self, node: ConstDeclaration):
        value_temp = self.visit_expression(node.value)
        self.emit(f"# Constant: {node.name} = {value_temp}")
    
    def visit_procedure_declaration(self, node: ProcedureDeclaration):
        self.emit("")
        self.emit(f"# Procedure: {node.name}")
        self.emit(f"{node.name}:")
        
        # Save parameters
        for i, param in enumerate(node.parameters):
            self.emit(f"# Parameter {param.name}")
        
        # Generate code for procedure body
        for decl in node.declarations:
            self.visit_declaration(decl)
        
        self.visit_block(node.block)
        self.emit("return")
        self.emit("")
    
    def visit_function_declaration(self, node: FunctionDeclaration):
        self.emit("")
        self.emit(f"# Function: {node.name}")
        self.emit(f"{node.name}:")
        
        # Save parameters
        for i, param in enumerate(node.parameters):
            self.emit(f"# Parameter {param.name}")
        
        # Generate code for function body
        for decl in node.declarations:
            self.visit_declaration(decl)
        
        self.visit_block(node.block)
        self.emit("return")
        self.emit("")
    
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
            self.visit_writeln_statement(node)
        elif isinstance(node, WriteStatement):
            self.visit_write_statement(node)
        elif isinstance(node, ReadlnStatement):
            self.visit_readln_statement(node)
    
    def visit_assignment_statement(self, node: AssignmentStatement):
        expr_temp = self.visit_expression(node.expression)
        
        if node.variable.index:
            # Array assignment
            index_temp = self.visit_expression(node.variable.index)
            self.emit(f"{node.variable.name}[{index_temp}] = {expr_temp}")
        else:
            self.emit(f"{node.variable.name} = {expr_temp}")
    
    def visit_if_statement(self, node: IfStatement):
        cond_temp = self.visit_expression(node.condition)
        else_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"if_false {cond_temp} goto {else_label}")
        self.visit_statement(node.then_statement)
        
        if node.else_statement:
            self.emit(f"goto {end_label}")
            self.emit(f"{else_label}:")
            self.visit_statement(node.else_statement)
            self.emit(f"{end_label}:")
        else:
            self.emit(f"{else_label}:")
    
    def visit_while_statement(self, node: WhileStatement):
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"{start_label}:")
        cond_temp = self.visit_expression(node.condition)
        self.emit(f"if_false {cond_temp} goto {end_label}")
        
        self.visit_statement(node.body)
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")
    
    def visit_for_statement(self, node: ForStatement):
        start_temp = self.visit_expression(node.start_value)
        end_temp = self.visit_expression(node.end_value)
        
        self.emit(f"{node.variable} = {start_temp}")
        
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"{start_label}:")
        
        # Check loop condition
        cond_temp = self.new_temp()
        if node.downto:
            self.emit(f"{cond_temp} = {node.variable} < {end_temp}")
        else:
            self.emit(f"{cond_temp} = {node.variable} > {end_temp}")
        self.emit(f"if_true {cond_temp} goto {end_label}")
        
        # Loop body
        self.visit_statement(node.body)
        
        # Increment/decrement loop variable
        if node.downto:
            self.emit(f"{node.variable} = {node.variable} - 1")
        else:
            self.emit(f"{node.variable} = {node.variable} + 1")
        
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")
    
    def visit_repeat_statement(self, node: RepeatStatement):
        start_label = self.new_label()
        
        self.emit(f"{start_label}:")
        for stmt in node.statements:
            self.visit_statement(stmt)
        
        cond_temp = self.visit_expression(node.condition)
        self.emit(f"if_false {cond_temp} goto {start_label}")
    
    def visit_compound_statement(self, node: CompoundStatement):
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_procedure_call_statement(self, node: ProcedureCallStatement):
        # Evaluate arguments
        arg_temps = []
        for arg in node.arguments:
            arg_temp = self.visit_expression(arg)
            arg_temps.append(arg_temp)
        
        # Generate call
        if arg_temps:
            args_str = ", ".join(arg_temps)
            self.emit(f"call {node.name}, {args_str}")
        else:
            self.emit(f"call {node.name}")
    
    def visit_writeln_statement(self, node: WritelnStatement):
        for expr in node.expressions:
            expr_temp = self.visit_expression(expr)
            self.emit(f"write {expr_temp}")
        self.emit("writeln")
    
    def visit_write_statement(self, node: WriteStatement):
        for expr in node.expressions:
            expr_temp = self.visit_expression(expr)
            self.emit(f"write {expr_temp}")
    
    def visit_readln_statement(self, node: ReadlnStatement):
        for var in node.variables:
            self.emit(f"read {var.name}")
        self.emit("readln")
    
    def visit_expression(self, node: Expression) -> str:
        if isinstance(node, IntegerLiteral):
            return str(node.value)
        
        elif isinstance(node, RealLiteral):
            return str(node.value)
        
        elif isinstance(node, StringLiteral):
            # Store string literal
            label = f"str{self.string_counter}"
            self.string_counter += 1
            self.string_literals[label] = node.value
            return label
        
        elif isinstance(node, BooleanLiteral):
            return "1" if node.value else "0"
        
        elif isinstance(node, Variable):
            if node.index:
                index_temp = self.visit_expression(node.index)
                temp = self.new_temp()
                self.emit(f"{temp} = {node.name}[{index_temp}]")
                return temp
            else:
                return node.name
        
        elif isinstance(node, BinaryOp):
            left_temp = self.visit_expression(node.left)
            right_temp = self.visit_expression(node.right)
            result_temp = self.new_temp()
            
            op_map = {
                '+': '+', '-': '-', '*': '*', '/': '/',
                'div': '/', 'mod': '%',
                '=': '==', '<>': '!=',
                '<': '<', '<=': '<=', '>': '>', '>=': '>=',
                'and': '&&', 'or': '||'
            }
            
            op = op_map.get(node.operator, node.operator)
            self.emit(f"{result_temp} = {left_temp} {op} {right_temp}")
            return result_temp
        
        elif isinstance(node, UnaryOp):
            operand_temp = self.visit_expression(node.operand)
            result_temp = self.new_temp()
            
            if node.operator == '-':
                self.emit(f"{result_temp} = -{operand_temp}")
            elif node.operator == '+':
                self.emit(f"{result_temp} = {operand_temp}")
            elif node.operator == 'not':
                self.emit(f"{result_temp} = !{operand_temp}")
            
            return result_temp
        
        elif isinstance(node, FunctionCall):
            # Evaluate arguments
            arg_temps = []
            for arg in node.arguments:
                arg_temp = self.visit_expression(arg)
                arg_temps.append(arg_temp)
            
            result_temp = self.new_temp()
            if arg_temps:
                args_str = ", ".join(arg_temps)
                self.emit(f"{result_temp} = call {node.name}, {args_str}")
            else:
                self.emit(f"{result_temp} = call {node.name}")
            
            return result_temp
        
        return "0"
