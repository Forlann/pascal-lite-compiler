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

        # 5. Operadores Relacionais e Matemáticos
        if c in ['<', '>', '=', '!', '+', '-', '*', '/',':']:
            return self.tratar_operador(c)

        # 6. Delimitadores de código
        if c in [';', ',', '(', ')', '{', '}','.']:
            return Atomo(DELIMITADOR, c, 0, self.nlinha)

        # Se chegou aqui, é um caractere desconhecido
        return Atomo(ERRO, c, 0, self.nlinha)
    
    
    def tratar_operador(self, c):
        lexema = c
        next_c = self.proximo_char()
        
        # Checa atribuição do Pascal (:=)
        if c == ':' and next_c == '=':
            lexema += next_c
            return Atomo(OPERADOR, lexema, 0, self.nlinha)
        # Se for apenas ':', tratamos como delimitador (para VAR x : integer)
        elif c == ':' and next_c != '=':
            self.retrair()
            return Atomo(DELIMITADOR, lexema, 0, self.nlinha)

        # Checa diferença do Pascal (<>)
        if c == '<' and next_c == '>':
            lexema += next_c
            return Atomo(OPERADOR, lexema, 0, self.nlinha)

        # Checa operadores lógicos/relacionais compostos (<=, >=, ==, !=)
        if c in ['<', '>', '=', '!'] and next_c == '=':
            lexema += next_c
            return Atomo(OPERADOR, lexema, 0, self.nlinha)

        # Se não for composto, devolve o caractere que lemos a mais para o buffer
        self.retrair()

        # Retorna o operador simples (+, -, *, /, <, > , =)
        return Atomo(OPERADOR, lexema, 0, self.nlinha)

class AnalisadorSintatico:
    def __init__(self, lexer):
        self.lexer = lexer
        self.atomo_atual = self.lexer.proximo_atomo()
        self.erros = []

    def erro(self, tipos_esperados: list):
        tipo_encontrado = self.atomo_atual.tipo 
        lexema_encontrado = self.atomo_atual.lexema
        linha = self.atomo_atual.linha
        
        # Converte a lista de esperados para string para exibição limpa
        esperados_str = ', '.join(map(str, tipos_esperados))
        msg_erro = f"Erro de sintaxe na linha {linha}: Esperado [{esperados_str}], encontrado tipo {tipo_encontrado} ('{lexema_encontrado}')"
        
        self.erros.append(msg_erro)
        print(msg_erro)
        self.atomo_atual = self.lexer.proximo_atomo() # Avança para não travar

    def consumir(self, esperado) -> bool:
        """
        Lógica:
        - Se 'esperado' for inteiro (ex: IDENTIFICADOR), compara com .tipo
        - Se 'esperado' for string (ex: 'begin', ';'), compara com .lexema
        """
        corresponde = False
        
        if isinstance(esperado, int):
            corresponde = (self.atomo_atual.tipo == esperado)
        elif isinstance(esperado, str):
            corresponde = (self.atomo_atual.lexema.lower() == esperado.lower())

        if corresponde:
            self.atomo_atual = self.lexer.proximo_atomo()
            return True
        else:
            self.erro([esperado])
            return False

    def analisar(self):
        print("Iniciando análise sintática...")
        self.programa()
        
        if not self.erros and self.atomo_atual.tipo == EOS:
            print("Análise sintática concluída com sucesso!")
            return True
        else:
            print("Análise sintática concluída com erros.")
            for err in self.erros:
                print(err)
            return False

    def programa(self):
        if not self.consumir("program"): return
        if not self.consumir(IDENTIFICADOR): return
        if not self.consumir(";"): return
        self.bloco()
        if not self.consumir("."): return

    def bloco(self):
        if self.atomo_atual.lexema.lower() == "var":
            self.declaracoes()
        self.comando_composto()

    def declaracoes(self):
        if not self.consumir("var"): return
        self.lista_identificadores()
        if not self.consumir(":"): return
        self.especificacao_tipo()
        if not self.consumir(";"): return
        
        # Permite múltiplas declarações na mesma sessão VAR
        while self.atomo_atual.tipo == IDENTIFICADOR or self.atomo_atual.lexema.lower() == "var":
             if self.atomo_atual.lexema.lower() == "var":
                 self.consumir("var")
             self.lista_identificadores()
             if not self.consumir(":"): return
             self.especificacao_tipo()
             if not self.consumir(";"): return

    def especificacao_tipo(self):
        lexema = self.atomo_atual.lexema.lower()
        if lexema == "integer":
            self.consumir("integer")
        elif lexema == "boolean":
            self.consumir("boolean")
        else:
            self.erro(["integer", "boolean"])

    def lista_identificadores(self):
        if not self.consumir(IDENTIFICADOR): return
        while self.atomo_atual.lexema == ",":
            self.consumir(",")
            if not self.consumir(IDENTIFICADOR): return

    def comando_composto(self):
        if not self.consumir("begin"): return
        self.lista_comandos()
        if not self.consumir("end"): return

    def lista_comandos(self):
        self.comando()
        while self.atomo_atual.lexema == ";":
            self.consumir(";")
            if not (self.atomo_atual.lexema.lower() == "end" or self.atomo_atual.tipo == EOS):
                self.comando()

    def comando(self):
        tipo = self.atomo_atual.tipo
        lexema = self.atomo_atual.lexema.lower()
        
        if tipo == IDENTIFICADOR: 
            self.comando_atribuicao()
        elif lexema == "if":
            self.comando_se()
        elif lexema == "while":
            self.comando_enquanto()
        elif lexema == "read":
            self.comando_leitura()
        elif lexema == "write":
            self.comando_escrita()
        elif lexema == "begin":
            self.comando_composto()

    def comando_atribuicao(self):
        if not self.consumir(IDENTIFICADOR): return
        if not self.consumir(":="): return
        self.expressao()

    def comando_se(self):
        if not self.consumir("if"): return
        self.condicao()
        if not self.consumir("then"): return
        self.comando()
        if self.atomo_atual.lexema.lower() == "else":
            self.consumir("else")
            self.comando()

    def comando_enquanto(self):
        if not self.consumir("while"): return
        self.condicao()
        if not self.consumir("do"): return
        self.comando()

    def comando_leitura(self):
        if not self.consumir("read"): return
        if not self.consumir("("): return
        self.lista_identificadores()
        if not self.consumir(")"): return

    def comando_escrita(self):
        if not self.consumir("write"): return
        if not self.consumir("("): return
        self.lista_expressoes()
        if not self.consumir(")"): return

    def lista_expressoes(self):
        self.expressao()
        while self.atomo_atual.lexema == ",":
            self.consumir(",")
            self.expressao()

    def condicao(self):
        if self.atomo_atual.lexema.lower() == "not":
            self.consumir("not")
            self.condicao()
        elif self.atomo_atual.lexema == "(":
            self.consumir("(")
            self.condicao()
            if not self.consumir(")"): return
        else:
            self.expressao()
            self.operador_relacional()
            self.expressao()

    def expressao(self):
        self.termo()
        while self.atomo_atual.lexema in ("+", "-"):
            self.consumir(self.atomo_atual.lexema) 
            self.termo()

    def termo(self):
        self.fator()
        while self.atomo_atual.lexema.lower() in ("*", "/", "div", "mod"):
            self.consumir(self.atomo_atual.lexema)
            self.fator()

    def fator(self):
        tipo = self.atomo_atual.tipo
        lexema = self.atomo_atual.lexema.lower()
        
        if tipo == IDENTIFICADOR:
            self.consumir(IDENTIFICADOR)
        elif tipo == NUM_INT:
            self.consumir(NUM_INT)
        elif tipo == NUM_REAL:
            self.consumir(NUM_REAL)
        elif lexema == "true":
            self.consumir("true")
        elif lexema == "false":
            self.consumir("false")
        elif lexema == "(":
            self.consumir("(")
            self.expressao()
            if not self.consumir(")"): return
        elif lexema == "not":
            self.consumir("not")
            self.fator()
        else:
            self.erro([IDENTIFICADOR, NUM_INT, NUM_REAL, "true", "false", "(", "not"])

    def operador_relacional(self):
        rel_ops = ["=", "<>", "<", "<=", ">", ">=", "!="]
        if self.atomo_atual.lexema in rel_ops:
            self.consumir(self.atomo_atual.lexema)
        else:
            self.erro(rel_ops)

def main():
    try:
        with open('entrada.txt', 'r') as f:
            buffer = f.read()
    except FileNotFoundError:
        print("Erro: Crie o arquivo 'entrada.txt' na mesma pasta.")
        return

    print("--- Iniciando Compilador ---")
    
    lexer = AnalisadorLexico(buffer)
    parser = AnalisadorSintatico(lexer)
    
    # Chama o método que agora se chama "analisar"
    parser.analisar()

if __name__ == "__main__":
    main()
