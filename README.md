# pascal-lite-compiler

Compilador para a linguagem **PascalLite** — um subconjunto simplificado de Pascal — implementado em Python como trabalho da disciplina de Compiladores.

O compilador realiza as fases de **análise léxica** e **análise sintática**, imprimindo cada átomo reconhecido e reportando erros com linha e descrição.

---

## Linguagem suportada (PascalLite)

Subconjunto de Pascal com suporte apenas a:

- Tipos: `integer` e `boolean`
- Declaração de variáveis (`var`)
- Comandos: atribuição (`:=`), `read`, `write`, `if/then/else`, `while/do`, `begin/end`
- Expressões com operadores aritméticos (`+`, `-`, `*`, `/`, `div`, `mod`), relacionais (`<`, `<=`, `=`, `<>`, `>`, `>=`) e booleanos (`and`, `or`, `not`)
- Comentários de linha (`//`), de bloco (`(* ... *)`) e entre chaves (`{ ... }`)
- Identificadores de até 20 caracteres, podendo iniciar com `_`

Funções e procedimentos **não** são suportados.

---

## Estrutura do projeto

```
.
├── compiler/
│   ├── main.py                  # Ponto de entrada
│   ├── AnalisadorLexico.py      # Análise léxica (tokenizador)
│   └── AnalisadorSintatico.py   # Análise sintática
├── examples/
│   ├── test_valido.pas          # Programa sintaticamente correto (if/else)
│   ├── test_while.pas           # Programa correto com while
│   ├── test_and_or.pas          # Uso de operadores booleanos and/or
│   ├── test_erro_lexico.pas     # Identificador com mais de 20 caracteres
│   ├── test_erro_sintatico.pas  # Erro de atribuição sem :=
│   ├── test_comentario_bug.pas  # Comentário (* *) sem espaço antes do próximo token
│   └── test_numero_fim.pas      # Programa sem ponto final
├── source.pas                   # Exemplo principal

```

---

## Como executar

```bash
cd compiler
py main.py ../source.pas
```

Ou informe qualquer arquivo `.pas`:

```bash
py main.py ../examples/test_valido.pas
```

---

## Formato de saída

Cada átomo reconhecido é impresso em uma linha:

```
Linha: 1 - atomo: PROGRAM         lexema: program
Linha: 1 - atomo: IDENTIF         lexema: ex01
Linha: 1 - atomo: PONTO_VIRG      lexema: ;
```

Para números, o valor é exibido ao final:

```
Linha: 6 - atomo: NUM             lexema: 10    valor: 10
```

Ao final de um programa correto:

```
14 linhas analisadas, programa sintaticamente correto.
```

Em caso de erro léxico:

```
Erro léxico: identificador 'identificador_muito_longo_demais' excede 20 caracteres na linha 4
```

Em caso de erro sintático:

```
Erro sintático: Esperado [PONTO] encontrado [EOS] na linha 14
```

---

## Tokens reconhecidos

| Categoria | Exemplos de lexemas |
|---|---|
| Palavras reservadas | `program`, `begin`, `end`, `var`, `if`, `then`, `else`, `while`, `do`, `read`, `write`, `and`, `or`, `not`, `true`, `false`, `integer`, `boolean`, `div`, `mod` |
| Identificador | `IDENTIF` |
| Número inteiro | `NUM` |
| Número real | `NUM_REAL` |
| Operadores e delimitadores | `:=`, `+`, `-`, `*`, `/`, `=`, `<`, `>`, `<=`, `>=`, `<>`, `;`, `,`, `:`, `(`, `)`, `.` |
