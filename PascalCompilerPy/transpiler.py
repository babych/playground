#!/usr/bin/env python3
"""
Three-Address Code to Python Transpiler
Converts intermediate code to executable Python code
"""

import sys
from pathlib import Path

class PythonTranspiler:
    def __init__(self):
        self.python_code = []
        self.strings = {}
        self.indent = 0
        
    def transpile(self, three_addr_code):
        """Convert three-address code to Python"""
        lines = [line.strip() for line in three_addr_code if line.strip()]
        
        # Add imports
        self.python_code.append("#!/usr/bin/env python3")
        self.python_code.append("# Generated from Pascal compiler")
        self.python_code.append("")
        
        # Parse string literals first
        in_strings = False
        for line in lines:
            if line == '# String literal data':
                in_strings = True
                continue
            if in_strings and line.startswith('str'):
                # Parse: str0: .string "Hello"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    value = parts[1].replace('.string', '').strip().strip('"')
                    self.strings[label] = value
        
        # Generate Python code
        self.python_code.append("def main():")
        self.indent = 1
        
        for line in lines:
            # Skip comments, string literals, and empty lines
            if (line.startswith('#') or 
                line.startswith('str') or 
                line == '# String literal data' or 
                not line):
                continue
            
            # Skip main label
            if line == 'main:':
                continue
            
            self.convert_instruction(line)
        
        # Add main call
        self.python_code.append("")
        self.python_code.append("if __name__ == '__main__':")
        self.python_code.append("    main()")
        
        return '\n'.join(self.python_code)
    
    def convert_instruction(self, instruction):
        """Convert a single instruction to Python"""
        ind = "    " * self.indent
        
        # Halt
        if instruction == 'halt':
            self.python_code.append(f"{ind}pass  # halt")
            return
        
        # Write
        if instruction.startswith('write '):
            expr = instruction[6:].strip()
            value = self.convert_expression(expr)
            self.python_code.append(f"{ind}print({value}, end='')")
            return
        
        # Writeln
        if instruction == 'writeln':
            self.python_code.append(f"{ind}print()")
            return
        
        # Read
        if instruction.startswith('read '):
            var = instruction[5:].strip()
            self.python_code.append(f"{ind}{var} = int(input())")
            return
        
        # Readln
        if instruction == 'readln':
            self.python_code.append(f"{ind}input()  # readln")
            return
        
        # Assignment
        if '=' in instruction and not any(instruction.startswith(op) for op in ['if_', 'goto']):
            parts = instruction.split('=', 1)
            left = parts[0].strip()
            right = parts[1].strip()
            
            # Convert expression
            right_py = self.convert_expression(right)
            
            # Handle array assignment
            if '[' in left:
                self.python_code.append(f"{ind}{left} = {right_py}")
            else:
                self.python_code.append(f"{ind}{left} = {right_py}")
            return
        
        # Labels (convert to comments in Python, as we'll restructure control flow)
        if instruction.endswith(':') and not instruction.startswith('#'):
            label = instruction[:-1]
            self.python_code.append(f"{ind}# Label: {label}")
            return
        
        # Goto (simplified - just add comment)
        if instruction.startswith('goto '):
            label = instruction[5:].strip()
            self.python_code.append(f"{ind}# goto {label} (not directly supported in Python)")
            return
        
        # Conditional jumps (simplified)
        if instruction.startswith('if_true '):
            parts = instruction.split()
            condition = self.convert_expression(parts[1])
            label = parts[3]
            self.python_code.append(f"{ind}if {condition}:")
            self.python_code.append(f"{ind}    pass  # goto {label}")
            return
        
        if instruction.startswith('if_false '):
            parts = instruction.split()
            condition = self.convert_expression(parts[1])
            label = parts[3]
            self.python_code.append(f"{ind}if not ({condition}):")
            self.python_code.append(f"{ind}    pass  # goto {label}")
            return
        
        # Call
        if instruction.startswith('call '):
            self.python_code.append(f"{ind}# {instruction}")
            return
        
        # Return
        if instruction == 'return':
            self.python_code.append(f"{ind}return")
            return
        
        # Unknown instruction - add as comment
        self.python_code.append(f"{ind}# {instruction}")
    
    def convert_expression(self, expr):
        """Convert an expression to Python"""
        expr = expr.strip()
        
        # String literal
        if expr.startswith('str'):
            return f'"{self.strings.get(expr, expr)}"'
        
        # Replace operators
        expr = expr.replace('&&', ' and ')
        expr = expr.replace('||', ' or ')
        expr = expr.replace('!', ' not ')
        expr = expr.replace('==', '==')
        
        return expr

def main():
    if len(sys.argv) < 2:
        print("Usage: python transpiler.py <three-address-code-file> [output.py]")
        print("\nConverts three-address intermediate code to Python")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Determine output file
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.with_suffix('.py')
    
    # Read three-address code
    with open(input_file, 'r') as f:
        code = f.readlines()
    
    # Transpile
    transpiler = PythonTranspiler()
    python_code = transpiler.transpile(code)
    
    # Write Python code
    with open(output_file, 'w') as f:
        f.write(python_code)
    
    print(f"Successfully transpiled to {output_file}")
    print(f"\nTo run:")
    print(f"  python {output_file}")

if __name__ == '__main__':
    main()
