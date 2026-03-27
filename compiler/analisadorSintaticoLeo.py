class AnalisadorSintatico:
    def __init__(self, lexer: AnalisadorLexico):
        self.lexer = lexer # Instância do analisador léxico para obter tokens
        self.current_atom = self.lexer.next_atom() # O token atual que está sendo processado
        self.errors = [] # Lista para armazenar erros sintáticos encontrados

    def error(self, expected_types: list):
        # Relata um erro de sintaxe.
        # Imprime uma mensagem de erro e adiciona à lista de erros.
        # Em parsers mais avançados, aqui haveria uma estratégia de recuperação de erros mais sofisticada.
        found_type = self.current_atom.type
        found_lexema = self.current_atom.lexema
        line = self.current_atom.line
        error_msg = f"Erro de sintaxe na linha {line}: Esperado {', '.join(expected_types)}, encontrado {found_type} ('{found_lexema}')"
        self.errors.append(error_msg)
        print(error_msg)
        # Por simplicidade, avança para o próximo token para tentar continuar a análise
        # e evitar um loop infinito em caso de erro.
        self.current_atom = self.lexer.next_atom()

    def eat(self, atom_type: str) -> bool:
        # "Come" (consome) o token atual se ele for do tipo esperado.
        # Se o tipo do token atual corresponder ao `atom_type` esperado, avança para o próximo token.
        # Caso contrário, reporta um erro sintático.
        if self.current_atom.type == atom_type:
            self.current_atom = self.lexer.next_atom()
            return True
        else:
            self.error([atom_type])
            return False

    def parse(self):
        # Método principal para iniciar a análise sintática.
        print("Iniciando análise sintática...")
        self.program() # Chama a regra inicial da gramática (program)
        
        # Verifica se houve erros e se o analisador chegou ao fim do arquivo (EOS).
        if not self.errors and self.current_atom.type == EOS:
            print("Análise sintática concluída com sucesso!")
            return True
        else:
            print("Análise sintática concluída com erros.")
            for err in self.errors:
                print(err)
            return False

    # =============================================================================
    # IMPLEMENTAÇÃO DAS REGRAS GRAMATICAIS (MÉTODOS DE DESCIDA RECURSIVA)
    # =============================================================================

    def program(self):
        # Regra: program -> PROGRAM ID ; block .
        if not self.eat("PROGRAM"): return
        if not self.eat(IDENTIFICADOR): return
        if not self.eat("PONTO_VIRG"): return
        self.block()
        if not self.eat("PONTO"): return

    def block(self):
        # Regra: block -> [VAR declarations] [subprogram_declarations] compound_statement
        # Bloco de declarações de variáveis é opcional.
        if self.current_atom.type == "VAR":
            self.declarations()
        # Subprogram_declarations (procedimentos/funções) podem ser adicionados aqui se a gramática for expandida.
        # if self.current_atom.type == "PROCEDURE" or self.current_atom.type == "FUNCTION":
        #     self.subprogram_declarations()
        self.compound_statement() # Um bloco sempre termina com um compound_statement.

    def declarations(self):
        # Regra: declarations -> VAR ID_LIST : type ; { declarations } (Simplificado para Pascal Lite)
        # A gramática aqui permite um ou mais grupos de declaração 'VAR ... : type ;'
        if not self.eat("VAR"): return
        self.id_list()
        if not self.eat("DOIS_PONTOS"): return
        self.type_spec()
        if not self.eat("PONTO_VIRG"): return
        # Permite múltiplas seções VAR ou declarações contínuas de identificadores.
        # A gramática Pascal real é mais flexível, mas esta implementação suporta:
        # VAR id1, id2 : type1; 
        # VAR id3 : type2;
        # Ou
        # VAR id1, id2 : type1; id3, id4 : type2;
        while self.current_atom.type == IDENTIFICADOR or self.current_atom.type == "VAR":
             if self.current_atom.type == "VAR": # Novo bloco de declaração VAR
                 self.eat("VAR") # Consome o VAR
             self.id_list()
             if not self.eat("DOIS_PONTOS"): return
             self.type_spec()
             if not self.eat("PONTO_VIRG"): return

    def type_spec(self):
        # Regra: type -> INTEGER | BOOLEAN
        if self.current_atom.type == "INTEGER":
            self.eat("INTEGER")
        elif self.current_atom.type == "BOOLEAN":
            self.eat("BOOLEAN")
        else:
            self.error(["INTEGER", "BOOLEAN"])

    def id_list(self):
        # Regra: ID_LIST -> ID { , ID }
        # Uma lista de identificadores separados por vírgulas.
        if not self.eat(IDENTIFICADOR): return
        while self.current_atom.type == "VIRGULA":
            self.eat("VIRGULA")
            if not self.eat(IDENTIFICADOR): return # Deve ter um ID após a vírgula

    def compound_statement(self):
        # Regra: compound_statement -> BEGIN statement_list END
        # Um bloco de statements delimitado por BEGIN e END.
        if not self.eat("BEGIN"): return
        self.statement_list()
        if not self.eat("END"): return

    def statement_list(self):
        # Regra: statement_list -> statement { ; statement }
        # Uma lista de statements, onde cada statement é opcionalmente seguido por ';'.
        self.statement()
        while self.current_atom.type == "PONTO_VIRG":
            self.eat("PONTO_VIRG")
            # Permite statements vazios (e.g., 'A:=1;; B:=2;') ou o ponto e vírgula antes de END.
            # Se o próximo token for END ou EOS, não esperamos outro statement.
            if not (self.current_atom.type == "END" or self.current_atom.type == EOS):
                self.statement()

    def statement(self):
        # Regra: statement -> assignment_statement
        #                  | if_statement
        #                  | while_statement
        #                  | read_statement
        #                  | write_statement
        #                  | compound_statement
        #                  | (empty) - implicitamente tratado se nenhum dos anteriores for correspondido
        # Determina o tipo de statement com base no token atual (lookahead).
        if self.current_atom.type == IDENTIFICADOR: # Pode ser um statement de atribuição
            self.assignment_statement()
        elif self.current_atom.type == "IF":
            self.if_statement()
        elif self.current_atom.type == "WHILE":
            self.while_statement()
        elif self.current_atom.type == "READ":
            self.read_statement()
        elif self.current_atom.type == "WRITE":
            self.write_statement()
        elif self.current_atom.type == "BEGIN":
            self.compound_statement()
        # Se não for nenhum dos tipos acima, pode ser um statement vazio ou um erro
        # O mecanismo de recuperação de erros no método error() pode ajudar aqui.
        # Para um statement vazio, simplesmente não fazemos nada, e o 'eat' do PONTO_VIRG 
        # na statement_list avança para o próximo token, efetivamente consumindo-o como um statement vazio.

    def assignment_statement(self):
        # Regra: assignment_statement -> ID ATRIBUICAO expression
        # Ex: x := 10
        if not self.eat(IDENTIFICADOR): return
        if not self.eat("ATRIBUICAO"): return # Espera o token ':='
        self.expression()

    def if_statement(self):
        # Regra: if_statement -> IF condition THEN statement [ELSE statement]
        # Ex: IF x > 0 THEN write(x) ELSE write(0)
        if not self.eat("IF"): return
        self.condition()
        if not self.eat("THEN"): return
        self.statement()
        if self.current_atom.type == "ELSE": # A cláusula ELSE é opcional
            self.eat("ELSE")
            self.statement()

    def while_statement(self):
        # Regra: while_statement -> WHILE condition DO statement
        # Ex: WHILE x > 0 DO x := x - 1
        if not self.eat("WHILE"): return
        self.condition()
        if not self.eat("DO"): return
        self.statement()

    def read_statement(self):
        # Regra: read_statement -> READ ( ID_LIST )
        # Ex: READ (x, y)
        if not self.eat("READ"): return
        if not self.eat("ABRE_PAR"): return
        self.id_list()
        if not self.eat("FECHA_PAR"): return

    def write_statement(self):
        # Regra: write_statement -> WRITE ( expression_list )
        # Ex: WRITE (x + y, 'Resultado')
        if not self.eat("WRITE"): return
        if not self.eat("ABRE_PAR"): return
        self.expression_list()
        if not self.eat("FECHA_PAR"): return

    def expression_list(self):
        # Regra: expression_list -> expression { , expression }
        # Uma lista de expressões separadas por vírgulas.
        self.expression()
        while self.current_atom.type == "VIRGULA":
            self.eat("VIRGULA")
            self.expression()

    def condition(self):
        # Regra: condition -> expression relational_operator expression
        #                  | NOT condition
        #                  | ( condition )
        # Lida com expressões booleanas e operadores relacionais.
        if self.current_atom.type == "NOT":
            self.eat("NOT")
            self.condition()
        elif self.current_atom.type == "ABRE_PAR":
            self.eat("ABRE_PAR")
            self.condition()
            if not self.eat("FECHA_PAR"): return
        else:
            self.expression() # Primeira expressão
            self.relational_operator() # Operador de comparação (ex: =, <, >)
            self.expression() # Segunda expressão

    def expression(self):
        # Regra: expression -> term { ( MAIS | MENOS ) term }
        # Lida com operações de adição e subtração (maior precedência para term).
        self.term()
        while self.current_atom.type in ("MAIS", "MENOS"):
            self.eat(self.current_atom.type) # Consome o operador (+ ou -)
            self.term()

    def term(self):
        # Regra: term -> factor { ( MULT | DIVISAO | DIV | MOD ) factor }
        # Lida com operações de multiplicação, divisão (/, DIV, MOD) (maior precedência para factor).
        self.factor()
        while self.current_atom.type in ("MULT", "DIVISAO", "DIV", "MOD"):
            self.eat(self.current_atom.type) # Consome o operador (*, /, DIV, MOD)
            self.factor()

    def factor(self):
        # Regra: factor -> ID | NUM_INT | NUM_REAL | TRUE | FALSE | ( expression ) | NOT factor
        # Elementos mais básicos de uma expressão.
        if self.current_atom.type == IDENTIFICADOR:
            self.eat(IDENTIFICADOR)
        elif self.current_atom.type == NUM_INT:
            self.eat(NUM_INT)
        elif self.current_atom.type == NUM_REAL:
            self.eat(NUM_REAL)
        elif self.current_atom.type == "TRUE":
            self.eat("TRUE")
        elif self.current_atom.type == "FALSE":
            self.eat("FALSE")
        elif self.current_atom.type == "ABRE_PAR":
            self.eat("ABRE_PAR")
            self.expression()
            if not self.eat("FECHA_PAR"): return
        elif self.current_atom.type == "NOT":
            self.eat("NOT")
            self.factor()
        else:
            # Se o token atual não corresponde a nenhum fator esperado, reporta um erro.
            self.error([IDENTIFICADOR, NUM_INT, NUM_REAL, "TRUE", "FALSE", "ABRE_PAR", "NOT"])

    def relational_operator(self):
        # Regra: relational_operator -> IGUAL | DIFERENTE | MENOR | MENOR_IGUAL | MAIOR | MAIOR_IGUAL
        # Consome qualquer um dos operadores relacionais válidos.
        rel_ops = ["IGUAL", "DIFERENTE", "MENOR", "MENOR_IGUAL", "MAIOR", "MAIOR_IGUAL"]
        if self.current_atom.type in rel_ops:
            self.eat(self.current_atom.type)
        else:
            self.error(rel_ops)
