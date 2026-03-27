import sys
from AnalisadorLexico import AnalisadorLexico, IDENTIFICADOR, NUM_INT, NUM_REAL, ERRO, EOS
from AnalisadorSintatico import AnalisadorSintatico

def formatar_atomo(atomo):
    tipo = atomo.type
    if tipo == IDENTIFICADOR:
        tipo_str = "IDENTIF"
    elif tipo == NUM_INT:
        tipo_str = "NUM"
    elif tipo == NUM_REAL:
        tipo_str = "NUM_REAL"
    else:
        tipo_str = str(tipo)

    linha = f"Linha: {atomo.line} - atomo: {tipo_str:<15} lexema: {atomo.lexema}"

    if tipo in (NUM_INT, NUM_REAL):
        linha += f"    valor: {atomo.value}"

    return linha

def analisar_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_fonte = arquivo.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        sys.exit(1)

    analisador_lexico = AnalisadorLexico(codigo_fonte)
    analisador_sintatico = AnalisadorSintatico(analisador_lexico, formatar_atomo)
    analisador_sintatico.regra_do_programa()

    total_linhas = analisador_lexico.current_line
    print(f"{total_linhas} linhas analisadas, programa sintaticamente correto.")

if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "./source.pas"
    analisar_arquivo(caminho)