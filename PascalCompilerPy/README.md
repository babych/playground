# Pascal Compiler

A complete Pascal compiler written in Python that translates Pascal source code into three-address intermediate code. This compiler implements all major phases of compilation: lexical analysis, parsing, semantic analysis, and code generation.

## Features

### Supported Pascal Features

#### Data Types
- **Integer**: Whole numbers
- **Real**: Floating-point numbers
- **Boolean**: True/False values
- **Char**: Single characters
- **String**: Text strings
- **Array**: Single and multi-dimensional arrays

#### Control Structures
- **IF-THEN-ELSE**: Conditional statements
- **WHILE-DO**: Pre-test loops
- **FOR-TO/DOWNTO-DO**: Counted loops
- **REPEAT-UNTIL**: Post-test loops
- **BEGIN-END**: Compound statements

#### Procedures and Functions
- Procedure declarations with parameters
- Function declarations with return values
- Variable (VAR) and value parameters
- Local variable declarations
- Nested declarations

#### Operators
- **Arithmetic**: +, -, *, /, DIV, MOD
- **Comparison**: =, <>, <, <=, >, >=
- **Logical**: AND, OR, NOT
- **Assignment**: :=

#### Built-in Procedures
- `WRITELN`: Output with newline
- `WRITE`: Output without newline
- `READLN`: Input with newline
- `READ`: Input without newline

## Architecture

The compiler consists of four main phases:

### 1. Lexical Analysis (Lexer)
- Tokenizes the source code
- Recognizes keywords, identifiers, literals, operators, and delimiters
- Handles comments: `{ }`, `(* *)`, and `//`
- Tracks line and column numbers for error reporting

### 2. Syntax Analysis (Parser)
- Builds an Abstract Syntax Tree (AST) from tokens
- Implements recursive descent parsing
- Enforces Pascal grammar rules
- Detects syntax errors with precise location

### 3. Semantic Analysis
- Type checking for expressions and assignments
- Symbol table management with scoping
- Checks for undefined variables and functions
- Validates function/procedure calls and parameter types
- Detects type mismatches and incompatible operations

### 4. Code Generation
- Generates three-address intermediate code
- Optimizes temporary variable usage
- Handles control flow with labels
- Manages string literals
- Produces human-readable assembly-like code

## Installation

No installation required! The compiler is written in pure Python 3 with no external dependencies.

### Requirements
- Python 3.6 or higher

## Usage

### Basic Usage

Compile a Pascal program and display the output:
```bash
python3 pascal_compiler.py program.pas
```

### Save Output to File

Compile and save intermediate code to a file:
```bash
python3 pascal_compiler.py program.pas -o output.txt
```

### Verbose Mode

Show detailed compilation phases:
```bash
python3 pascal_compiler.py program.pas -v
```

### Command-Line Options

```
usage: pascal_compiler.py [-h] [-o OUTPUT] [-v] input

Pascal Compiler - Compiles Pascal source code to intermediate code

positional arguments:
  input                 Input Pascal source file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file for intermediate code
  -v, --verbose         Enable verbose output
```

## Examples

### Example 1: Simple Arithmetic

**Input (simple.pas):**
```pascal
program SimpleTest;
var
    x, y, z: integer;
    result: integer;

begin
    x := 10;
    y := 20;
    z := x + y;
    result := z * 2;
    writeln(result)
end.
```

**Output:**
```
# Program: SimpleTest
# String literals
# Variable: x
# Variable: y
# Variable: z
# Variable: result

# Main program
main:
x = 10
y = 20
t0 = x + y
z = t0
t1 = z * 2
result = t1
write result
writeln
halt
```

### Example 2: Control Structures

**Input (control.pas):**
```pascal
program ControlStructures;
var
    i, sum, factorial: integer;

begin
    { Test if statement }
    i := 15;
    if i > 10 then
        writeln('i is greater than 10')
    else
        writeln('i is less than or equal to 10');
    
    { Test while loop }
    sum := 0;
    i := 1;
    while i <= 10 do
    begin
        sum := sum + i;
        i := i + 1
    end;
    writeln('Sum: ', sum);
    
    { Test for loop }
    factorial := 1;
    for i := 1 to 5 do
        factorial := factorial * i;
    writeln('Factorial: ', factorial)
end.
```

### Example 3: Procedures and Functions

**Input (functions.pas):**
```pascal
program ProceduresAndFunctions;
var
    a, b, result: integer;

procedure Swap(var x, y: integer);
var
    temp: integer;
begin
    temp := x;
    x := y;
    y := temp
end;

function Add(x, y: integer): integer;
begin
    Add := x + y
end;

function Factorial(n: integer): integer;
var
    i, result: integer;
begin
    result := 1;
    for i := 1 to n do
        result := result * i;
    Factorial := result
end;

begin
    a := 5;
    b := 10;
    
    writeln('Before swap: a=', a, ', b=', b);
    Swap(a, b);
    writeln('After swap: a=', a, ', b=', b);
    
    result := Add(a, b);
    writeln('Add result: ', result);
    
    result := Factorial(5);
    writeln('Factorial(5) = ', result)
end.
```

## Intermediate Code Format

The generated intermediate code uses a three-address code format with the following instructions:

### Assignment
```
variable = value
variable = expression
```

### Arithmetic Operations
```
temp = operand1 + operand2
temp = operand1 - operand2
temp = operand1 * operand2
temp = operand1 / operand2
```

### Comparison Operations
```
temp = operand1 == operand2
temp = operand1 != operand2
temp = operand1 < operand2
temp = operand1 <= operand2
temp = operand1 > operand2
temp = operand1 >= operand2
```

### Control Flow
```
label:                    # Define a label
goto label                # Unconditional jump
if_true condition goto L  # Conditional jump if true
if_false condition goto L # Conditional jump if false
```

### Procedure/Function Calls
```
call procedure_name, arg1, arg2
result = call function_name, arg1, arg2
return
```

### I/O Operations
```
write expression          # Output expression
writeln                   # Output newline
read variable            # Input to variable
readln                   # Input newline
```

### Array Access
```
temp = array[index]       # Array read
array[index] = value      # Array write
```

## File Structure

```
pascal_compiler/
├── pascal_compiler.py      # Main compiler driver
├── lexer.py               # Lexical analyzer
├── parser.py              # Syntax analyzer
├── ast_nodes.py           # AST node definitions
├── semantic_analyzer.py   # Semantic analyzer
├── code_generator.py      # Code generator
├── test_simple.pas        # Simple test program
├── test_control.pas       # Control structures test
├── test_functions.pas     # Procedures/functions test
└── README.md             # This file
```

## Error Handling

The compiler provides detailed error messages with line and column information:

### Syntax Errors
```
Syntax Error: Expected SEMICOLON, got IDENTIFIER at 5:10
```

### Semantic Errors
```
Semantic Error: Undefined variable: count
Type mismatch in assignment: cannot assign real to integer
```

### Lexical Errors
```
Syntax Error: Unexpected character '#' at 3:5
Syntax Error: Unterminated string at 7:12
```

## Testing

Three comprehensive test programs are included:

1. **test_simple.pas**: Basic arithmetic and variable assignment
2. **test_control.pas**: Control structures (if, while, for, repeat)
3. **test_functions.pas**: Procedures, functions, and parameters

Run all tests:
```bash
python3 pascal_compiler.py test_simple.pas -v
python3 pascal_compiler.py test_control.pas -v
python3 pascal_compiler.py test_functions.pas -v
```

## Limitations

The following Pascal features are not currently implemented:
- Record type field access
- Type declarations (TYPE section)
- Pointer types
- Sets
- File I/O operations
- Units and USES clause
- Object-oriented features (classes, objects)

## Future Enhancements

Potential improvements:
1. Generate actual executable code (x86, ARM, etc.)
2. Optimization passes (constant folding, dead code elimination)
3. More comprehensive type system
4. Better error recovery
5. Debug symbol generation
6. Standard library functions

## Technical Details

### Grammar

The compiler implements a subset of standard Pascal grammar:

```
program       → PROGRAM identifier SEMICOLON declarations block DOT
declarations  → (var_decl | const_decl | proc_decl | func_decl)*
var_decl      → VAR (identifier_list COLON type SEMICOLON)+
block         → BEGIN statement_list END
statement     → assignment | if_stmt | while_stmt | for_stmt | 
                repeat_stmt | compound_stmt | proc_call
expression    → simple_expr (relop simple_expr)?
simple_expr   → term ((PLUS | MINUS | OR) term)*
term          → factor ((MULTIPLY | DIVIDE | DIV | MOD | AND) factor)*
factor        → INTEGER | REAL | STRING | BOOLEAN | identifier |
                func_call | LPAREN expression RPAREN |
                (PLUS | MINUS | NOT) factor
```

### Symbol Table

The compiler uses a hierarchical symbol table with:
- Global scope for program-level declarations
- Local scopes for procedures and functions
- Parent pointers for scope chain lookup
- Symbol attributes: name, type, kind, parameters

### Type System

Type checking ensures:
- Assignment compatibility
- Operator type requirements
- Function return type matching
- Parameter type matching
- Array index types

## License

This Pascal compiler is provided as-is for educational purposes.

## Author

Created as a demonstration of compiler construction techniques.

## Acknowledgments

- Based on standard Pascal language specification
- Inspired by classic compiler design principles
- Uses traditional compiler phases architecture
