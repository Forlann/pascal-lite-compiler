import os

def analisar_arquivo_c(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return

    contagem_caracteres = {}
    espacos_branco = 0
    linhas = 0
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
            
            # Tamanho do arquivo em bytes
            tamanho_bytes = os.path.getsize(caminho_arquivo)
            
            # Contagem de linhas (baseado nas quebras de linha)
            linhas = conteudo.count('\n') + (1 if conteudo and not conteudo.endswith('\n') else 0)

            for char in conteudo:
                if char.isalnum():  # Verifica se é letra ou dígito
                    contagem_caracteres[char] = contagem_caracteres.get(char, 0) + 1
                elif char.isspace(): # Espaços, tabs e novas linhas
                    espacos_branco += 1

        # Ordenar por quantidade (valor) em ordem crescente
        listagem_ordenada = sorted(contagem_caracteres.items(), key=lambda item: item[1])

        # Exibição dos resultados
        print("-" * 30)
        print(f"ANÁLISE DO ARQUIVO: {caminho_arquivo}")
        print("-" * 30)
        
        print("Listagem de Letras e Dígitos (Ordem Crescente):")
        for char, qtd in listagem_ordenada:
            print(f" '{char}': {qtd}")

        print("-" * 30)
        print(f"Quantidade de espaços em branco: {espacos_branco}")
        print(f"Número de linhas: {linhas}")
        print(f"Tamanho do arquivo: {tamanho_bytes} bytes")
        print("-" * 30)

    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

# Execução
if __name__ == "__main__":
    nome_arq = r"C:/Users/2203008/Desktop/teste/ex01.c"
    analisar_arquivo_c(nome_arq)