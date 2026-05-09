# -----------------------------------------------------------------------------
# Compilador PascalLite - Fase 2: Análise Semântica e Geração de Código MEPA
#
# Integrantes do grupo:
#   - Kauê Forlan
#
# Disciplina: Compiladores - Faculdade Impacta de Tecnologia
# -----------------------------------------------------------------------------

import os
import sys
from AnalisadorLexico import AnalisadorLexico
from AnalisadorSintatico import AnalisadorSintatico


def caminho_saida_mepa(caminho_entrada):
    """Retorna o caminho do arquivo .mepa correspondente ao .pas de entrada."""
    base, _ = os.path.splitext(caminho_entrada)
    return base + ".mepa"


def analisar_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            codigo_fonte = arquivo.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.", file=sys.stderr)
        sys.exit(1)

    analisador_lexico = AnalisadorLexico(codigo_fonte)
    analisador_sintatico = AnalisadorSintatico(analisador_lexico)
    analisador_sintatico.regra_do_programa()

    # Grava o código MEPA gerado em arquivo .mepa ao lado do arquivo de entrada
    caminho_mepa = caminho_saida_mepa(caminho_arquivo)
    with open(caminho_mepa, "w", encoding="utf-8") as f:
        for instrucao in analisador_sintatico.saida_mepa:
            f.write(instrucao + "\n")


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "./source.pas"
    analisar_arquivo(caminho)
