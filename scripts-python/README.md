# Scripts em Python puro

Três programas de terminal feitos só com recursos básicos do Python e módulos nativos (`json`, `uuid`, `datetime`). Nenhuma biblioteca para instalar.

| Script | O que faz | Conceitos |
|---|---|---|
| [`estoque.py`](estoque.py) | Menu de estoque: consulta, entrada, saída e histórico de movimentações | `while`, `if/elif`, dicionários, listas, funções, `try/except`, JSON, `uuid` |
| [`comissao.py`](comissao.py) | Lê as vendas de um JSON e calcula a comissão de cada vendedor | `for`, dicionário acumulador, f-strings formatadas em tabela |
| [`juros.py`](juros.py) | Calcula os juros de um título atrasado (2,5% ao dia) | `datetime`, diferença entre datas, validação de entrada |

## Como rodar

Dentro desta pasta (os scripts leem os arquivos JSON que estão nela):

```bash
python estoque.py
python comissao.py
python juros.py
```

## Estoque

Menu que roda num `while` até o usuário escolher sair. Os produtos do `estoque.json` viram um dicionário com o código como chave, então a busca é direta (`produtos[101]`). Cada movimentação ganha um ID único com `uuid.uuid4()` e vai para a lista de histórico.

```
==================================================
                MENU DE ESTOQUE
==================================================
  1. Consultar estoque
  2. Entrada de produtos
  3. Saída de produtos
  4. Histórico de movimentações
  0. Sair
==================================================
Escolha uma opção: 3

Código do produto: 101
Produto: Caneta Azul (estoque atual: 150 un)
Descrição da movimentação: Venda
Quantidade: 10

==================================================
            SAIDA REGISTRADA
==================================================
  ID:            cbfbbbc6-14e6-4757-bc6d-ae3bd3d06cb4
  Descrição:     Venda
  Produto:       Caneta Azul
  Quantidade:    -10
  Estoque final: 140 un
==================================================
```

Validações: código inexistente é recusado, a quantidade precisa ser maior que zero, saída maior que o estoque é bloqueada e texto no lugar de número não derruba o programa (a função `ler_inteiro()` pede de novo).

## Comissão

Regra por venda: abaixo de R$ 100 não tem comissão, abaixo de R$ 500 é 1% e a partir de R$ 500 é 5%.

```
==============================================================
                  COMISSÃO POR VENDEDOR
==============================================================
  Vendedor            Vendas    Total vendido       Comissão
--------------------------------------------------------------
  João Silva              10      R$ 10754.70      R$ 495.68
  Maria Souza              9       R$ 9874.30      R$ 465.95
  Carlos Oliveira          8       R$ 7928.35      R$ 379.37
  Ana Lima                 9       R$ 8763.95      R$ 404.98
--------------------------------------------------------------
  Total de comissões                              R$ 1745.98
==============================================================
```

## Juros

O usuário digita o valor (aceita vírgula ou ponto) e a data de vencimento. Subtrair duas datas dá um `timedelta`, e `.days` devolve os dias de atraso.

```
========================================
  Valor original:  R$ 1000.00
  Vencimento:      01/11/2026
  Data de hoje:    10/11/2026
----------------------------------------
  Dias em atraso:  9
  Juros (2,5%/dia): R$ 225.00
  Total a pagar:   R$ 1225.00
========================================
```
