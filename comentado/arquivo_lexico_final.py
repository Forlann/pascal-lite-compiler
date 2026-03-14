# ------------------------------------------------------------
# Compilador PascalLite - Analisador Léxico
# Faculdade Impacta - Compiladores
#
# Implementa a função obter_atomo() que retorna o próximo token
# da entrada para o analisador sintático.
# ------------------------------------------------------------

import sys

# ----------------------------
# Estrutura do Átomo (Token)
# ----------------------------
class Atomo:
    def __init__(self, tipo, lexema, linha, valor=None):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.valor = valor


# ----------------------------
# Palavras Reservadas
# ----------------------------
PALAVRAS_RESERVADAS = {
    "begin": "BEGIN",
    "boolean": "BOOLEAN",
    "div": "DIV",
    "do": "DO",
    "else": "ELSE",
    "end": "END",
    "false": "FALSE",
    "if": "IF",
    "integer": "INTEGER",
    "mod": "MOD",
    "program": "PROGRAM",
    "read": "READ",
    "then": "THEN",
    "true": "TRUE",
    "not": "NOT",
    "var": "VAR",
    "while": "WHILE",
    "write": "WRITE"
}


# ----------------------------
# Classe do Analisador Léxico
# ----------------------------
class AnalisadorLexico:

    def __init__(self, arquivo):
        with open(arquivo, 'r', encoding="utf-8") as f:
            self.codigo = f.read()

        self.pos = 0
        self.linha = 1
        self.tamanho = len(self.codigo)

    # ---------------------------------
    # Lê próximo caractere
    # ---------------------------------
    def proximo_char(self):
        if self.pos >= self.tamanho:
            return None
        return self.codigo[self.pos]

    # ---------------------------------
    # Avança posição
    # ---------------------------------
    def avancar(self):
        c = self.proximo_char()     # lê o caractere atual
        self.pos += 1               # avança a posição no código fonte
        
        # se o caractere for quebra de linha,
        # incrementa o contador de linhas
        if c == '\n':
            self.linha += 1
        return c

    # ---------------------------------
    # Ignora espaços e comentários
    # ---------------------------------
    def ignorar_espacos_e_comentarios(self):

        while True:

            c = self.proximo_char()

            # Espaços
            if c in [' ', '\t', '\r', '\n']:
                self.avancar()
                continue

            # Comentário //
            if c == '/' and self.pos+1 < self.tamanho and self.codigo[self.pos+1] == '/':
                while c != '\n' and c is not None:
                    c = self.avancar()
                continue

            # Comentário (* *)
            if c == '(' and self.pos+1 < self.tamanho and self.codigo[self.pos+1] == '*':
                self.avancar()
                self.avancar()
                while True:
                    if self.proximo_char() == '*' and self.codigo[self.pos+1] == ')':
                        self.avancar()
                        self.avancar()
                        break
                    if self.proximo_char() is None:
                        self.erro("Comentário não fechado")
                    self.avancar()
                continue

            # Comentário { }
            if c == '{':
                self.avancar()
                while self.proximo_char() != '}':
                    if self.proximo_char() is None:
                        self.erro("Comentário não fechado")
                    self.avancar()
                self.avancar()
                continue

            break

    # ---------------------------------
    # Erro léxico
    # ---------------------------------
    def erro(self, msg):
        print(f"Erro léxico: {msg} na linha {self.linha}")
        sys.exit(1)

    # ---------------------------------
    # Reconhece identificador ou palavra reservada
    # ---------------------------------
    def identificador(self):

        inicio = self.pos

        while self.proximo_char() and (
                self.proximo_char().isalnum() or self.proximo_char() == "_"):
            self.avancar()

        lexema = self.codigo[inicio:self.pos]

        if len(lexema) > 20:
            self.erro("Identificador com mais de 20 caracteres")

        if lexema in PALAVRAS_RESERVADAS:
            return Atomo(PALAVRAS_RESERVADAS[lexema], lexema, self.linha)

        return Atomo("IDENTIF", lexema, self.linha)

    # ---------------------------------
    # Reconhece número
    # ---------------------------------
    def numero(self):

        inicio = self.pos

        while self.proximo_char() and self.proximo_char().isdigit():
            self.avancar()

        lexema = self.codigo[inicio:self.pos]

        return Atomo("NUM", lexema, self.linha, int(lexema))

    # ---------------------------------
    # Obtém próximo átomo
    # ---------------------------------
    def obter_atomo(self):

        self.ignorar_espacos_e_comentarios()

        c = self.proximo_char()

        if c is None:
            return None

        # Identificador
        if c.isalpha() or c == "_":
            return self.identificador()

        # Número
        if c.isdigit():
            return self.numero()

        # Operadores compostos
        if c == ':' and self.codigo[self.pos+1] == '=':
            self.avancar()
            self.avancar()
            return Atomo("ATRIB", ":=", self.linha)

        if c == '<':
            self.avancar()
            if self.proximo_char() == '=':
                self.avancar()
                return Atomo("MENOR_IGUAL", "<=", self.linha)
            elif self.proximo_char() == '>':
                self.avancar()
                return Atomo("DIF", "<>", self.linha)
            return Atomo("MENOR", "<", self.linha)

        if c == '>':
            self.avancar()
            if self.proximo_char() == '=':
                self.avancar()
                return Atomo("MAIOR_IGUAL", ">=", self.linha)
            return Atomo("MAIOR", ">", self.linha)

        # Delimitadores
        simples = {
            ";": "PONTO_VIRG",
            ",": "VIRGULA",
            ":": "DOIS_PONTOS",
            "(": "ABRE_PAR",
            ")": "FECHA_PAR",
            "+": "MAIS",
            "-": "MENOS",
            "*": "MULT",
            "/": "DIVISAO",
            "=": "IGUAL",
            ".": "PONTO"
        }

        if c in simples:
            self.avancar()
            return Atomo(simples[c], c, self.linha)

        self.erro(f"Caractere inválido {c}")


# ----------------------------
# Execução do Léxico
# ----------------------------
def executar_lexico(arquivo):

    lexico = AnalisadorLexico(arquivo)

    while True:

        atomo = lexico.obter_atomo()

        if atomo is None:
            break

        if atomo.tipo == "NUM":
            print(
                f"Linha: {atomo.linha} - atomo: {atomo.tipo} lexema: {atomo.lexema} valor: {atomo.valor}")
        else:
            print(
                f"Linha: {atomo.linha} - atomo: {atomo.tipo} lexema: {atomo.lexema}")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso: python lexico.py arquivo.pas")
        sys.exit(1)

    executar_lexico(sys.argv[1])
