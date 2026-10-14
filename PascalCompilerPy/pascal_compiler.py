#!/usr/bin/env python3
"""
Pascal Compiler - Main Driver
Coordinates lexical analysis, parsing, semantic analysis, and code generation
"""

import sys
import argparse
from pathlib import Path
from pascal_lexer import Lexer
from pascal_parser import Parser
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator

class PascalCompiler:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def compile(self, source_code: str, output_file: str = None) -> bool:
        """
        Compile Pascal source code
        Returns True if compilation successful, False otherwise
        """
        try:
            # Phase 1: Lexical Analysis
            if self.verbose:
                print("Phase 1: Lexical Analysis")
                print("-" * 50)
            
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            if self.verbose:
                print(f"Generated {len(tokens)} tokens")
                for token in tokens[:10]:  # Show first 10 tokens
                    print(f"  {token}")
                if len(tokens) > 10:
                    print(f"  ... and {len(tokens) - 10} more tokens")
                print()
            
            # Phase 2: Syntax Analysis (Parsing)
            if self.verbose:
                print("Phase 2: Syntax Analysis")
                print("-" * 50)
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            if self.verbose:
                print(f"Successfully parsed program: {ast.name}")
                print(f"  Declarations: {len(ast.declarations)}")
                print(f"  Statements in main block: {len(ast.block.statements)}")
                print()
            
            # Phase 3: Semantic Analysis
            if self.verbose:
                print("Phase 3: Semantic Analysis")
                print("-" * 50)
            
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            if self.verbose:
                print("Semantic analysis passed")
                print()
            
            # Phase 4: Code Generation
            if self.verbose:
                print("Phase 4: Code Generation")
                print("-" * 50)
            
            generator = CodeGenerator()
            code = generator.generate(ast)
            
            if self.verbose:
                print(f"Generated {len(code)} lines of intermediate code")
                print()
            
            # Output
            if output_file:
                with open(output_file, 'w') as f:
                    f.write('\n'.join(code))
                print(f"Compiled successfully. Output written to {output_file}")
            else:
                print("Compilation successful. Intermediate code:")
                print("=" * 60)
                for line in code:
                    print(line)
                print("=" * 60)
            
            return True
            
        except SyntaxError as e:
            print(f"Syntax Error: {e}", file=sys.stderr)
            return False
        except SemanticError as e:
            print(f"Semantic Error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Compilation Error: {e}", file=sys.stderr)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(
        description='Pascal Compiler - Compiles Pascal source code to intermediate code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s program.pas                 # Compile and display output
  %(prog)s program.pas -o output.txt   # Compile and save to file
  %(prog)s program.pas -v              # Compile with verbose output
        """
    )
    
    parser.add_argument('input', help='Input Pascal source file')
    parser.add_argument('-o', '--output', help='Output file for intermediate code')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        source_code = input_path.read_text()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Compile
    compiler = PascalCompiler(verbose=args.verbose)
    success = compiler.compile(source_code, args.output)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
