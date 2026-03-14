from typing import NamedTuple, Union

ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4

RESERVED_WORDS = ["begin", "boolean", "div", "do", "else", "end", "false", "if", "integer", "mod", "program", "read", "then", "true", "not", "var", "while",
"write"]

class Atomo(NamedTuple):
    type: int
    lexema: str
    value: Union[int, float, str]
    line: int

class AnalisadorLexico:
    def __init__(self, source_code):
        self.code = source_code
        self.position = 0
        self.current_line = 1

    def advance(self):
        char = self.peek()
        if char:
            if char == '\n':
                self.current_line += 1
            self.position += 1

        return char
    
    def retreat(self):
        self.position -= 1

    def peek(self, i=0):
        index = self.position + i
        return self.code[index] if index < len(self.code) else None
    
    def next_atom(self):
        self.skip_whitespace_and_comments()

        char = self.peek()

        if char is None:
            return Atomo(EOS, "EOF", 0, self.current_line)
        
        if char.isalpha() or char == "_":
            return self.handle_identifiers(char)
        
        if char.isdigit():
            return self.handle_digits(char)
        
        delimiters = {
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
    
        if char in delimiters:
            self.advance()
            return Atomo(delimiters[char], char, 0, self.current_line)
        
        print("Caracter Inválido")
    
    def handle_identifiers(self, c):
        self.advance() # Consome a 1ª letra (que já estava salva no c)
        lexema = c
        c = self.advance()
        stage = 1

        while True:
            if stage == 1:
                if c.isalnum(): # letras ou dígitos
                    lexema += c
                    c = self.advance()
                else:
                    if lexema in RESERVED_WORDS:
                        # print("É uma palavra reservada")
                        return Atomo(lexema.upper(), lexema, 0, self.current_line)
                    stage = 2
            elif stage == 2:
                self.retreat()
                return Atomo(IDENTIFICADOR, lexema, 0, self.current_line)


    def handle_digits(self, c):
        lexema = c
        self.advance()
        c = self.advance()
        stage = 1

        while True:
            if stage == 1:
                if c.isdigit():
                    lexema += c
                    c = self.advance()
                elif c == '.':
                    lexema += c
                    stage = 3
                    c = self.advance()
                elif c.isalpha():
                     return Atomo(ERRO, lexema, 0, self.current_line)
                else:
                    stage = 2 # É Inteiro

            elif stage == 2:
                self.retreat()
                return Atomo(NUM_INT, lexema, int(lexema), self.current_line)

            elif stage == 3: # Parte decimal
                if c.isdigit():
                    lexema += c
                    stage = 4
                    c = self.advance()
                else:
                    return Atomo(ERRO, lexema, 0, self.current_line)

            elif stage == 4:
                if c.isdigit():
                    lexema += c
                    c = self.advance()
                elif c.isalpha():
                    return Atomo(ERRO, lexema, 0, self.current_line)
                else:
                    stage = 5

            elif stage == 5:
                self.retreat()
                return Atomo(NUM_REAL, lexema, float(lexema), self.current_line)

    def skip_whitespace_and_comments(self):
        # char = self.code[self.position]
        skip_chars = [' ', '\t', '\r', '\n']

        # Trata comentários e caracters não interessantes
        while True:
            char = self.peek()
            if char is None: break
            
            if char in skip_chars:
                self.advance()
            elif [char, self.peek(1)] == ['(', '*']:
                self._skip_star_comment()
            elif char == '{':
                self._skip_curly_braces_comment()
            elif [char, self.peek(1)] == ['/', '/']:
                self._skip_line_comment()
            else: 
                break

    def _skip_line_comment(self):
        # Avança os //
        self.advance()
        self.advance()
        while self.peek() and self.peek() != '\n':
            self.advance()
            
    def _skip_curly_braces_comment(self):
        self.advance() # Consome {
        while self.peek() and self.peek() !=  '}':
            self.advance()
        self.advance() # Consome }
        
    def _skip_star_comment(self):
        # Consome ( e *
        self.advance() 
        self.advance()
        
        while self.peek():
            if self.peek() == '*' and self.peek(1) == ')':
                self.advance() # Consome *
                self.advance() # Consome )
                return self.advance()