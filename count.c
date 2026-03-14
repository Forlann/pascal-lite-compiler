/*
 * count.c
 *
 * Lê um arquivo fonte em C e conta:
 *  - ocorrência de letras (A..Z, a..z)
 *  - ocorrência de dígitos (0..9)
 *  - quantidade de espaços em branco (consideramos: ' ', '\t', '\v', '\f')
 *  - número de linhas
 *  - tamanho do arquivo em bytes
 *
 * Uso:
 *   gcc count.c -o count.exe
 *   .\count.exe nome_do_arquivo.c
 *
 * Observações / suposições:
 *  - Contamos letras separadamente por maiúsculas e minúsculas.
 *  - Imprimimos apenas símbolos com ocorrência > 0.
 *  - "Espaços em branco" aqui inclui espaço e tabulações (\t, \v, \f),
 *    mas exclui quebras de linha, pois as linhas são contadas separadamente.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s arquivo_fonte.c\n", argv[0]);
        return 2;
    }

    const char *filename = argv[1];
    FILE *f = fopen(filename, "rb");
    if (!f) {
        perror("Erro ao abrir o arquivo");
        return 1;
    }

    /* obter tamanho em bytes */
    if (fseek(f, 0, SEEK_END) != 0) {
        perror("fseek");
        fclose(f);
        return 1;
    }
    long filesize = ftell(f);
    if (filesize < 0) filesize = 0;
    rewind(f);

    long lines = 0;
    long spaces = 0; /* ' ' e tabulações */
    long digits[10] = {0};
    long upper[26] = {0};
    long lower[26] = {0};

    int c;
    int lastc = -1;
    while ((c = fgetc(f)) != EOF) {
        if (c == '\n') lines++;

        if (c == ' ' || c == '\t' || c == '\v' || c == '\f') {
            spaces++;
        }

        if (c >= '0' && c <= '9') {
            digits[c - '0']++;
        } else if (c >= 'A' && c <= 'Z') {
            upper[c - 'A']++;
        } else if (c >= 'a' && c <= 'z') {
            lower[c - 'a']++;
        }

        lastc = c;
    }

    /* Se o arquivo não estiver vazio e não terminar com '\n', conta última linha */
    if (filesize > 0 && lastc != '\n') lines++;

    fclose(f);

    printf("Relatório para: %s\n", filename);
    printf("Tamanho do arquivo: %ld bytes\n", filesize);
    printf("Número de linhas: %ld\n", lines);
    printf("Espaços em branco (espacos e tabs): %ld\n", spaces);

    /* Imprimir dígitos (0..9) se ocorrência > 0, em ordem crescente de símbolo */
    for (int i = 0; i < 10; ++i) {
        if (digits[i] > 0) {
            printf("'%c' : %ld\n", (char)('0' + i), digits[i]);
        }
    }

    /* Imprimir letras maiúsculas A..Z */
    for (int i = 0; i < 26; ++i) {
        if (upper[i] > 0) {
            printf("'%c' : %ld\n", (char)('A' + i), upper[i]);
        }
    }

    /* Imprimir letras minúsculas a..z */
    for (int i = 0; i < 26; ++i) {
        if (lower[i] > 0) {
            printf("'%c' : %ld\n", (char)('a' + i), lower[i]);
        }
    }

    return 0;
}
