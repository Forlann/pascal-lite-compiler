{ Programa com erro semântico: identificador declarado duas vezes }

program teste_erro_dup;
var x, y: integer;
    x: integer;
begin
  x := 1;
  y := 2;
  write(x, y)
end.
