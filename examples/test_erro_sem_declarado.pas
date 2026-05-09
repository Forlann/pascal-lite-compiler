{ Programa com erro semântico: variável usada sem ser declarada }

program teste_erro_decl;
var a: integer;
begin
  read(a);
  b := a + 1;
  write(b)
end.
