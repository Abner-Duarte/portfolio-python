# Chuva de Frutas
# Mexa a cesta com as setas (ou A e D) e pegue as frutas que caem do céu.
# Cuidado com as bombas: cada uma tira uma vida. Você tem 3 vidas.
# A cada 10 pontos, as coisas caem mais rápido!
#
# Para rodar:  pgzrun frutas.py

import random

WIDTH = 640
HEIGHT = 480
TITLE = "Chuva de Frutas"

VELOCIDADE_CESTA = 7
FRUTAS = ["maca", "laranja", "uva"]   # nomes das imagens na pasta images/
CHANCE_DE_BOMBA = 0.2                 # 0.2 = 20% das coisas que caem são bombas

cesta = Actor("cesta")
itens = []        # lista com tudo que está caindo agora

pontos = 0
vidas = 3
velocidade_queda = 3
fim_de_jogo = False


def criar_item():
    """Cria uma fruta ou uma bomba no alto da tela."""
    if fim_de_jogo:
        return

    if random.random() < CHANCE_DE_BOMBA:
        item = Actor("bomba")
        item.tipo = "bomba"
    else:
        item = Actor(random.choice(FRUTAS))
        item.tipo = "fruta"

    item.x = random.randint(20, WIDTH - 20)
    item.y = -20                      # começa um pouquinho acima da tela
    itens.append(item)


def comecar_jogo():
    """Zera tudo para uma partida nova."""
    global pontos, vidas, velocidade_queda, fim_de_jogo
    pontos = 0
    vidas = 3
    velocidade_queda = 3
    fim_de_jogo = False
    itens.clear()
    cesta.pos = (WIDTH // 2, HEIGHT - 40)


def mover_cesta():
    if (keyboard.left or keyboard.a) and cesta.left > 0:
        cesta.x -= VELOCIDADE_CESTA
    if (keyboard.right or keyboard.d) and cesta.right < WIDTH:
        cesta.x += VELOCIDADE_CESTA


def pegou_item(item):
    """Decide o que acontece quando um item cai dentro da cesta."""
    global pontos, vidas, velocidade_queda, fim_de_jogo

    if item.tipo == "fruta":
        pontos += 1
        # A cada 10 pontos o jogo fica mais difícil
        if pontos % 10 == 0:
            velocidade_queda += 1
    else:  # é uma bomba
        vidas -= 1
        if vidas == 0:
            fim_de_jogo = True


def update():
    if fim_de_jogo:
        return

    mover_cesta()

    # Percorre uma CÓPIA da lista (itens[:]) porque vamos remover itens dela
    for item in itens[:]:
        item.y += velocidade_queda

        if item.colliderect(cesta):
            pegou_item(item)
            itens.remove(item)
        elif item.top > HEIGHT:
            # Caiu no chão sem ninguém pegar: só some
            itens.remove(item)


def desenhar_vidas():
    for i in range(vidas):
        x = WIDTH - 25 - i * 30
        screen.draw.filled_circle((x, 25), 10, "red")


def draw():
    screen.fill((135, 206, 250))                                    # céu
    screen.draw.filled_rect(Rect(0, HEIGHT - 20, WIDTH, 20), (90, 170, 70))  # grama

    for item in itens:
        item.draw()
    cesta.draw()

    screen.draw.text(f"Pontos: {pontos}", (10, 10), fontsize=34, color="darkblue")
    desenhar_vidas()

    if fim_de_jogo:
        palavra = "fruta" if pontos == 1 else "frutas"
        screen.draw.text("FIM DE JOGO!", center=(WIDTH // 2, HEIGHT // 2 - 40), fontsize=72, color="darkred")
        screen.draw.text(f"Você pegou {pontos} {palavra}", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=40, color="black")
        screen.draw.text("Aperte ESPAÇO para jogar de novo", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=30, color="darkblue")


def on_key_down(key):
    if fim_de_jogo and key == keys.SPACE:
        comecar_jogo()


comecar_jogo()
clock.schedule_interval(criar_item, 0.8)   # uma coisa nova cai a cada 0,8 segundo
