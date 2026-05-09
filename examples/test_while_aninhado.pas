{ Testa while aninhado para validar geracao de rotulos sequenciais }

program teste_while_an;
var i, j: integer;
begin
  i := 0;
  while i < 3 do
  begin
    j := 0;
    while j < 3 do
    begin
      write(i, j);
      j := j + 1
    end;
    i := i + 1
  end
end.
