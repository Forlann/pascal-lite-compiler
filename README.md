# pascal-lite-compiler

Compilador para a linguagem **PascalLite** — um subconjunto simplificado de Pascal — implementado em Python como trabalho da disciplina de Compiladores.

O compilador realiza:

- **Análise léxica** — tokenização do código-fonte com reporte de erros léxicos.
- **Análise sintática** — parser recursivo descendente sobre a gramática de PascalLite, com erros sintáticos detalhados (átomo esperado vs. encontrado).
- **Análise semântica** — minitabela de símbolos com verificação de declaração única e uso de identificadores declarados.
- **Geração de código intermediário MEPA** — instruções emitidas em ações semânticas embutidas nas funções recursivas do parser, no estilo Kowaltowski.

---

## Linguagem suportada (PascalLite — fase 2)

A fase 2 simplifica a gramática original conforme o enunciado: o compilador trata **tudo como inteiro** (não há mais distinção entre expressões inteiras e lógicas).

Subconjunto de Pascal com suporte a:

- Tipo: `integer`
- Declaração de variáveis (`var`)
- Comandos: atribuição (`:=`), `read`, `write`, `if/then/else`, `while/do`, `begin/end`
- Expressões com operadores aritméticos (`+`, `-`, `*`, `/`, `div`, `mod`) e relacionais (`<`, `<=`, `=`, `<>`, `>`, `>=`)
- Comentários de linha (`//`), de bloco (`(* ... *)`) e entre chaves (`{ ... }`)
- Identificadores de até 20 caracteres, podendo iniciar com `_`

> **Removido na fase 2** (vs. fase 1): tipo `boolean`, constantes `true`/`false`, operadores `and`/`or`/`not`. Funções e procedimentos continuam **não** suportados.

---

## Estrutura do projeto

```
.
├── compiler/
│   ├── main.py                  # Ponto de entrada
│   ├── AnalisadorLexico.py      # Análise léxica (tokenizador)
│   ├── AnalisadorSintatico.py   # Análise sintática + semântica + geração MEPA
│   └── TabelaSimbolos.py        # Tabela de símbolos e erros semânticos
├── examples/
│   ├── fatorial.pas             # Programa do enunciado da fase 2 (calcula fatorial)
│   ├── test_valido.pas          # Programa correto com if/else
│   ├── test_while.pas           # Programa correto com while
│   ├── test_expr_complexa.pas   # Expressão com precedência e unário negativo
│   ├── test_if_aninhado.pas     # Validação de rótulos em if/else aninhado
│   ├── test_while_aninhado.pas  # Validação de rótulos em while aninhado
│   ├── test_erro_sem_declarado.pas  # Erro semântico: variável não declarada
│   ├── test_erro_sem_duplicado.pas  # Erro semântico: identificador duplicado
│   ├── test_erro_lexico.pas     # Erro léxico: identificador > 20 caracteres
│   └── test_erro_sintatico.pas  # Erro sintático: atribuição sem :=
```

---

## Como executar

A partir da raiz do projeto:

```bash
py compiler/main.py examples/fatorial.pas
```

Ou entrando no diretório `compiler/`:

```bash
cd compiler
py main.py ../examples/fatorial.pas
```

O compilador:

1. Imprime as instruções MEPA geradas em **stdout**.
2. Grava o mesmo conteúdo em um arquivo **`.mepa`** ao lado do `.pas` (ex: `examples/fatorial.pas` → `examples/fatorial.mepa`).
3. Em caso de erro, imprime a mensagem em **stderr** e termina com **exit code 1**.

### Exemplo de execução

Entrada (`examples/fatorial.pas`):
```pascal
program exemplo1;
var fat, num, cont: integer;
begin
  read(num);
  fat := 1;
  cont := 2;
  while cont <= num do
  begin
    fat := fat * num;
    cont := cont + 1
  end;
  write(fat)
end.
```

Saída (stdout e `examples/fatorial.mepa`):
```
INPP
AMEM 3
LEIT
ARMZ 1
CRCT 1
ARMZ 0
CRCT 2
ARMZ 2
L1: NADA
CRVL 2
CRVL 1
CMEG
DSVF L2
CRVL 0
CRVL 1
MULT
ARMZ 0
CRVL 2
CRCT 1
SOMA
ARMZ 2
DSVS L1
L2: NADA
CRVL 0
IMPR
PARA
```

---

## Mensagens de erro

**Erro léxico** (identificador > 20 caracteres ou número malformado):
```
Erro léxico: identificador 'identificador_muito_longo_demais' excede 20 caracteres na linha 4
```

**Erro sintático** (átomo inesperado):
```
Erro sintático: Esperado [PONTO] encontrado [EOS] na linha 14
```

**Erro semântico** (variável não declarada ou redeclaração):
```
Erro semântico: identificador 'b' não declarado na linha 7
Erro semântico: identificador 'x' já declarado na linha 5
```

---

## Mapa de instruções MEPA geradas

| Construção PascalLite | Instruções MEPA |
|---|---|
| Início do programa | `INPP` |
| `var x, y: integer;` (n vars) | `AMEM n` |
| `read(x)` | `LEIT` + `ARMZ <end>` |
| `write(expr)` | `<expr>` + `IMPR` |
| Atribuição `x := expr` | `<expr>` + `ARMZ <end>` |
| Identificador em expressão | `CRVL <end>` |
| Constante numérica | `CRCT <valor>` |
| `+` / `-` / `*` / `div` ou `/` / `mod` | `SOMA` / `SUBT` / `MULT` / `DIVI` / `MOD` |
| Unário `-` | `INVR` |
| `<` / `<=` / `>` / `>=` / `=` / `<>` | `CMME` / `CMEG` / `CMMA` / `CMAG` / `CMIG` / `CMDG` |
| `if E then C` | `<E>` `DSVF L1` `<C>` `L1: NADA` |
| `if E then C1 else C2` | `<E>` `DSVF L1` `<C1>` `DSVS L2` `L1: NADA` `<C2>` `L2: NADA` |
| `while E do C` | `L1: NADA` `<E>` `DSVF L2` `<C>` `DSVS L1` `L2: NADA` |
| Fim do programa | `PARA` |

---

## Tokens reconhecidos pelo léxico

| Categoria | Exemplos de lexemas |
|---|---|
| Palavras reservadas | `program`, `begin`, `end`, `var`, `if`, `then`, `else`, `while`, `do`, `read`, `write`, `integer`, `div`, `mod` |
| Identificador | `IDENTIF` |
| Número inteiro | `NUM` |
| Operadores e delimitadores | `:=`, `+`, `-`, `*`, `/`, `=`, `<`, `>`, `<=`, `>=`, `<>`, `;`, `,`, `:`, `(`, `)`, `.` |

> Tokens `boolean`, `true`, `false`, `and`, `or`, `not` continuam reconhecidos pelo léxico (são palavras reservadas), mas o parser da fase 2 não os aceita em nenhuma produção, então o uso resulta em erro sintático.
