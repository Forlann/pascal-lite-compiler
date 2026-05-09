{ Testa expressao com precedencia, parenteses e operador unario }

program teste_expr;
var a, b, c, r: integer;
begin
  read(a, b, c);
  r := -a + b * (c - 1) div 2;
  write(r)
end.
