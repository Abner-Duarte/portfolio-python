# Chuva de Frutas
# Mexa a cesta com as setas (ou A e D) e pegue as frutas que caem do céu.
# Cuidado com as bombas: cada uma tira uma vida. Você tem 3 vidas.
# A estrela dourada vale 5 pontos. A cada 10 pontos, você sobe de nível
# e tudo cai mais rápido!
#
# Para rodar:  pgzrun frutas.py

import math
import random

WIDTH = 800
HEIGHT = 600
TITLE = "Chuva de Frutas"

VELOCIDADE_CESTA = 8
FRUTAS = ["maca", "laranja", "uva"]   # nomes das imagens na pasta images/
CHANCE_DE_BOMBA = 0.2                 # 0.2 = 20% das coisas que caem são bombas
CHANCE_DE_ESTRELA = 0.05              # 5% são estrelas douradas
VIDAS_INICIAIS = 3
CHAO = HEIGHT - 30
FONTE = "fredoka"                     # arquivo fonts/fredoka.ttf

# Cores do suco que espirra de cada fruta
COR_DO_SUCO = {
    "maca": [(230, 40, 60), (255, 120, 120)],
    "laranja": [(255, 150, 20), (255, 210, 90)],
    "uva": [(130, 50, 180), (200, 140, 240)],
    "estrela": [(255, 210, 40), (255, 250, 200)],
    "bomba": [(255, 140, 30), (90, 90, 110), (255, 230, 120)],
}

cesta = Actor("cesta")
itens = []        # tudo o que está caindo agora
gotas = []        # pedacinhos de suco e fumaça (cada um é um dicionário)
textos = []       # textos que sobem e somem ("+1", "NÍVEL 2!")

# Nuvens do fundo: [nome da imagem, x, y, velocidade]
nuvens = [["nuvem1", 80, 50, 0.25], ["nuvem2", 420, 120, 0.4], ["nuvem1", 700, 190, 0.15]]

estado = "inicio"      # "inicio", "jogando" ou "fim"
pontos = 0
vidas = VIDAS_INICIAIS
nivel = 1
velocidade_queda = 3
recorde = 0
tremor = 0             # quanto a tela treme (depois de uma bomba)
quadro = 0             # conta os quadros desenhados (para animações)


# ------------------------------------------------------------------ itens

def criar_item():
    """Cria uma fruta, uma bomba ou uma estrela no alto da tela."""
    if estado != "jogando":
        return

    sorteio = random.random()
    if sorteio < CHANCE_DE_ESTRELA:
        item = Actor("estrela")
        item.tipo = "estrela"
    elif sorteio < CHANCE_DE_ESTRELA + CHANCE_DE_BOMBA:
        item = Actor("bomba")
        item.tipo = "bomba"
    else:
        fruta = random.choice(FRUTAS)
        item = Actor(fruta)
        item.tipo = fruta

    item.x = random.randint(40, WIDTH - 40)
    item.y = -30                           # começa um pouquinho acima da tela
    item.giro = random.uniform(-3, 3)      # quanto gira por quadro
    item.balanco = random.uniform(0, 6)    # para balançar de um lado pro outro
    itens.append(item)


def espirrar(x, y, cores, quantidade=14):
    """Solta pedacinhos coloridos para todos os lados."""
    for _ in range(quantidade):
        angulo = random.uniform(0, 2 * math.pi)
        forca = random.uniform(2, 6)
        gotas.append({
            "x": x, "y": y,
            "vx": math.cos(angulo) * forca,
            "vy": math.sin(angulo) * forca - 2,
            "raio": random.uniform(3, 6),
            "cor": random.choice(cores),
        })


def mostrar_texto(texto, x, y, cor, tamanho=40):
    textos.append({"texto": texto, "x": x, "y": y, "cor": cor,
                   "tamanho": tamanho, "vida": 1.0})


# ------------------------------------------------------------------ jogo

def comecar_jogo():
    """Zera tudo para uma partida nova."""
    global estado, pontos, vidas, nivel, velocidade_queda
    estado = "jogando"
    pontos = 0
    vidas = VIDAS_INICIAIS
    nivel = 1
    velocidade_queda = 3
    itens.clear()
    gotas.clear()
    textos.clear()
    cesta.pos = (WIDTH // 2, CHAO - 30)
    cesta.angle = 0


def mover_cesta():
    andou = 0
    if (keyboard.left or keyboard.a) and cesta.left > 0:
        cesta.x -= VELOCIDADE_CESTA
        andou = -1
    if (keyboard.right or keyboard.d) and cesta.right < WIDTH:
        cesta.x += VELOCIDADE_CESTA
        andou = 1
    # A cesta inclina um pouquinho para o lado que está indo
    cesta.angle = -andou * 6


def pegou_item(item):
    """Decide o que acontece quando um item cai dentro da cesta."""
    global pontos, vidas, nivel, velocidade_queda, tremor

    if item.tipo == "bomba":
        vidas -= 1
        tremor = 14
        espirrar(item.x, item.y, COR_DO_SUCO["bomba"], 30)
        mostrar_texto("-1", item.x, item.y - 30, (220, 40, 60))
        tocar("bomba")
        if vidas == 0:
            terminar_jogo()
        return

    if item.tipo == "estrela":
        ganho = 5
        tocar("estrela")
    else:
        ganho = 1
        tocar("pegar")
    pontos_antes = pontos
    pontos += ganho
    espirrar(item.x, item.y, COR_DO_SUCO[item.tipo])
    mostrar_texto(f"+{ganho}", item.x, item.y - 30, (255, 255, 255))

    # A cada 10 pontos o jogo fica mais difícil
    if pontos // 10 > pontos_antes // 10:
        nivel += 1
        velocidade_queda += 1
        mostrar_texto(f"NÍVEL {nivel}!", WIDTH // 2, HEIGHT // 2 - 60, (255, 200, 60), 64)
        tocar("nivel")


def terminar_jogo():
    global estado, recorde
    estado = "fim"
    # Tudo que ainda estava caindo "estoura" e some
    for item in itens:
        espirrar(item.x, item.y, COR_DO_SUCO[item.tipo], 5)
    itens.clear()
    if pontos > recorde:
        recorde = pontos
    tocar("fim")


def tocar(nome):
    getattr(sounds, nome).play()


def update():
    global tremor, quadro
    quadro += 1

    # As nuvens andam devagar e voltam pela esquerda
    for nuvem in nuvens:
        nuvem[1] += nuvem[3]
        if nuvem[1] > WIDTH + 20:
            nuvem[1] = -200

    # Pedacinhos de suco: andam, caem pela gravidade e encolhem
    for gota in gotas[:]:
        gota["x"] += gota["vx"]
        gota["y"] += gota["vy"]
        gota["vy"] += 0.3
        gota["raio"] -= 0.12
        if gota["raio"] <= 0:
            gotas.remove(gota)

    for texto in textos[:]:
        texto["y"] -= 1
        texto["vida"] -= 0.02
        if texto["vida"] <= 0:
            textos.remove(texto)

    if tremor > 0:
        tremor -= 1

    if estado != "jogando":
        return

    mover_cesta()

    # Percorre uma CÓPIA da lista (itens[:]) porque vamos remover itens dela
    for item in itens[:]:
        item.y += velocidade_queda
        item.x += math.sin(quadro / 15 + item.balanco) * 0.6
        item.angle += item.giro

        # Só conta se cair pela boca da cesta (parte de cima)
        if (abs(item.x - cesta.x) < 50 and cesta.top < item.y < cesta.top + 30):
            pegou_item(item)
            itens.remove(item)
        elif item.y > CHAO:
            # Caiu no chão sem ninguém pegar
            if item.tipo != "bomba":
                espirrar(item.x, CHAO, COR_DO_SUCO[item.tipo], 6)
            itens.remove(item)


# ------------------------------------------------------------------ desenho

def escrever(texto, tamanho, cor, **posicao):
    screen.draw.text(texto, fontname=FONTE, fontsize=tamanho, color=cor,
                     owidth=1.5, ocolor=(70, 40, 90), **posicao)


def desenhar_vidas():
    for i in range(VIDAS_INICIAIS):
        imagem = "coracao" if i < vidas else "coracao_vazio"
        screen.blit(imagem, (WIDTH - 50 - i * 40, 18))


def desenhar_faisca(item, dx, dy):
    """Faísca piscando na ponta do pavio da bomba."""
    if quadro % 6 < 3:
        cor = (255, 230, 80)
    else:
        cor = (255, 120, 30)
    angulo = math.radians(-item.angle)
    # ponta do pavio fica acima e à direita do centro da bomba
    px, py = 9, -25
    x = item.x + px * math.cos(angulo) - py * math.sin(angulo) + dx
    y = item.y + px * math.sin(angulo) + py * math.cos(angulo) + dy
    screen.draw.filled_circle((x, y), random.randint(3, 5), cor)


def draw():
    # Tremor: tudo que é do jogo é desenhado um pouco deslocado
    dx = random.randint(-tremor, tremor) if tremor else 0
    dy = random.randint(-tremor, tremor) if tremor else 0

    screen.blit("fundo", (0, 0))
    for nome, x, y, _ in nuvens:
        screen.blit(nome, (x, y))

    for item in itens:
        item.x += dx
        item.y += dy
        item.draw()
        item.x -= dx
        item.y -= dy
        if item.tipo == "bomba":
            desenhar_faisca(item, dx, dy)

    if estado == "jogando":
        cesta.x += dx
        cesta.draw()
        cesta.x -= dx

    for gota in gotas:
        screen.draw.filled_circle((gota["x"] + dx, gota["y"] + dy), gota["raio"], gota["cor"])

    for texto in textos:
        screen.draw.text(texto["texto"], center=(texto["x"], texto["y"]), fontname=FONTE,
                         fontsize=texto["tamanho"], color=texto["cor"],
                         owidth=1.5, ocolor=(70, 40, 90), alpha=max(0, texto["vida"]))

    if estado == "jogando":
        escrever(f"Pontos: {pontos}", 40, (255, 255, 255), topleft=(20, 14))
        escrever(f"Nível {nivel}", 26, (255, 220, 120), topleft=(22, 60))
        desenhar_vidas()
    elif estado == "inicio":
        desenhar_inicio()
    else:
        desenhar_fim()


def desenhar_inicio():
    balanco = math.sin(quadro / 20) * 6
    escrever("Chuva de Frutas", 86, (255, 210, 80), center=(WIDTH // 2, 170 + balanco))
    screen.blit("maca", (WIDTH // 2 - 160, 250))
    screen.blit("laranja", (WIDTH // 2 - 60, 250))
    screen.blit("uva", (WIDTH // 2 + 40, 250))
    screen.blit("estrela", (WIDTH // 2 + 110, 250))
    escrever("Pegue as frutas e fuja das bombas!", 30, (255, 255, 255), center=(WIDTH // 2, 345))
    if quadro // 30 % 2 == 0:
        escrever("Aperte ESPAÇO para começar", 34, (255, 230, 140), center=(WIDTH // 2, 420))
    escrever("Setas ou A/D para mexer a cesta", 22, (255, 255, 255), center=(WIDTH // 2, 470))


def desenhar_fim():
    screen.blit("painel", (WIDTH // 2 - 230, 120))
    centro = WIDTH // 2 - 3
    escrever("Fim de jogo!", 60, (240, 90, 80), center=(centro, 180))
    palavra = "ponto" if pontos == 1 else "pontos"
    screen.draw.text(f"{pontos} {palavra}", center=(centro, 255), fontname=FONTE,
                     fontsize=56, color=(90, 60, 130))
    screen.draw.text(f"Recorde: {recorde}   |   Nível {nivel}", center=(centro, 310),
                     fontname=FONTE, fontsize=26, color=(150, 120, 170))
    screen.blit("maca", (centro - 105, 335))
    screen.blit("laranja", (centro - 30, 335))
    screen.blit("uva", (centro + 45, 335))
    screen.draw.text("Aperte ESPAÇO para jogar de novo", center=(centro, 412),
                     fontname=FONTE, fontsize=23, color=(240, 140, 50))


def on_key_down(key):
    if estado != "jogando" and key == keys.SPACE:
        comecar_jogo()


clock.schedule_interval(criar_item, 0.7)   # uma coisa nova cai a cada 0,7 segundo
