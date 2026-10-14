#!/usr/bin/env python3
"""
Pascal Compiler Test Suite
Runs all test programs and verifies compilation
"""

import subprocess
import sys
import os
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def run_test(test_file, description):
    """Run a single test and return success status"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing: {description}{Colors.RESET}")
    print(f"File: {test_file}")
    print("-" * 60)
    
    try:
        # Try python first (Windows), then python3 (Mac/Linux)
        python_cmd = 'python' if sys.platform == 'win32' else 'python3'
        result = subprocess.run(
            [python_cmd, 'pascal_compiler.py', test_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}[PASSED]{Colors.RESET}")
            print(f"\nOutput preview (first 10 lines):")
            lines = result.stdout.split('\n')
            for line in lines[:10]:
                print(f"  {line}")
            if len(lines) > 10:
                print(f"  ... ({len(lines) - 10} more lines)")
            return True
        else:
            print(f"{Colors.RED}[FAILED]{Colors.RESET}")
            print(f"\nError output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}[TIMEOUT]{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}[ERROR]: {e}{Colors.RESET}")
        return False

def main():
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("Pascal Compiler Test Suite")
    print(f"{'=' * 60}{Colors.RESET}\n")
    
    tests = [
        ('test_simple.pas', 'Simple arithmetic and variables'),
        ('test_control.pas', 'Control structures (if/while/for/repeat)'),
        ('test_functions.pas', 'Procedures and functions'),
        ('test_errors.pas', 'Error handling and type checking'),
    ]
    
    results = []
    for test_file, description in tests:
        if not Path(test_file).exists():
            print(f"{Colors.YELLOW}[WARNING] Skipping {test_file} - file not found{Colors.RESET}")
            continue
        
        success = run_test(test_file, description)
        results.append((test_file, success))
    
    # Summary
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("Test Summary")
    print(f"{'=' * 60}{Colors.RESET}\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_file, success in results:
        status = f"{Colors.GREEN}[PASSED]{Colors.RESET}" if success else f"{Colors.RED}[FAILED]{Colors.RESET}"
        print(f"{status}  {test_file}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed!{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some tests failed.{Colors.RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
