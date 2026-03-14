from typing import NamedTuple, Union

# Átomos (tokens)
ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4
RELOP = 5
ADDOP = 6
MULOP = 7

# Operadores Relacionais
LE = 1000
NE = 1001
LT = 1002
GE = 1003
GT = 1004
EQ = 1005

PALAVRAS_RESERVADAS = ["begin", "boolean", "div", "do", "else", "end", "false", "if", "integer", "mod", "program", "read", "then", "true", "not", "var", "while",
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

    def peek(self, i=0):
        index = self.position + i
        return self.code[index] if index < len(self.code) else None

    def skip_whitespace_and_comments(self):
        char = self.code[self.position]
        skip_chars = [' ', '\t', '\r', '\n']

        # Trata comentários e caracters não interessantes
        while True:
            char = self.peek()
            if char is None: break
            
            if char in skip_chars:
                self.advance()
                advance = self.peek(1)
            elif [char, self.peek(1)] == ['(', '*']:
                self._skip_star_comment()
            elif char == '{':
                self._skip_curly_braces_comment()
            elif [char, self.peek(1)] == ['/', '/']:
                self._skip_line_comment()
            elif [char, self.peek(1)] == ['\0']:
                return Atomo (EOS, '', 0, self.current_line)
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
            if self.peek == '*' and self.peek(1) == ')':
                self.advance() # Consome *
                self.advance() # Consome )
                return self.advance()

atomo_msg = ['ERRO','IDENTIF','NUM_INT','NUM_REAL','EOS']
def main():
    buffer = "leia_arquivo ()"
    lex = AnalisadorLexico(buffer)
    atomo = lex.Atomo()
    while ( atomo.tipo != EOS and atomo.tipo != ERRO ):
        print (" Linha : {}".format(atomolinha))
        print ("-  ́a tomo : {}".format(atomo_msg[atomo.tipo]))
        print ("\t\ tlexema : {}".format(atomolexema))
        print ("\t\ tvalor : {}".format(atomovalor) )
        atomo = lex.proximo_atomo()

    print (" Linha: {}".format(atomo.linha))
    print (" - atomo: {} ".format(atomo_msg[atomo.tipo ]))
    print ("\t\ tlexema: {}".format(atomo.lexema))
    print ("\t\ tvalor: {}".format(atomo.valor))

main()