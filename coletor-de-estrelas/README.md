# Coletor de Estrelas

![Tela do jogo](tela.png)

Pilote a nave e pegue o máximo de estrelas antes de o tempo acabar.

- **Setas ou WASD** movem a nave (com inércia: ela acelera e vai parando aos poucos).
- Estrelas pegas em sequência, com menos de 2,5 s entre uma e outra, formam **COMBO**: a 2ª vale 2 pontos, a 3ª vale 3, até x5.
- Cada **meteoro** que bate tira **3 segundos**, zera o combo e faz a tela tremer.
- O **relógio azul** aparece de vez em quando e devolve **3 segundos**.
- Os meteoros ficam mais rápidos e mais numerosos com o tempo.
- O **recorde** fica salvo em `recorde.txt`.

Menu com botões (mouse ou teclado): **ENTER** joga, **M** liga/desliga o som, **ESC** volta ao menu ou sai.

## Como rodar

```bash
pip install pgzero
cd coletor-de-estrelas
pgzrun coletor.py
```

## O que o código usa

| Conceito | Onde |
|---|---|
| Variáveis e estados | `estado` alterna entre `"menu"`, `"jogando"` e `"fim"` |
| Condicionais (`if`) | `mover_nave()`: cada seta acelera a nave numa direção |
| Laços (`for`) | `update()`: cada meteoro anda, gira e confere se bateu na nave |
| Funções | `pegar_estrela()`, `bater_em_meteoro()`, `comecar_jogo()` |
| Classes | `Particula`, `Onda` e `TextoFlutuante` (os efeitos visuais) |
| Listas | `meteoros`, `efeitos` e as `camadas` de estrelas do fundo (parallax) |
| Colisão | distância entre centros com `math.hypot` |
| Matemática | `math.sin` faz a estrela flutuar e o título balançar |
| Arquivos | `ler_recorde()` e `salvar_recorde()` |
| Mouse e teclado | `on_mouse_move`, `on_mouse_down` e `on_key_down` |

## Arte e sons

Tudo em `images/` e `sounds/` é gerado por código em `ferramentas/gerar_arte.py` (Pillow + módulo `wave`).
A fonte é a [Orbitron](https://fonts.google.com/specimen/Orbitron), licença OFL (`fonts/OFL.txt`).
