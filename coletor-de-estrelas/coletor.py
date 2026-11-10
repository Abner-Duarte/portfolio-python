# Coletor de Estrelas
# Pilote a nave com as setas (ou WASD), pegue o máximo de estrelas antes do
# tempo acabar e fuja dos meteoros. Estrelas seguidas formam COMBO e valem
# mais pontos; o relógio azul devolve 3 segundos.
#
# Para rodar:  pgzrun coletor.py

import math
import random

WIDTH = 800
HEIGHT = 600
TITLE = "Coletor de Estrelas"

TEMPO_INICIAL = 30
ACELERACAO = 0.9      # quanto a nave ganha de velocidade por quadro
ATRITO = 0.86         # quanto da velocidade sobra no quadro seguinte (inércia)
TEMPO_COMBO = 2.5     # segundos para pegar a próxima estrela e manter o combo
COMBO_MAXIMO = 5
TOPO_JOGO = 70        # abaixo do placar
COR_FUNDO = (14, 8, 34)
ARQUIVO_RECORDE = "recorde.txt"


# ------------------------------------------------------------------ ajudantes

def misturar(cor1, cor2, f):
    """Mistura duas cores: f=0 devolve cor1, f=1 devolve cor2."""
    return tuple(int(a + (b - a) * f) for a, b in zip(cor1, cor2))


def distancia(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def tocar(nome):
    if som_ligado:
        getattr(sounds, nome).play()


def ler_recorde():
    try:
        with open(ARQUIVO_RECORDE) as f:
            return int(f.read())
    except (OSError, ValueError):
        return 0


def salvar_recorde(valor):
    try:
        with open(ARQUIVO_RECORDE, "w") as f:
            f.write(str(valor))
    except OSError:
        pass


# ------------------------------------------------------------------ efeitos

class Particula:
    """Pontinho que voa, encolhe e some (rastro do motor, explosões)."""

    def __init__(self, x, y, vx, vy, vida, cor, raio, gravidade=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.vida = self.restante = vida
        self.cor = cor
        self.raio = raio
        self.gravidade = gravidade

    def atualizar(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravidade * dt * 60
        self.vx *= 0.97
        self.vy *= 0.97
        self.restante -= dt

    def viva(self):
        return self.restante > 0

    def desenhar(self, ox, oy):
        f = self.restante / self.vida
        raio = max(1, self.raio * f)
        cor = misturar(self.cor, COR_FUNDO, 1 - f)
        screen.draw.filled_circle((self.x + ox, self.y + oy), raio, cor)


class Onda:
    """Anel que cresce e desbota (quando pega uma estrela)."""

    def __init__(self, x, y, cor, raio_final=60, vida=0.45):
        self.x, self.y = x, y
        self.cor = cor
        self.raio_final = raio_final
        self.vida = self.restante = vida

    def atualizar(self, dt):
        self.restante -= dt

    def viva(self):
        return self.restante > 0

    def desenhar(self, ox, oy):
        f = 1 - self.restante / self.vida
        raio = 8 + (self.raio_final - 8) * f
        cor = misturar(self.cor, COR_FUNDO, f)
        screen.draw.circle((self.x + ox, self.y + oy), raio, cor)
        screen.draw.circle((self.x + ox, self.y + oy), raio - 1, cor)


class TextoFlutuante:
    """Texto que sobe e desaparece ("+3", "-3s", "COMBO x2")."""

    def __init__(self, texto, x, y, cor, tamanho=34):
        self.texto = texto
        self.x, self.y = x, y
        self.cor = cor
        self.tamanho = tamanho
        self.vida = self.restante = 0.9

    def atualizar(self, dt):
        self.y -= 50 * dt
        self.restante -= dt

    def viva(self):
        return self.restante > 0

    def desenhar(self, ox, oy):
        screen.draw.text(self.texto, center=(self.x + ox, self.y + oy),
                         fontname="orbitron", fontsize=self.tamanho, color=self.cor,
                         owidth=1.2, ocolor=(20, 10, 40),
                         alpha=min(1, self.restante / self.vida * 1.6))


def explodir(x, y, cores, quantidade=24, forca=5):
    for _ in range(quantidade):
        angulo = random.uniform(0, 2 * math.pi)
        v = random.uniform(1, forca)
        efeitos.append(Particula(x, y, math.cos(angulo) * v, math.sin(angulo) * v,
                                 random.uniform(0.4, 0.8), random.choice(cores),
                                 random.uniform(2, 4.5)))


# ------------------------------------------------------------------ fundo

# Três camadas de estrelinhas: as do fundo andam devagar, as da frente rápido.
# Isso dá a sensação de profundidade (efeito "parallax").
camadas = []
for velocidade, quantidade, raio in [(0.3, 70, 1), (0.8, 35, 1.5), (1.8, 14, 2)]:
    for _ in range(quantidade):
        camadas.append([random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                        velocidade, raio, random.uniform(0, 6.28)])


def mover_fundo(dt):
    for ponto in camadas:
        ponto[0] -= ponto[2] * dt * 60
        if ponto[0] < 0:
            ponto[0] = WIDTH
            ponto[1] = random.uniform(0, HEIGHT)


def desenhar_fundo():
    screen.blit("fundo", (0, 0))
    for x, y, velocidade, raio, fase in camadas:
        piscada = 0.65 + 0.35 * math.sin(relogio_global * 3 + fase)
        cor = misturar(COR_FUNDO, (230, 230, 255), piscada * min(1, 0.35 + velocidade / 2))
        screen.draw.filled_circle((x, y), raio, cor)


# ------------------------------------------------------------------ estado

nave = Actor("nave")
estrela = Actor("estrela")
bonus_relogio = Actor("relogio")
meteoros = []
efeitos = []          # partículas, ondas e textos

estado = "menu"       # "menu", "jogando" ou "fim"
som_ligado = True
recorde = ler_recorde()
novo_recorde = False
relogio_global = 0.0  # segundos desde que o jogo abriu (para animações)

pontos = 0
tempo = TEMPO_INICIAL
tempo_de_jogo = 0.0
combo = 0
maior_combo = 0
tempo_restante_combo = 0.0
protegida = 0.0       # segundos de proteção depois de uma batida
tremor = 0.0          # força do tremor da tela
flash_dano = 0.0
vx = vy = 0.0         # velocidade da nave
estrela_base_y = 0
relogio_ativo = False
relogio_vida = 0.0
proximo_relogio = 0.0

# Botões: (texto, ação). O retângulo de cada um é calculado na hora.
BOTOES_MENU = [("JOGAR", "jogar"), ("SOM", "som"), ("SAIR", "sair")]
BOTOES_FIM = [("JOGAR DE NOVO", "jogar"), ("MENU", "menu")]
botao_em_cima = None


def botoes_da_tela():
    lista = BOTOES_MENU if estado == "menu" else BOTOES_FIM if estado == "fim" else []
    inicio_y = 330 if estado == "menu" else 410
    resultado = []
    for i, (texto, acao) in enumerate(lista):
        if acao == "som":
            texto = "SOM: LIGADO" if som_ligado else "SOM: DESLIGADO"
        retangulo = Rect(0, 0, 260, 54)
        retangulo.center = (WIDTH // 2, inicio_y + i * 68)
        resultado.append((texto, acao, retangulo))
    return resultado


# ------------------------------------------------------------------ jogo

def sortear_lugar_da_estrela():
    """Coloca a estrela num lugar novo, longe da nave."""
    global estrela_base_y
    for _ in range(20):
        estrela.x = random.randint(60, WIDTH - 60)
        estrela_base_y = random.randint(TOPO_JOGO + 40, HEIGHT - 50)
        estrela.y = estrela_base_y
        if distancia(estrela, nave) > 180:
            break
    efeitos.append(Onda(estrela.x, estrela.y, (255, 220, 120), 40, 0.35))


def criar_meteoro():
    grande = random.random() < 0.5
    meteoro = Actor("meteoro_grande" if grande else "meteoro_pequeno")
    meteoro.raio = 24 if grande else 16
    lancar_meteoro(meteoro)
    meteoros.append(meteoro)


def lancar_meteoro(meteoro):
    """Coloca o meteoro fora da tela, à direita, com altura e velocidade sorteadas.
    Quanto mais tempo de jogo, mais rápido eles vêm."""
    dificuldade = 1 + tempo_de_jogo / 35
    meteoro.x = WIDTH + random.randint(60, 360)
    meteoro.y = random.randint(TOPO_JOGO + 30, HEIGHT - 30)
    meteoro.velocidade = random.uniform(2.8, 5.2) * dificuldade
    meteoro.subida = random.uniform(-0.7, 0.7)
    meteoro.giro = random.uniform(-3, 3)


def comecar_jogo():
    global estado, pontos, tempo, tempo_de_jogo, combo, maior_combo
    global tempo_restante_combo, protegida, tremor, flash_dano, vx, vy
    global relogio_ativo, proximo_relogio, novo_recorde
    estado = "jogando"
    pontos = 0
    tempo = TEMPO_INICIAL
    tempo_de_jogo = 0.0
    combo = maior_combo = 0
    tempo_restante_combo = 0.0
    protegida = tremor = flash_dano = 0.0
    vx = vy = 0.0
    novo_recorde = False
    relogio_ativo = False
    proximo_relogio = random.uniform(7, 10)
    nave.pos = (140, HEIGHT // 2)
    nave.angle = 0
    meteoros.clear()
    efeitos.clear()
    for _ in range(3):
        criar_meteoro()
    sortear_lugar_da_estrela()


def terminar_jogo():
    global estado, recorde, novo_recorde
    estado = "fim"
    explodir(nave.x, nave.y, [(255, 160, 60), (255, 230, 150), (120, 200, 255)], 40, 6)
    if pontos > recorde:
        recorde = pontos
        novo_recorde = True
        salvar_recorde(recorde)
        tocar("recorde")
    else:
        tocar("fim")


def mover_nave():
    """Setas aceleram a nave; sem tecla, ela vai parando aos poucos."""
    global vx, vy
    if keyboard.left or keyboard.a:
        vx -= ACELERACAO
    if keyboard.right or keyboard.d:
        vx += ACELERACAO
    if keyboard.up or keyboard.w:
        vy -= ACELERACAO
    if keyboard.down or keyboard.s:
        vy += ACELERACAO
    vx *= ATRITO
    vy *= ATRITO
    nave.x = min(max(nave.x + vx, 40), WIDTH - 40)
    nave.y = min(max(nave.y + vy, TOPO_JOGO + 20), HEIGHT - 25)
    # Inclina o bico para onde a nave está indo
    nave.angle = max(-25, min(25, -vy * 3.5))


def soltar_fumaca_do_motor():
    traseira_x = nave.x - 40 * math.cos(math.radians(nave.angle))
    traseira_y = nave.y + 40 * math.sin(math.radians(nave.angle))
    for _ in range(2):
        cor = random.choice([(255, 120, 220), (120, 220, 255), (255, 200, 120)])
        efeitos.append(Particula(traseira_x, traseira_y + random.uniform(-4, 4),
                                 -random.uniform(2, 4) + vx * 0.3, random.uniform(-0.4, 0.4),
                                 random.uniform(0.25, 0.45), cor, random.uniform(2, 4)))


def pegar_estrela():
    global pontos, combo, maior_combo, tempo_restante_combo
    if tempo_restante_combo > 0:
        combo = min(COMBO_MAXIMO, combo + 1)
    else:
        combo = 1
    maior_combo = max(maior_combo, combo)
    tempo_restante_combo = TEMPO_COMBO
    pontos += combo
    explodir(estrela.x, estrela.y, [(255, 220, 90), (255, 255, 220), (255, 160, 40)], 26)
    efeitos.append(Onda(estrela.x, estrela.y, (255, 220, 120), 70))
    efeitos.append(TextoFlutuante(f"+{combo}", estrela.x, estrela.y - 20, (255, 225, 110)))
    if combo > 1:
        efeitos.append(TextoFlutuante(f"COMBO x{combo}", estrela.x, estrela.y - 52,
                                      (255, 120, 220), 22))
    tocar("pegar")
    sortear_lugar_da_estrela()


def bater_em_meteoro(meteoro):
    global tempo, protegida, tremor, flash_dano, combo, tempo_restante_combo
    tempo = max(0, tempo - 3)
    protegida = 1.5
    tremor = 12
    flash_dano = 0.45
    combo = 0
    tempo_restante_combo = 0
    explodir(meteoro.x, meteoro.y, [(255, 120, 60), (180, 140, 170), (255, 210, 120)], 30, 6)
    efeitos.append(TextoFlutuante("-3s", nave.x, nave.y - 40, (255, 90, 110)))
    tocar("batida")
    lancar_meteoro(meteoro)


def atualizar_relogio_bonus(dt):
    """De tempos em tempos aparece um relógio que devolve 3 segundos."""
    global relogio_ativo, relogio_vida, proximo_relogio, tempo
    if not relogio_ativo:
        proximo_relogio -= dt
        if proximo_relogio <= 0:
            relogio_ativo = True
            relogio_vida = 5.0
            bonus_relogio.pos = (random.randint(80, WIDTH - 80),
                                 random.randint(TOPO_JOGO + 50, HEIGHT - 60))
            efeitos.append(Onda(bonus_relogio.x, bonus_relogio.y, (90, 240, 255), 50))
        return
    relogio_vida -= dt
    if distancia(nave, bonus_relogio) < 38:
        tempo += 3
        explodir(bonus_relogio.x, bonus_relogio.y, [(90, 240, 255), (220, 255, 255)], 22)
        efeitos.append(Onda(bonus_relogio.x, bonus_relogio.y, (90, 240, 255), 70))
        efeitos.append(TextoFlutuante("+3s", bonus_relogio.x, bonus_relogio.y - 30,
                                      (120, 240, 255)))
        tocar("relogio")
        relogio_vida = 0
    if relogio_vida <= 0:
        relogio_ativo = False
        proximo_relogio = random.uniform(8, 12)


def update(dt):
    """Roda umas 60 vezes por segundo: aqui fica a lógica do jogo."""
    global relogio_global, tempo, tempo_de_jogo, protegida, tremor, flash_dano
    global tempo_restante_combo, combo

    relogio_global += dt
    mover_fundo(dt)
    for efeito in efeitos:
        efeito.atualizar(dt)
    efeitos[:] = [e for e in efeitos if e.viva()]
    tremor = max(0, tremor - 40 * dt)
    flash_dano = max(0, flash_dano - dt)

    if estado == "menu":
        # A nave fica flutuando na tela de início
        nave.pos = (WIDTH // 2, 235 + math.sin(relogio_global * 2) * 10)
        nave.angle = math.sin(relogio_global * 2 + 1) * 6
        soltar_fumaca_do_motor()
        return
    if estado != "jogando":
        return

    tempo_de_jogo += dt
    tempo -= dt
    protegida = max(0, protegida - dt)
    tempo_restante_combo = max(0, tempo_restante_combo - dt)
    if tempo_restante_combo == 0:
        combo = 0

    mover_nave()
    soltar_fumaca_do_motor()

    # Estrela gira e flutua de leve
    estrela.angle = relogio_global * 90
    estrela.y = estrela_base_y + math.sin(relogio_global * 3) * 6
    if distancia(nave, estrela) < 38:
        pegar_estrela()

    # Mais meteoros com o passar do tempo (máximo de 7)
    if len(meteoros) < min(7, 3 + int(tempo_de_jogo // 8)):
        criar_meteoro()

    for meteoro in meteoros:
        meteoro.x -= meteoro.velocidade * dt * 60
        meteoro.y += meteoro.subida * dt * 60
        meteoro.angle += meteoro.giro
        if meteoro.y < TOPO_JOGO + 20 or meteoro.y > HEIGHT - 20:
            meteoro.subida = -meteoro.subida
        if meteoro.x < -60:
            lancar_meteoro(meteoro)
        if protegida == 0 and distancia(meteoro, nave) < meteoro.raio + 16:
            bater_em_meteoro(meteoro)

    atualizar_relogio_bonus(dt)

    if tempo <= 0:
        tempo = 0
        terminar_jogo()


# ------------------------------------------------------------------ desenho

def desenhar_ator(ator, ox, oy):
    """Desenha um ator deslocado (para o tremor da tela)."""
    ator.x += ox
    ator.y += oy
    ator.draw()
    ator.x -= ox
    ator.y -= oy


def texto(conteudo, tamanho, cor, **posicao):
    screen.draw.text(conteudo, fontname="orbitron", fontsize=tamanho, color=cor,
                     shadow=(0, 2), scolor=(8, 4, 20), **posicao)


def desenhar_placar():
    texto("PONTOS", 16, (170, 160, 230), topleft=(24, 14))
    texto(str(pontos), 38, (255, 225, 110), topleft=(24, 30))
    texto("RECORDE", 16, (170, 160, 230), topright=(WIDTH - 24, 14))
    texto(str(max(recorde, pontos)), 38, (255, 255, 255), topright=(WIDTH - 24, 30))

    # Barra de tempo no meio: verde → amarelo → vermelho
    largura = 320
    x = WIDTH // 2 - largura // 2
    y = 30
    fracao = max(0, min(1, tempo / TEMPO_INICIAL))
    if fracao > 0.5:
        cor = misturar((255, 220, 80), (80, 230, 160), (fracao - 0.5) * 2)
    else:
        cor = misturar((255, 70, 90), (255, 220, 80), fracao * 2)
    if tempo <= 5 and int(relogio_global * 6) % 2 == 0:
        cor = (255, 255, 255)
    screen.draw.filled_rect(Rect(x - 3, y - 3, largura + 6, 22), (40, 28, 80))
    screen.draw.filled_rect(Rect(x, y, largura, 16), (22, 14, 48))
    screen.draw.filled_rect(Rect(x, y, int(largura * fracao), 16), cor)
    screen.draw.filled_rect(Rect(x, y, int(largura * fracao), 4), misturar(cor, (255, 255, 255), 0.5))
    texto(f"{math.ceil(tempo)}s", 18, (235, 230, 255), midtop=(WIDTH // 2, 52))

    # Combo: texto e barrinha que esvazia
    if combo > 1:
        texto(f"COMBO x{combo}", 20, (255, 120, 220), midtop=(WIDTH // 2, 76))
        f = tempo_restante_combo / TEMPO_COMBO
        screen.draw.filled_rect(Rect(WIDTH // 2 - 50, 100, int(100 * f), 3), (255, 120, 220))


def desenhar_botoes():
    for conteudo, acao, retangulo in botoes_da_tela():
        ativo = acao == botao_em_cima
        screen.blit("botao_ativo" if ativo else "botao", retangulo.topleft)
        cor = (255, 225, 110) if ativo else (225, 220, 255)
        texto(conteudo, 22, cor, center=retangulo.center)


def desenhar_menu():
    titulo_y = 120 + math.sin(relogio_global * 1.5) * 4
    screen.draw.text("COLETOR DE", center=(WIDTH // 2, titulo_y - 30), fontname="orbitron",
                     fontsize=34, color=(200, 190, 255), shadow=(0, 3), scolor=(8, 4, 20))
    screen.draw.text("ESTRELAS", center=(WIDTH // 2, titulo_y + 20), fontname="orbitron",
                     fontsize=78, color=(255, 240, 150), gcolor=(255, 140, 60),
                     shadow=(0, 3), scolor=(70, 20, 60))
    nave.draw()
    desenhar_botoes()
    texto(f"RECORDE: {recorde}", 18, (170, 160, 230), center=(WIDTH // 2, 540))
    texto("SETAS/WASD movem   |   ENTER joga   |   M som   |   ESC sai", 14,
          (130, 120, 190), center=(WIDTH // 2, 570))


def desenhar_fim():
    screen.blit("painel", (WIDTH // 2 - 220, 100))
    texto("FIM DE JOGO", 40, (255, 150, 90), center=(WIDTH // 2, 150))
    palavra = "PONTO" if pontos == 1 else "PONTOS"
    texto(str(pontos), 76, (255, 225, 110), center=(WIDTH // 2, 225))
    texto(palavra, 18, (200, 190, 255), center=(WIDTH // 2, 272))
    if novo_recorde:
        pulso = 0.5 + 0.5 * math.sin(relogio_global * 8)
        texto("NOVO RECORDE!", 24, misturar((255, 120, 220), (255, 240, 150), pulso),
              center=(WIDTH // 2, 310))
    texto(f"RECORDE: {recorde}   |   MAIOR COMBO: x{maior_combo}", 16,
          (170, 160, 230), center=(WIDTH // 2, 345))
    desenhar_botoes()


def draw():
    """Desenha tudo na tela, também umas 60 vezes por segundo."""
    ox = random.uniform(-tremor, tremor) if tremor else 0
    oy = random.uniform(-tremor, tremor) if tremor else 0

    desenhar_fundo()

    if estado == "jogando":
        # Anel pulsante em volta da estrela
        pulso = math.sin(relogio_global * 5)
        screen.draw.circle((estrela.x + ox, estrela.y + oy), 30 + pulso * 4,
                           misturar((255, 200, 80), COR_FUNDO, 0.55 + pulso * 0.2))
        desenhar_ator(estrela, ox, oy)
        if relogio_ativo and (relogio_vida > 1.5 or int(relogio_global * 10) % 2 == 0):
            bonus_relogio.y += math.sin(relogio_global * 4) * 0.3
            desenhar_ator(bonus_relogio, ox, oy)

    for efeito in efeitos:
        efeito.desenhar(ox, oy)

    if estado == "jogando":
        for meteoro in meteoros:
            desenhar_ator(meteoro, ox, oy)
        # Protegida, a nave pisca
        if protegida == 0 or int(relogio_global * 14) % 2 == 0:
            desenhar_ator(nave, ox, oy)
        desenhar_placar()
    elif estado == "menu":
        desenhar_menu()
    else:
        desenhar_fim()

    # Borda vermelha que some aos poucos depois de uma batida
    if flash_dano > 0.3:
        screen.blit("dano_forte", (0, 0))
    elif flash_dano > 0.15:
        screen.blit("dano_medio", (0, 0))
    elif flash_dano > 0:
        screen.blit("dano_fraco", (0, 0))


# ------------------------------------------------------------------ controles

def executar(acao):
    global estado, som_ligado
    tocar("clique")
    if acao == "jogar":
        comecar_jogo()
    elif acao == "menu":
        estado = "menu"
        efeitos.clear()
    elif acao == "som":
        som_ligado = not som_ligado
        tocar("clique")
    elif acao == "sair":
        exit()


def on_mouse_move(pos):
    global botao_em_cima
    botao_em_cima = None
    for _, acao, retangulo in botoes_da_tela():
        if retangulo.collidepoint(pos):
            botao_em_cima = acao


def on_mouse_down(pos):
    for _, acao, retangulo in botoes_da_tela():
        if retangulo.collidepoint(pos):
            executar(acao)
            return


def on_key_down(key):
    if key == keys.M:
        executar("som")
    elif key == keys.ESCAPE:
        if estado == "menu":
            exit()
        executar("menu")
    elif key in (keys.RETURN, keys.SPACE) and estado != "jogando":
        executar("jogar")
