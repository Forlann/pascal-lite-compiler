source_file = "./source.pas"
from AnalisadorLexico import AnalisadorLexico

ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4
            
def analisar_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_fonte = arquivo.read()
            
        analisador = AnalisadorLexico(codigo_fonte)
        
        print(f"{'TIPO':<15} | {'LEXEMA':<15} | {'VALOR':<10} | {'LINHA'}")
        print("-" * 60)
        
        while True:
            atomo = analisador.next_atom()
            
            if atomo is None:
                print("Atomo esta vazio")
                break
                
            print(f"{str(atomo.type):<15} | {str(atomo.lexema):<15} | {str(atomo.value):<10} | {atomo.line}")
            
            if atomo.type == EOS:
                print("Fim do codigo")
                break

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")

analisar_arquivo(source_file)