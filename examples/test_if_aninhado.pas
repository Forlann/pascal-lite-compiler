{ Testa if/else aninhado para validar uso correto de rotulos }

program teste_if;
var x, y: integer;
begin
  read(x, y);
  if x > 0 then
    if y > 0 then
      write(1)
    else
      write(2)
  else
    write(3)
end.
