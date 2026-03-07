class AnalisadorLexico:
    def __init__(self, source_code):
        self.code = source_code
        self.position = 0
        self.current_line = 1
        # Lista de palavras reservadas conforme o PDF [cite: 66]
        self.palavras_reservadas = [
            'begin', 'boolean', 'div', 'do', 'else', 'end', 'false', 'if',
            'integer', 'mod', 'program', 'read', 'then', 'true', 'not', 'var', 'while', 'write'
        ]

    def peak_char(self, i=0):
        """Olha o caractere à frente sem mover o ponteiro de posição."""
        if self.position + i < len(self.code):
            return self.code[self.position + i]
        return None

    def next_char(self):
        """Lê o próximo caractere e avança a posição."""
        char = self.peak_char()
        if char:
            if char == '\n':
                self.current_line += 1
            self.position += 1
        return char

    def skip_ignorable(self):
        """Ignora espaços e comentários, mantendo a contagem de linhas[cite: 61, 65]."""
        while True:
            char = self.peak_char()
            
            # 1. Espaços em branco e quebras de linha [cite: 61]
            if char in [' ', '\t', '\r', '\n']:
                self.next_char()
                continue
            
            # 2. Comentários de linha // [cite: 62]
            if char == '/' and self.peak_char(1) == '/':
                while self.peak_char() and self.peak_char() != '\n':
                    self.next_char()
                continue

            # 3. Comentários de bloco (* *) [cite: 63]
            if char == '(' and self.peak_char(1) == '*':
                self.next_char() # consome (
                self.next_char() # consome *
                while self.peak_char() and not (self.peak_char() == '*' and self.peak_char(1) == ')'):
                    self.next_char()
                self.next_char() # consome *
                self.next_char() # consome )
                continue

            # 4. Comentários de bloco { } [cite: 64]
            if char == '{':
                while self.peak_char() and self.peak_char() != '}':
                    self.next_char()
                self.next_char() # consome }
                continue
            
            break # Se não for espaço nem comentário, para de pular

    def obter_atomo(self):
        """A função principal que o analisador sintático chamará[cite: 7]."""
        self.skip_ignorable()
        char = self.peak_char()

        if char is None:
            return {'atomo': 'EOF', 'lexema': 'EOF', 'linha': self.current_line}

        # Reconhecimento de Identificadores e Palavras Reservadas [cite: 67, 68]
        if char.isalpha() or char == '_':
            lexema = ""
            while char and (char.isalnum() or char == '_'):
                lexema += self.next_char()
                char = self.peak_char()
            
            # Erro de tamanho de identificador 
            if len(lexema) > 20:
                return f"Erro Léxico: Identificador '{lexema}' muito longo na linha {self.current_line}"

            tipo = lexema.upper() if lexema in self.palavras_reservadas else 'IDENTIF'
            return {'atomo': tipo, 'lexema': lexema, 'linha': self.current_line}

        # Reconhecimento de Números 
        if char.isdigit():
            lexema = ""
            while char and char.isdigit():
                lexema += self.next_char()
                char = self.peak_char()
            return {'atomo': 'NUM', 'lexema': lexema, 'linha': self.current_line}

        # Reconhecimento de Operadores e Delimitadores 
        # Exemplo para atribuição ':='
        if char == ':' and self.peak_char(1) == '=':
            self.next_char(); self.next_char()
            return {'atomo': 'ATRIB', 'lexema': ':=', 'linha': self.current_line}
        
        # Outros símbolos simples (ponto e vírgula, etc)
        simbolos = {';': 'PONTO_VIRG', ':': 'DOIS_PONTOS', ',': 'VIRGULA', '.': 'PONTO', 
                    '(': 'ABRE_PARENTES', ')': 'FECHA_PARENTES', '+': 'SOMA', '-': 'SUB'}
        
        if char in simbolos:
            lex = self.next_char()
            return {'atomo': simbolos[lex], 'lexema': lex, 'linha': self.current_line}

        # Se chegar aqui e não reconhecer nada, é erro léxico [cite: 79]
        return f"Erro Léxico: Caractere inesperado '{self.next_char()}' na linha {self.current_line}"