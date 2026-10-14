@echo off
echo ============================================================
echo Pascal Compiler - Windows Test Runner
echo ============================================================
echo.

echo Testing simple program...
python pascal_compiler.py test_simple.pas
echo.
echo ============================================================
echo.

echo Testing control structures...
python pascal_compiler.py test_control.pas -o output_control.txt
echo.
echo ============================================================
echo.

echo Testing functions...
python pascal_compiler.py test_functions.pas -o output_functions.txt
echo.
echo ============================================================
echo.

echo Testing error handling...
python pascal_compiler.py test_errors.pas
echo.
echo ============================================================
echo.

echo All tests completed!
pause
