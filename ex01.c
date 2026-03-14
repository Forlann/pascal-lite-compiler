#include <stdio.h>

/* Programa de teste para o contador 
   Soma simples de dois valores
*/

int somar(int a, int b) {
    return a + b;
}

int main() {
    int valor1 = 10;
    int valor2 = 25;
    int resultado;

    resultado = somar(valor1, valor2);

    printf("A soma de %d e %d e igual a: %d\n", valor1, valor2, resultado);

    return 0;
}