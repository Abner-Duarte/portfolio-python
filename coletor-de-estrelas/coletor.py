# Coletor de Estrelas
# Pilote a nave com as setas, pegue o máximo de estrelas em 30 segundos
# e fuja dos meteoros (cada batida tira 3 segundos do relógio).
#
# Para rodar:  pgzrun coletor.py

import random

# Tamanho da janela do jogo
WIDTH = 640
HEIGHT = 480
TITLE = "Coletor de Estrelas"

VELOCIDADE_NAVE = 5
TEMPO_INICIAL = 30

# Os "atores" são as imagens que aparecem na tela (ficam na pasta images/)
nave = Actor("nave")
estrela = Actor("estrela")
meteoros = []

# Pontinhos brancos do fundo (só enfeite): cada um é um par (x, y)
fundo = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(60)]

pontos = 0
tempo = TEMPO_INICIAL
fim_de_jogo = False
quadro = 0          # contador de quadros desenhados (para piscar)
protegida = False   # depois de uma batida, a nave fica 1,5 s protegida


def mudar_estrela_de_lugar():
    """Sorteia uma nova posição para a estrela."""
    estrela.x = random.randint(30, WIDTH - 30)
    estrela.y = random.randint(60, HEIGHT - 30)


def criar_meteoro():
    """Cria um meteoro na direita da tela, numa altura sorteada."""
    meteoro = Actor("meteoro")
    mandar_meteoro_para_direita(meteoro)
    meteoros.append(meteoro)


def mandar_meteoro_para_direita(meteoro):
    """Coloca o meteoro fora da tela, à direita, com altura e velocidade sorteadas."""
    meteoro.x = WIDTH + random.randint(50, 300)
    meteoro.y = random.randint(60, HEIGHT - 30)
    meteoro.velocidade = random.randint(3, 6)


def tirar_protecao():
    global protegida
    protegida = False


def contar_um_segundo():
    """O relógio do jogo chama esta função uma vez por segundo."""
    global tempo, fim_de_jogo
    if not fim_de_jogo:
        tempo -= 1
        if tempo <= 0:
            tempo = 0
            fim_de_jogo = True


def comecar_jogo():
    """Coloca tudo no lugar inicial. Usada no começo e ao jogar de novo."""
    global pontos, tempo, fim_de_jogo, protegida
    pontos = 0
    tempo = TEMPO_INICIAL
    fim_de_jogo = False
    protegida = False
    nave.pos = (WIDTH // 2, HEIGHT // 2)
    meteoros.clear()
    for _ in range(3):
        criar_meteoro()
    mudar_estrela_de_lugar()


def mover_nave():
    """Move a nave conforme a seta apertada, sem deixar sair da tela."""
    if keyboard.left and nave.left > 0:
        nave.x -= VELOCIDADE_NAVE
    if keyboard.right and nave.right < WIDTH:
        nave.x += VELOCIDADE_NAVE
    if keyboard.up and nave.top > 40:
        nave.y -= VELOCIDADE_NAVE
    if keyboard.down and nave.bottom < HEIGHT:
        nave.y += VELOCIDADE_NAVE


def update():
    """Roda sozinha umas 60 vezes por segundo: aqui fica a lógica do jogo."""
    global pontos, tempo, protegida

    if fim_de_jogo:
        return  # jogo parado, não mexe em nada

    mover_nave()

    # A nave encostou na estrela?
    if nave.colliderect(estrela):
        pontos += 1
        mudar_estrela_de_lugar()

    # Cada meteoro anda para a esquerda
    for meteoro in meteoros:
        meteoro.x -= meteoro.velocidade

        # Saiu pela esquerda? Volta pela direita
        if meteoro.right < 0:
            mandar_meteoro_para_direita(meteoro)

        # Bateu na nave (e ela não está protegida)? Perde 3 segundos
        if meteoro.colliderect(nave) and not protegida:
            tempo = max(0, tempo - 3)
            protegida = True
            clock.schedule(tirar_protecao, 1.5)
            mandar_meteoro_para_direita(meteoro)


def draw():
    """Desenha tudo na tela, também umas 60 vezes por segundo."""
    screen.fill((10, 10, 40))
    for x, y in fundo:
        screen.draw.filled_circle((x, y), 1, "white")

    estrela.draw()
    for meteoro in meteoros:
        meteoro.draw()
    # Protegida, a nave pisca: aparece em metade dos quadros
    if not protegida or piscar():
        nave.draw()

    screen.draw.text(f"Pontos: {pontos}", (10, 10), fontsize=32, color="yellow")
    cor_tempo = "red" if tempo <= 5 else "white"
    screen.draw.text(f"Tempo: {tempo}", topright=(WIDTH - 10, 10), fontsize=32, color=cor_tempo)

    if fim_de_jogo:
        palavra = "estrela" if pontos == 1 else "estrelas"
        screen.draw.text("FIM DE JOGO!", center=(WIDTH // 2, HEIGHT // 2 - 40), fontsize=72, color="orange")
        screen.draw.text(f"Você pegou {pontos} {palavra}", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=40, color="white")
        screen.draw.text("Aperte ESPAÇO para jogar de novo", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=30, color="lightblue")


def piscar():
    """Devolve True e False alternando, rápido, para fazer a nave piscar."""
    global quadro
    quadro += 1
    return quadro // 5 % 2 == 0


def on_key_down(key):
    """Chamada quando uma tecla é apertada."""
    if fim_de_jogo and key == keys.SPACE:
        comecar_jogo()


comecar_jogo()
clock.schedule_interval(contar_um_segundo, 1.0)
