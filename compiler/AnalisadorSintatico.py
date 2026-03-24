class AnalisadorSintatico:
  def __init__(self, analisador_lexico):
    self.lexico = analisador_lexico
    self.lookahead = self.lexico.next_atom()
    self.tipo_esperado = "PROGRAM"

  def consome(self, tipo_esperado):
    if self.lookahead.type == tipo_esperado:
      self.lookahead = self.lexico.next_atom()
    else:
      # Formato de erro exigido pelo documento
      print(f"Erro sintático: Esperado [{tipo_esperado}] encontrado [{self.lookahead.type}] na linha {self.lookahead.line}")
      exit()
  
  def regra_do_programa(self):
    self.consome("PROGRAM")

    self.consome(IDENTIFICADOR)

    if self.lookahead.type == "ABRE_PAR":
      self.parametros_funcao()

    self.consome("PONTO_VIRG")

  def lista_indentificadores(self):
     self.consome("ABRE_PAR")
      self.consome(IDENTIFICADOR)
      while self.lookahead.type == "VIRGULA":
        self.consome("VIRGULA")
        self.consome(IDENTIFICADOR)
      self.consome("FECHA_PAR")

  def regra_bloco(self):
    ...

  def declara_variaveis(self):
    self.consome("VAR")
    while self.lookahead.type == "VIRGULA":
      self.lista_indentificadores()
    self.consome(":")

    if self.lookahead.type == NUM_INT: