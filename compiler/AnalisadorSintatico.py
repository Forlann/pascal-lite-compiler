from AnalisadorLexico import IDENTIFICADOR, NUM_INT, NUM_REAL, EOS, ERRO
from TabelaSimbolos import TabelaSimbolos
import sys

_NOMES_TIPO = {
    ERRO: "ERRO",
    IDENTIFICADOR: "IDENTIF",
    NUM_INT: "NUM",
    NUM_REAL: "NUM_REAL",
    EOS: "EOS",
}

# Mapeamento dos operadores relacionais para instruções MEPA
_REL_MEPA = {
    "IGUAL": "CMIG",
    "MENOR": "CMME",
    "MAIOR": "CMMA",
    "DIFERENTE": "CMDG",
    "MENOR_IGUAL": "CMEG",
    "MAIOR_IGUAL": "CMAG",
}


def _nome_tipo(tipo):
    return _NOMES_TIPO.get(tipo, str(tipo))


class AnalisadorSintatico:
    def __init__(self, analisador_lexico):
        self.lexico = analisador_lexico
        self.lookahead = self.lexico.next_atom()

        # Estruturas da fase 2: análise semântica e geração de código
        self.tabela = TabelaSimbolos()
        self.contador_rotulos = 0
        self.saida_mepa = []

    def emit(self, instrucao):
        """Adiciona uma instrução MEPA à saída e imprime em stdout."""
        self.saida_mepa.append(instrucao)
        print(instrucao)

    def proximo_rotulo(self):
        """Retorna o próximo rótulo no formato L1, L2, L3, ..."""
        self.contador_rotulos += 1
        return f"L{self.contador_rotulos}"

    def consome(self, tipo_esperado):
        if self.lookahead.type == tipo_esperado:
            self.lookahead = self.lexico.next_atom()
        else:
            print(
                f"Erro sintático: Esperado [{_nome_tipo(tipo_esperado)}] "
                f"encontrado [{_nome_tipo(self.lookahead.type)}] na linha {self.lookahead.line}",
                file=sys.stderr,
            )
            sys.exit(1)

    def regra_do_programa(self):
        self.consome("PROGRAM")
        self.consome(IDENTIFICADOR)

        if self.lookahead.type == "ABRE_PAR":
            self.consome("ABRE_PAR")
            self.lista_indentificadores()
            self.consome("FECHA_PAR")

        self.consome("PONTO_VIRG")
        self.emit("INPP")
        self.regra_bloco()
        self.emit("PARA")
        self.consome("PONTO")

    def lista_indentificadores(self):
        """Lê uma lista de identificadores e retorna pares (lexema, linha)."""
        nomes = [(self.lookahead.lexema, self.lookahead.line)]
        self.consome(IDENTIFICADOR)
        while self.lookahead.type == "VIRGULA":
            self.consome("VIRGULA")
            nomes.append((self.lookahead.lexema, self.lookahead.line))
            self.consome(IDENTIFICADOR)
        return nomes

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
            nomes = self.lista_indentificadores()
            self.consome("FECHA_PAR")
            for nome, linha in nomes:
                endereco, _ = self.tabela.buscar(nome, linha)
                self.emit("LEIT")
                self.emit(f"ARMZ {endereco}")

        elif self.lookahead.type == "WRITE":
            self.consome("WRITE")
            self.consome("ABRE_PAR")
            self.expressao()
            self.emit("IMPR")
            while self.lookahead.type == "VIRGULA":
                self.consome("VIRGULA")
                self.expressao()
                self.emit("IMPR")
            self.consome("FECHA_PAR")

        elif self.lookahead.type == IDENTIFICADOR:
            # Atribuição: identificador := expressao
            nome = self.lookahead.lexema
            linha = self.lookahead.line
            endereco, _ = self.tabela.buscar(nome, linha)
            self.consome(IDENTIFICADOR)
            self.consome("ATRIB")
            self.expressao()
            self.emit(f"ARMZ {endereco}")

        elif self.lookahead.type == "WHILE":
            # Rótulos antes da expressão para garantir ordem correta
            L1 = self.proximo_rotulo()
            L2 = self.proximo_rotulo()
            self.consome("WHILE")
            self.emit(f"{L1}: NADA")
            self.expressao()
            self.emit(f"DSVF {L2}")
            self.consome("DO")
            self.comando()
            self.emit(f"DSVS {L1}")
            self.emit(f"{L2}: NADA")

        elif self.lookahead.type == "IF":
            self.consome("IF")
            self.expressao()
            L1 = self.proximo_rotulo()
            self.emit(f"DSVF {L1}")
            self.consome("THEN")
            self.comando()

            if self.lookahead.type == "ELSE":
                L2 = self.proximo_rotulo()
                self.emit(f"DSVS {L2}")
                self.emit(f"{L1}: NADA")
                self.consome("ELSE")
                self.comando()
                self.emit(f"{L2}: NADA")
            else:
                self.emit(f"{L1}: NADA")

        elif self.lookahead.type == "BEGIN":
            self.comando_composto()

    def fator(self):
        # Versão simplificada conforme fase 2: identificador | numero | ( expressao )
        if self.lookahead.type == IDENTIFICADOR:
            endereco, _ = self.tabela.buscar(self.lookahead.lexema, self.lookahead.line)
            self.emit(f"CRVL {endereco}")
            self.consome(IDENTIFICADOR)

        elif self.lookahead.type == NUM_INT:
            self.emit(f"CRCT {self.lookahead.value}")
            self.consome(NUM_INT)

        else:
            self.consome("ABRE_PAR")
            self.expressao()
            self.consome("FECHA_PAR")

    def operador_multiplicacao(self):
        if self.lookahead.type == "MULT":
            self.consome("MULT")
        elif self.lookahead.type == "DIVISAO":
            self.consome("DIVISAO")
        elif self.lookahead.type == "DIV":
            self.consome("DIV")
        elif self.lookahead.type == "MOD":
            self.consome("MOD")

    def termo(self):
        self.fator()
        while self.lookahead.type in ("MULT", "DIVISAO", "DIV", "MOD"):
            op = self.lookahead.type
            self.operador_multiplicacao()
            self.fator()
            if op == "MULT":
                self.emit("MULT")
            elif op in ("DIVISAO", "DIV"):
                self.emit("DIVI")
            elif op == "MOD":
                # MEPA padrão não tem MOD; emitido como pseudo-instrução.
                self.emit("MOD")

    def operador_adicao(self):
        if self.lookahead.type == "MAIS":
            self.consome("MAIS")
        elif self.lookahead.type == "MENOS":
            self.consome("MENOS")

    def expressao_simples(self):
        sinal_unario = None
        if self.lookahead.type == "MAIS":
            self.consome("MAIS")
            sinal_unario = "MAIS"
        elif self.lookahead.type == "MENOS":
            self.consome("MENOS")
            sinal_unario = "MENOS"

        self.termo()

        if sinal_unario == "MENOS":
            self.emit("INVR")

        while self.lookahead.type in ("MAIS", "MENOS"):
            op = self.lookahead.type
            self.operador_adicao()
            self.termo()
            if op == "MAIS":
                self.emit("SOMA")
            elif op == "MENOS":
                self.emit("SUBT")

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
            op = self.lookahead.type
            self.operador_relacional()
            self.expressao_simples()
            self.emit(_REL_MEPA[op])

    def regra_bloco(self):
        if self.lookahead.type == "VAR":
            self.declara_variaveis()
        self.comando_composto()

    def declaracao(self):
        nomes = self.lista_indentificadores()
        self.consome("DOIS_PONTOS")
        # Fase 2: somente tipo integer é aceito (tudo é tratado como inteiro)
        self.consome("INTEGER")
        for nome, linha in nomes:
            self.tabela.inserir(nome, "integer", linha)

    def declara_variaveis(self):
        self.consome("VAR")
        self.declaracao()

        while self.lookahead.type == "PONTO_VIRG":
            self.consome("PONTO_VIRG")
            if self.lookahead.type == IDENTIFICADOR:
                self.declaracao()
            else:
                break

        if self.tabela.total() > 0:
            self.emit(f"AMEM {self.tabela.total()}")
