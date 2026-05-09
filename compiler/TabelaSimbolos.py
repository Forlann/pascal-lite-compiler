import sys


def erro_semantico(mensagem, linha):
    print(f"Erro semântico: {mensagem} na linha {linha}", file=sys.stderr)
    sys.exit(1)


class TabelaSimbolos:
    def __init__(self):
        self._simbolos = {}
        self._proximo_endereco = 0

    def inserir(self, nome, tipo, linha):
        if nome in self._simbolos:
            erro_semantico(f"identificador '{nome}' já declarado", linha)
        self._simbolos[nome] = (self._proximo_endereco, tipo)
        self._proximo_endereco += 1

    def buscar(self, nome, linha):
        if nome not in self._simbolos:
            erro_semantico(f"identificador '{nome}' não declarado", linha)
        return self._simbolos[nome]

    def total(self):
        return self._proximo_endereco
