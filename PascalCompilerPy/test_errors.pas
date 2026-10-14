program ErrorTest;
var
    x: integer;
    y: real;
    flag: boolean;

begin
    { This should work }
    x := 10;
    y := 3.14;
    flag := true;
    
    { Test type checking - this will cause semantic error }
    { Uncommenting the next line will show type mismatch error }
    { x := y; }
    
    { Test undefined variable - uncommenting will show error }
    { z := 5; }
    
    { Valid comparisons }
    if x > 5 then
        writeln('x is greater than 5');
    
    if flag then
        writeln('flag is true');
    
    writeln('Program completed successfully')
end.
