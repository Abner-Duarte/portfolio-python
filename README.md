# Portfólio Python — Abner Duarte

Jogos pequenos feitos com **Python + Pygame Zero**, escritos com código simples e comentado em português, pensados para quem está aprendendo.

| Projeto | O que é |
|---|---|
| [Coletor de Estrelas](coletor-de-estrelas/) | Pegue estrelas com a nave antes do tempo acabar e fuja dos meteoros |
| [Chuva de Frutas](chuva-de-frutas/) | Pegue as frutas com a cesta e desvie das bombas |
| [Desafios-Dev](https://github.com/darkslipx/Desafios-Dev) | Scripts em Python puro: controle de estoque com menu, cálculo de comissão e de juros (JSON, funções, laços e validação de entrada) |

## Como rodar os jogos

```bash
pip install pgzero
cd coletor-de-estrelas
pgzrun coletor.py
```

> No Python 3.14, o `pygame` ainda não tem instalador pronto. Nesse caso, use:
> `pip install pygame-ce numpy` e depois `pip install --no-deps pgzero`.
