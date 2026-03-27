from AnalisadorLexico import IDENTIFICADOR, NUM_INT, NUM_REAL, EOS, ERRO
import sys

_NOMES_TIPO = {
    ERRO: "ERRO",
    IDENTIFICADOR: "IDENTIF",
    NUM_INT: "NUM",
    NUM_REAL: "NUM_REAL",
    EOS: "EOS",
}

def _nome_tipo(tipo):
    return _NOMES_TIPO.get(tipo, str(tipo))


class AnalisadorSintatico:
    def __init__(self, analisador_lexico, formatar_atomo):
        self.lexico = analisador_lexico
        self.formatar_atomo = formatar_atomo
        self.lookahead = self.lexico.next_atom()

    def consome(self, tipo_esperado):
        if self.lookahead.type == tipo_esperado:
            print(self.formatar_atomo(self.lookahead))
            self.lookahead = self.lexico.next_atom()
        else:
            print(
                f"Erro sintático: Esperado [{_nome_tipo(tipo_esperado)}] encontrado [{_nome_tipo(self.lookahead.type)}] na linha {self.lookahead.line}")
            sys.exit(1)

    def regra_do_programa(self):
        self.consome("PROGRAM")
        self.consome(IDENTIFICADOR)

        if self.lookahead.type == "ABRE_PAR":
            self.consome("ABRE_PAR")
            self.lista_indentificadores()
            self.consome("FECHA_PAR")

        self.consome("PONTO_VIRG")
        self.regra_bloco()
        self.consome("PONTO")

    def lista_indentificadores(self):
        self.consome(IDENTIFICADOR)
        while self.lookahead.type == "VIRGULA":
            self.consome("VIRGULA")
            self.consome(IDENTIFICADOR)

    def comando_composto(self):
        self.consome("BEGIN")
        self.comando()

        while self.lookahead.type == "PONTO_VIRG":
            self.consome("PONTO_VIRG")
            if self.lookahead.type != "END":
                self.comando()
            else:
                break
        self.consome("END")

    def comando(self):
        if self.lookahead.type == "READ":
            self.consome("READ")
            self.consome("ABRE_PAR")
            self.lista_indentificadores()
            self.consome("FECHA_PAR")

        elif self.lookahead.type == "WRITE":
            self.consome("WRITE")
            self.consome("ABRE_PAR")
            self.expressao()
            while self.lookahead.type == "VIRGULA":
                self.consome("VIRGULA")
                self.expressao()
            self.consome("FECHA_PAR")

        elif self.lookahead.type == IDENTIFICADOR:
            self.consome(IDENTIFICADOR)
            self.consome("ATRIB")
            self.expressao()

        elif self.lookahead.type == "WHILE":
            self.consome("WHILE")
            self.expressao()
            self.consome("DO")
            self.comando()

        elif self.lookahead.type == "IF":
            self.consome("IF")
            self.expressao()
            self.consome("THEN")
            self.comando()

            if self.lookahead.type == "ELSE":
                self.consome("ELSE")
                self.comando()

        elif self.lookahead.type == "BEGIN":
            self.comando_composto()

    def fator(self):
        if self.lookahead.type == IDENTIFICADOR:
            self.consome(IDENTIFICADOR)

        elif self.lookahead.type == NUM_INT:
            self.consome(NUM_INT)

        elif self.lookahead.type == "ABRE_PAR":
            self.consome("ABRE_PAR")
            self.expressao()
            self.consome("FECHA_PAR")

        elif self.lookahead.type == "TRUE":
            self.consome("TRUE")

        elif self.lookahead.type == "FALSE":
            self.consome("FALSE")

        elif self.lookahead.type == "NOT":
            self.consome("NOT")
            self.fator()

    def operador_multiplicacao(self):
        if self.lookahead.type == "MULT":
            self.consome("MULT")

        elif self.lookahead.type == "DIVISAO":
            self.consome("DIVISAO")

        elif self.lookahead.type == "DIV":
            self.consome("DIV")

        elif self.lookahead.type == "MOD":
            self.consome("MOD")

        elif self.lookahead.type == "AND":
            self.consome("AND")

    def termo(self):
        self.fator()
        while self.lookahead.type in ("MULT", "DIVISAO", "DIV", "MOD", "AND"):
            self.operador_multiplicacao()
            self.fator()

    def operador_adicao(self):
        if self.lookahead.type == "MAIS":
            self.consome("MAIS")

        elif self.lookahead.type == "MENOS":
            self.consome("MENOS")

        elif self.lookahead.type == "OR":
            self.consome("OR")

    def expressao_simples(self):
        if self.lookahead.type == "MAIS":
            self.consome("MAIS")
        elif self.lookahead.type == "MENOS":
            self.consome("MENOS")

        self.termo()
        while self.lookahead.type in ("MAIS", "MENOS", "OR"):
            self.operador_adicao()
            self.termo()

    def operador_relacional(self):
        if self.lookahead.type == "MAIOR_IGUAL":
            self.consome("MAIOR_IGUAL")

        elif self.lookahead.type == "MENOR_IGUAL":
            self.consome("MENOR_IGUAL")

        elif self.lookahead.type == "DIFERENTE":
            self.consome("DIFERENTE")

        elif self.lookahead.type == "MAIOR":
            self.consome("MAIOR")

        elif self.lookahead.type == "MENOR":
            self.consome("MENOR")

        elif self.lookahead.type == "IGUAL":
            self.consome("IGUAL")

    def expressao(self):
        self.expressao_simples()
        if self.lookahead.type in ("IGUAL", "MENOR", "MAIOR", "DIFERENTE", "MENOR_IGUAL", "MAIOR_IGUAL"):
            self.operador_relacional()
            self.expressao_simples()

    def regra_bloco(self):
        if self.lookahead.type == "VAR":
            self.declara_variaveis()
        self.comando_composto()

    def declaracao(self):
        self.lista_indentificadores()
        self.consome("DOIS_PONTOS")

        if self.lookahead.type == "INTEGER":
            self.consome("INTEGER")
        elif self.lookahead.type == "BOOLEAN":
            self.consome("BOOLEAN")

    def declara_variaveis(self):
        self.consome("VAR")
        self.declaracao()

        while self.lookahead.type == "PONTO_VIRG":
            self.consome("PONTO_VIRG")
            if self.lookahead.type == IDENTIFICADOR:
                self.declaracao()
            else:
                break
