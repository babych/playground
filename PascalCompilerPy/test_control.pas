program ControlStructures;
var
    i, sum, factorial: integer;
    found: boolean;

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
    writeln('Sum of 1 to 10: ', sum);
    
    { Test for loop }
    factorial := 1;
    for i := 1 to 5 do
        factorial := factorial * i;
    writeln('Factorial of 5: ', factorial);
    
    { Test repeat until }
    i := 0;
    repeat
        i := i + 1;
        writeln('Iteration: ', i)
    until i >= 3
end.
