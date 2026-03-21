import sys
from arquivo_lexico_final import AnalisadorLexico


# Classe responsável pela análise sintática
class AnalisadorSintatico:

    # Construtor do analisador sintático
    def __init__(self, arquivo):

        # cria o analisador léxico passando o arquivo fonte
        self.lexico = AnalisadorLexico(arquivo)

        # obtém o primeiro token da entrada
        self.atual = self.lexico.obter_atomo()

        # imprime o primeiro token reconhecido
        if self.atual is not None:
            self.imprime_token(self.atual)


    # Função responsável por imprimir os tokens no formato exigido
    def imprime_token(self, atomo):

        # se o token for número, também imprime seu valor
        if atomo.tipo == "NUM":
            print(
                f"Linha: {atomo.linha} - atomo: {atomo.tipo} lexema: {atomo.lexema} valor: {atomo.valor}")
        else:
            print(
                f"Linha: {atomo.linha} - atomo: {atomo.tipo} lexema: {atomo.lexema}")


    # Função para tratamento de erro sintático
    def erro(self, esperado):

        # se chegou ao fim do arquivo
        if self.atual is None:
            encontrado = "EOF"
            linha = self.lexico.linha
        else:
            encontrado = self.atual.tipo
            linha = self.atual.linha

        print(
            f"Erro sintático: Esperado [{esperado}] encontrado [{encontrado}] na linha {linha}")

        sys.exit(1)


    # Função consome: verifica se o token atual é o esperado
    # e solicita o próximo token ao analisador léxico
    def consome(self, esperado):

        # se o token não for o esperado gera erro
        if self.atual is None or self.atual.tipo != esperado:
            self.erro(esperado)

        # caso seja o correto, obtém o próximo token do léxico
        self.atual = self.lexico.obter_atomo()

        # imprime o token reconhecido
        if self.atual is not None:
            self.imprime_token(self.atual)


    # Regra da gramática:
    # <programa> ::= program identificador ; <bloco>.
    def programa(self):

        self.consome("PROGRAM")
        self.consome("IDENTIF")
        self.consome("PONTO_VIRG")

        self.bloco()

        self.consome("PONTO")


    # Regra:
    # <bloco> ::= [<declarações de variáveis>] <comando composto>
    def bloco(self):

        if self.atual.tipo == "VAR":
            self.declaracoes_variaveis()

        self.comando_composto()


    # Regra:
    # <declarações de variáveis> ::= var <declaração> {; <declaração>}
    def declaracoes_variaveis(self):

        self.consome("VAR")

        self.declaracao()

        while self.atual.tipo == "PONTO_VIRG":
            self.consome("PONTO_VIRG")

            if self.atual.tipo == "IDENTIF":
                self.declaracao()


    # Regra:
    # <declaração> ::= <lista de identificadores> : <tipo>
    def declaracao(self):

        self.lista_identificadores()
        self.consome("DOIS_PONTOS")
        self.tipo()


    # Regra:
    # <lista de identificadores> ::= identificador { , identificador }
    def lista_identificadores(self):

        self.consome("IDENTIF")

        while self.atual.tipo == "VIRGULA":
            self.consome("VIRGULA")
            self.consome("IDENTIF")


    # Regra:
    # <tipo> ::= integer | boolean
    def tipo(self):

        if self.atual.tipo == "INTEGER":
            self.consome("INTEGER")

        elif self.atual.tipo == "BOOLEAN":
            self.consome("BOOLEAN")

        else:
            self.erro("INTEGER ou BOOLEAN")


    # Regra:
    # <comando composto> ::= begin <comando> { ; <comando> } end
    def comando_composto(self):

        self.consome("BEGIN")

        self.comando()

        while self.atual.tipo == "PONTO_VIRG":
            self.consome("PONTO_VIRG")
            self.comando()

        self.consome("END")


    # Regra que identifica qual tipo de comando será executado
    def comando(self):

        if self.atual.tipo == "IDENTIF":
            self.atribuicao()

        elif self.atual.tipo == "READ":
            self.comando_read()

        elif self.atual.tipo == "WRITE":
            self.comando_write()

        elif self.atual.tipo == "IF":
            self.comando_if()

        elif self.atual.tipo == "WHILE":
            self.comando_while()

        elif self.atual.tipo == "BEGIN":
            self.comando_composto()

        else:
            self.erro("COMANDO")


    # Regra:
    # <atribuição> ::= identificador := <expressao>
    def atribuicao(self):

        self.consome("IDENTIF")
        self.consome("ATRIB")
        self.expressao()


    # Regra:
    # <comando de entrada> ::= read ( <lista de identificadores> )
    def comando_read(self):

        self.consome("READ")
        self.consome("ABRE_PAR")

        self.lista_identificadores()

        self.consome("FECHA_PAR")


    # Regra:
    # <comando de saída> ::= write ( <expressao> { , <expressao> } )
    def comando_write(self):

        self.consome("WRITE")
        self.consome("ABRE_PAR")

        self.expressao()

        while self.atual.tipo == "VIRGULA":
            self.consome("VIRGULA")
            self.expressao()

        self.consome("FECHA_PAR")


    # Regra do comando if
    def comando_if(self):

        self.consome("IF")

        self.expressao()

        self.consome("THEN")

        self.comando()

        if self.atual.tipo == "ELSE":
            self.consome("ELSE")
            self.comando()


    # Regra do comando while
    def comando_while(self):

        self.consome("WHILE")

        self.expressao()

        self.consome("DO")

        self.comando()


    # Regra:
    # <expressao> ::= <expressao simples> [<operador relacional> <expressao simples>]
    def expressao(self):

        self.expressao_simples()

        if self.atual and self.atual.tipo in ["MENOR", "MENOR_IGUAL", "MAIOR", "MAIOR_IGUAL", "IGUAL", "DIF"]:
            self.consome(self.atual.tipo)
            self.expressao_simples()


    # Regra da expressão simples
    def expressao_simples(self):

        if self.atual.tipo in ["MAIS", "MENOS"]:
            self.consome(self.atual.tipo)

        self.termo()

        while self.atual.tipo in ["MAIS", "MENOS", "OR"]:
            self.consome(self.atual.tipo)
            self.termo()


    # Regra do termo
    def termo(self):

        self.fator()

        while self.atual.tipo in ["MULT", "DIVISAO", "DIV", "MOD", "AND"]:
            self.consome(self.atual.tipo)
            self.fator()


    # Regra do fator
    def fator(self):

        if self.atual.tipo == "IDENTIF":
            self.consome("IDENTIF")

        elif self.atual.tipo == "NUM":
            self.consome("NUM")

        elif self.atual.tipo == "TRUE":
            self.consome("TRUE")

        elif self.atual.tipo == "FALSE":
            self.consome("FALSE")

        elif self.atual.tipo == "NOT":
            self.consome("NOT")
            self.fator()

        elif self.atual.tipo == "ABRE_PAR":
            self.consome("ABRE_PAR")
            self.expressao()
            self.consome("FECHA_PAR")

        else:
            self.erro("FATOR")


# Função principal do compilador
if __name__ == "__main__":

    # verifica se o arquivo foi passado na linha de comando
    if len(sys.argv) != 2:
        print("Uso: python sintatico.py arquivo.pas")
        sys.exit(1)

    # cria o analisador sintático
    sintatico = AnalisadorSintatico(sys.argv[1])

    # inicia a análise sintática
    sintatico.programa()

    # mensagem final caso o programa esteja correto
    print(f"\n{sintatico.lexico.linha} linhas analisadas, programa sintaticamente correto.")