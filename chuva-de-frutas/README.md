# Chuva de Frutas

![Tela do jogo](tela.png)

Mexa a cesta com as **setas** (ou **A** e **D**) e pegue as frutas que caem.

- Cada fruta vale **1 ponto**, e a **estrela dourada** vale **5**.
- As **bombas** tiram uma vida (a tela treme), e você tem **3 vidas**.
- A cada 10 pontos você sobe de **nível** e tudo cai mais rápido.
- A fruta só conta se cair pela boca da cesta.

Aperte **ESPAÇO** para começar e para jogar de novo.

## Como rodar

```bash
pip install pgzero
cd chuva-de-frutas
pgzrun frutas.py
```

## O que o código usa

Este jogo foi escrito de propósito sem classes: os efeitos são feitos com listas e dicionários, para o código ficar fácil de acompanhar para quem está começando.

| Conceito | Onde |
|---|---|
| Listas | `itens` guarda tudo o que está caindo, `gotas` guarda os pedacinhos de suco |
| Dicionários | cada gota é um dicionário (`{"x": ..., "y": ..., "cor": ...}`) e `COR_DO_SUCO` liga cada fruta às suas cores |
| Laço (`for`) | `update()` percorre os itens e faz cada um cair, girar e balançar |
| Condicionais (`if / elif / else`) | `pegou_item()`: fruta dá ponto, estrela dá 5, bomba tira vida |
| Funções | `criar_item()`, `espirrar()`, `pegou_item()`, `desenhar_vidas()` |
| Sorteio | `random.random()` decide se vem bomba, estrela ou fruta |
| Divisão inteira `//` | `pontos // 10` descobre quando subir de nível |
| Matemática | `math.sin` faz as frutas balançarem e o título flutuar |
| Estados | `estado` alterna entre `"inicio"`, `"jogando"` e `"fim"` |

## Arte e sons

Tudo em `images/` e `sounds/` é gerado por código em `ferramentas/gerar_arte.py` (Pillow + módulo `wave`).
A fonte é a [Fredoka](https://fonts.google.com/specimen/Fredoka), licença OFL (`fonts/OFL.txt`).
