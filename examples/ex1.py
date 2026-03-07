from typing import NamedTuple, Union

# --- Definição dos Átomos (Tokens) ---
ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4

class Atomo(NamedTuple):
    tipo: int
    lexema: str
    valor: Union[int, float, str]
    linha: int

class AnalisadorLexico:
    def __init__(self, buffer):
        self.buffer = buffer + '\0'  # Adiciona fim de string
        self.i = 0
        self.nlinha = 1

    def proximo_char(self):
        if self.i >= len(self.buffer):
            return '\0'
        c = self.buffer[self.i]
        self.i += 1
        return c

    def retrair(self):
        self.i -= 1

    # --- Lógica para identificar palavras (Identificadores) ---
    def tratar_identificador(self, c):
        lexema = c
        c = self.proximo_char()
        estado = 1
        
        while True:
            if estado == 1:
                if c.isalnum(): # letras ou dígitos
                    lexema += c
                    c = self.proximo_char()
                else:
                    estado = 2
            elif estado == 2:
                self.retrair()
                return Atomo(IDENTIFICADOR, lexema, 0, self.nlinha)

    # --- Lógica para identificar números (Inteiros e Reais) ---
    def tratar_numero(self, c):
        lexema = c
        c = self.proximo_char()
        estado = 1

        while True:
            if estado == 1:
                if c.isdigit():
                    lexema += c
                    c = self.proximo_char()
                elif c == '.':
                    lexema += c
                    estado = 3
                    c = self.proximo_char()
                elif c.isalpha():
                     return Atomo(ERRO, lexema, 0, self.nlinha)
                else:
                    estado = 2 # É Inteiro

            elif estado == 2:
                self.retrair()
                return Atomo(NUM_INT, lexema, int(lexema), self.nlinha)

            elif estado == 3: # Parte decimal
                if c.isdigit():
                    lexema += c
                    estado = 4
                    c = self.proximo_char()
                else:
                    return Atomo(ERRO, lexema, 0, self.nlinha)

            elif estado == 4:
                if c.isdigit():
                    lexema += c
                    c = self.proximo_char()
                elif c.isalpha():
                    return Atomo(ERRO, lexema, 0, self.nlinha)
                else:
                    estado = 5

            elif estado == 5:
                self.retrair()
                return Atomo(NUM_REAL, lexema, float(lexema), self.nlinha)

    # --- Método Principal que decide o que fazer ---
    def proximo_atomo(self):
        c = self.proximo_char()

        # Pular espaços e contar linhas
        while c in [' ', '\n', '\t', '\r']:
            if c == '\n':
                self.nlinha += 1
            c = self.proximo_char()

        if c == '\0':
            return Atomo(EOS, '', 0, self.nlinha)

        if c.isalpha():
            return self.tratar_identificador(c)
        
        if c.isdigit():
            return self.tratar_numero(c)

        # Se chegou aqui, é um caractere desconhecido
        return Atomo(ERRO, c, 0, self.nlinha)


def main():
    # Tenta ler o arquivo entrada.txt
    try:
        with open('entrada.txt', 'r') as f:
            buffer = f.read()
    except FileNotFoundError:
        print("Erro: Crie o arquivo 'entrada.txt' na mesma pasta.")
        return

    lex = AnalisadorLexico(buffer)
    atomo_msg = ['ERRO', 'IDENTIF', 'NUM_INT', 'NUM_REAL', 'EOS']

    atomo = lex.proximo_atomo()
    while atomo.tipo != EOS and atomo.tipo != ERRO:
        print(f"Linha: {atomo.linha} - atomo: {atomo_msg[atomo.tipo]} lexema: {atomo.lexema} valor: {atomo.valor}")
        atomo = lex.proximo_atomo()

    # Imprime o último token (EOS ou ERRO)
    print(f"Linha: {atomo.linha} - atomo: {atomo_msg[atomo.tipo]}")

if __name__ == "__main__":
    main()