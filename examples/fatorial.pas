(*
  programa que calcula o fatorial de um numero lido
*)
program exemplo1;
var fat, num, cont: integer;
begin
  read(num);
  fat := 1;
  cont := 2;
  while cont <= num do
  begin
    fat := fat * num;
    cont := cont + 1
  end;
  write(fat) // imprime fatorial calculado
end.
