{ Teste: operadores 'and' e 'or' - expõe bug de palavras reservadas }

program teste_and_or;
var a, b: boolean;
begin
    a := true;
    b := false;
    if a and b then
        write(1)
    else
        write(0)
end.
