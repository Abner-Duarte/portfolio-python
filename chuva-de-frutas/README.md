# Chuva de Frutas

![Tela do jogo](tela.png)

Mexa a cesta com as **setas** (ou **A** e **D**) e pegue as frutas que caem.
As **bombas** tiram uma vida, e você tem **3 vidas**. A cada 10 pontos, tudo cai mais rápido.
No fim, aperte **ESPAÇO** para jogar de novo.

## Como rodar

```bash
pip install pgzero
pgzrun frutas.py
```

## O que o código usa

| Conceito | Onde |
|---|---|
| Listas | `itens` guarda tudo o que está caindo, e `FRUTAS` guarda os tipos de fruta |
| Laço (`for`) | `update()` percorre a lista e faz cada item descer |
| Condicionais (`if / elif / else`) | `pegou_item()`: fruta dá ponto, bomba tira vida |
| Funções | `criar_item()`, `pegou_item()`, `desenhar_vidas()` |
| Sorteio | `random.random()` decide se vem bomba, `random.choice()` escolhe a fruta |
| Operador `%` | `pontos % 10 == 0` acelera o jogo a cada 10 pontos |
