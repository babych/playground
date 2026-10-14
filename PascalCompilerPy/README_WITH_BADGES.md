# Pascal Compiler

![CI Status](https://github.com/babych/PascalCompilerPy/workflows/Pascal%20Compiler%20CI/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

A full-featured Pascal language compiler written in Python. Supports all core Pascal constructs and generates intermediate code in three-address code format.

## 🚀 Quick Start

### Windows
python pascal_compiler.py test_simple.pas

or double-click `run_tests_windows.bat`

### Linux / macOS
python3 pascal_compiler.py test_simple.pas

or run:
python3 run_tests.py

## ✨ Features

- Full Pascal syntax support
- Data types: integer, real, boolean, string, char, array
- Control structures: if/then/else, while, for, repeat/until
- Procedures and functions with parameters
- Semantic analysis and type checking
- Intermediate code generation
- Detailed error messages
- Cross-platform (Windows, Linux, macOS)

## 📋 Requirements

- Python 3.8 or newer
- No additional dependencies required

## 🔧 Installation

1. Clone the repository:
git clone https://github.com/babych/PascalCompilerPy.git
cd pascal-compiler

2. Done. The compiler does not require installation.

## 📖 Usage

### Basic compilation
python pascal_compiler.py program.pas

### Verbose output
python pascal_compiler.py program.pas -v

### Save output to file
python pascal_compiler.py program.pas -o output.txt

### Help
python pascal_compiler.py -h

## 📝 Examples

### Simple example
program Hello;
var
    x: integer;
begin
    x := 42;
    writeln('The answer is: ', x)
end.

### Functions and procedures
program MathExample;

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
    writeln('5! = ', Factorial(5))
end.

More examples can be found in the test_*.pas files.

## 🧪 Testing

Run all tests:
python run_tests.py

Individual tests:
python pascal_compiler.py test_simple.pas
python pascal_compiler.py test_control.pas
python pascal_compiler.py test_functions.pas
python pascal_compiler.py test_errors.pas

## 🏗️ Architecture

The compiler consists of four main phases:

1. Lexical analysis (lexer.py)
2. Syntax analysis (parser.py)
3. Semantic analysis (semantic_analyzer.py)
4. Code generation (code_generator.py)

## 📂 Project Structure

pascal-compiler/
├── .github/
│   └── workflows/
├── pascal_compiler.py
├── pascal_lexer.py
├── pascal_parser.py
├── ast_nodes.py
├── semantic_analyzer.py
├── code_generator.py
├── run_tests.py
├── test_*.pas
└── README.md

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

## 📊 CI/CD

GitHub Actions runs tests on:
- Linux
- Windows
- macOS

Python versions: 3.8 – 3.12

## 📄 License

Provided “as is” for educational purposes.

## 🙏 Acknowledgements

Created as a demonstration of classical compiler construction techniques.

## 📞 Feedback

If you find a bug or have suggestions, open an Issue:
https://github.com/Babych/PascalCompilerPy/issues

Made with ❤️ for the Pascal community
