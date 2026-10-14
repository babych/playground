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

function Multiply(x, y: integer): integer;
begin
    Multiply := x * y
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
    writeln('Add(', a, ', ', b, ') = ', result);
    
    result := Multiply(a, b);
    writeln('Multiply(', a, ', ', b, ') = ', result);
    
    result := Factorial(5);
    writeln('Factorial(5) = ', result)
end.
