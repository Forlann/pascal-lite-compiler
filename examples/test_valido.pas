{ Programa válido: calcula soma de dois inteiros }

program soma;
var a, b, resultado: integer;
begin
    read(a, b);
    resultado := a + b;
    if resultado > 100 then
        write(resultado)
    else
        write(a);
    write(b)
end.
