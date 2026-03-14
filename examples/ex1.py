from typing import NamedTuple, Union

# --- Definição dos Átomos (Tokens) ---
ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4
PALAVRA_RESERVADA = 5
OPERADOR = 6
DELIMITADOR = 7

# Conjunto de palavras reservadas 
PALAVRAS_RESERVADAS = { "begin": "BEGIN",
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
    "write": "WRITE"}


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
                if c.isalnum() or c == '_': # letras ou dígitos
                    lexema += c
                    c = self.proximo_char()
                else:
                    estado = 2
            elif estado == 2:
                self.retrair()
                #verifica se é palavra reservada antes de retornar
                if lexema in PALAVRAS_RESERVADAS:
                    return Atomo(PALAVRA_RESERVADA, lexema, 0, self.nlinha)
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
    def pular_espacos_e_comentarios(self):
        c = self.proximo_char()
        while True:
            # 1. Pular espaços
            if c in [' ', '\n', '\t', '\r']:
                if c == '\n':
                    self.nlinha += 1
                c = self.proximo_char()
                continue
            
            # 2. Verificar início de comentário
            if c == '/' and self.i < len(self.buffer):
                next_c = self.buffer[self.i] # Espia o próximo sem avançar
                
                # Comentário de Linha (//)
                if next_c == '/':
                    self.proximo_char() # Consome o segundo '/'
                    while c != '\n' and c != '\0':
                        c = self.proximo_char()
                    continue 
                
                # Comentário de Bloco (/* ... */)
                elif next_c == '*':
                    self.proximo_char() # Consome o '*'
                    c = self.proximo_char()
                    while c != '\0':
                        if c == '\n':
                            self.nlinha += 1
                        elif c == '*' and self.i < len(self.buffer) and self.buffer[self.i] == '/':
                            self.proximo_char() # Consome o '/'
                            c = self.proximo_char()
                            break
                        c = self.proximo_char()
                    continue
            
            # 3. Fim da limpeza: devolve o caractere útil e sai do loop
            self.retrair()
            break
    def proximo_atomo(self):
        # 1. Primeiro, chamamos a nossa nova função que limpa a sujeira
        self.pular_espacos_e_comentarios()
        
        # 2. Agora sim, pegamos o caractere limpo
        c = self.proximo_char()

        # 3. Verificamos o fim do arquivo
        if c == '\0':
            return Atomo(EOS, '', 0, self.nlinha)

        # 4. Direcionamos para a função correta
        if c.isalpha() or c == '_':
            return self.tratar_identificador(c)
        
        if c.isdigit():
            return self.tratar_numero(c)

        # --- AS NOVIDADES ENTRAM AQUI ---
        # 5. Operadores Relacionais e Matemáticos
        if c in ['<', '>', '=', '!', '+', '-', '*', '/']:
            return self.tratar_operador(c)

        # 6. Delimitadores de código
        if c in [';', ',', '(', ')', '{', '}']:
            return Atomo(DELIMITADOR, c, 0, self.nlinha)

        # Se chegou aqui, é um caractere desconhecido
        return Atomo(ERRO, c, 0, self.nlinha)
    
    
    def tratar_operador(self, c):
        lexema = c
        next_c = self.proximo_char()

        #checa operadores lógicos/relacionais compostos
        if c in['<', '>', '=', '!'] and next_c == '=':
            lexema += next_c
            return Atomo(OPERADOR, lexema, 0, self.nlinha)
        # Se não for composto, devolve o caractere que lemos a mais para o buffer
        self.retrair()

        #Retorna o operador simples (+, -, *, /, <, >, =, !)
        return Atomo(OPERADOR, lexema, 0, self.nlinha)
def main():
    # Tenta ler o arquivo entrada.txt
    try:
        with open('entrada.txt', 'r') as f:
            buffer = f.read()
    except FileNotFoundError:
        print("Erro: Crie o arquivo 'entrada.txt' na mesma pasta.")
        return

    lex = AnalisadorLexico(buffer)
    atomo_msg = ['ERRO', 'IDENTIF', 'NUM_INT', 'NUM_REAL', 'EOS', 'PALAVRA_RES', 'OPERADOR', 'DELIMITADOR']
    atomo = lex.proximo_atomo()
    while atomo.tipo != EOS and atomo.tipo != ERRO:
        print(f"Linha: {atomo.linha} - atomo: {atomo_msg[atomo.tipo]} lexema: {atomo.lexema} valor: {atomo.valor}")
        atomo = lex.proximo_atomo()

    # Imprime o último token (EOS ou ERRO)
    print(f"Linha: {atomo.linha} - atomo: {atomo_msg[atomo.tipo]}")

if __name__ == "__main__":
    main()
