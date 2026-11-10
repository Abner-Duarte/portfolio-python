"""Gera as imagens (images/) e os sons (sounds/) da Chuva de Frutas.

Não faz parte do jogo: só precisa rodar de novo se quiser mudar a arte.
    pip install pillow
    python ferramentas/gerar_arte.py
"""

import math
import random
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

PASTA = Path(__file__).resolve().parent.parent
IMAGENS = PASTA / "images"
SONS = PASTA / "sounds"
LARGURA, ALTURA = 800, 600
E = 4  # desenha 4x maior e reduz, para as bordas ficarem suaves

random.seed(3)


# ---------------------------------------------------------------- ajudantes

def tela(w, h):
    return Image.new("RGBA", (w * E, h * E), (0, 0, 0, 0))


def caixa(x1, y1, x2, y2):
    return [x1 * E, y1 * E, x2 * E, y2 * E]


def reduzir(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def compor(*camadas):
    base = camadas[0].copy()
    for c in camadas[1:]:
        base = Image.alpha_composite(base, c)
    return base


def sombra_projetada(forma, deslocamento=2, borrao=2, opacidade=90):
    alfa = forma.getchannel("A").point(lambda v: v * opacidade // 255)
    sombra = Image.new("RGBA", forma.size, (40, 30, 60, 0))
    sombra.putalpha(alfa)
    sombra = sombra.transform(sombra.size, Image.AFFINE,
                              (1, 0, -deslocamento * E, 0, 1, -deslocamento * E))
    return sombra.filter(ImageFilter.GaussianBlur(borrao * E))


def esfera(img, cx, cy, r, escura, clara, brilho=True):
    """Bolinha com degradê (luz vindo de cima à esquerda) e reflexo."""
    d = ImageDraw.Draw(img)
    passos = 24
    for i in range(passos):
        f = i / (passos - 1)
        rr = r * (1 - f * 0.75)
        ox = -r * 0.28 * f
        oy = -r * 0.32 * f
        cor = tuple(int(a + (b - a) * f) for a, b in zip(escura, clara)) + (255,)
        d.ellipse(caixa(cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr), fill=cor)
    if brilho:
        d.ellipse(caixa(cx - r * 0.55, cy - r * 0.6, cx - r * 0.15, cy - r * 0.3),
                  fill=(255, 255, 255, 170))


def folha(img, x, y, tamanho, angulo, cor=(80, 190, 70)):
    camada = tela(img.width // E, img.height // E)
    d = ImageDraw.Draw(camada)
    a = math.radians(angulo)
    pontos = []
    for i in range(21):
        t = i / 20
        lado = math.sin(t * math.pi) * tamanho * 0.38
        px = t * tamanho
        pontos.append((px, lado))
    for i in range(20, -1, -1):
        t = i / 20
        pontos.append((t * tamanho, -math.sin(t * math.pi) * tamanho * 0.38))
    rot = [((x + px * math.cos(a) - py * math.sin(a)) * E,
            (y + px * math.sin(a) + py * math.cos(a)) * E) for px, py in pontos]
    d.polygon(rot, fill=cor + (255,))
    d.line([(x * E, y * E), ((x + tamanho * 0.9 * math.cos(a)) * E,
                             (y + tamanho * 0.9 * math.sin(a)) * E)],
           fill=(50, 140, 50, 255), width=E)
    return Image.alpha_composite(img, camada)


def salvar_sprite(img, nome, w, h):
    img = compor(sombra_projetada(img), img)
    reduzir(img, w, h).save(IMAGENS / f"{nome}.png")


# ---------------------------------------------------------------- frutas e itens

def maca():
    t = 60
    img = tela(t, t)
    esfera(img, 24, 34, 19, (170, 20, 40), (255, 110, 110))
    esfera(img, 36, 34, 19, (170, 20, 40), (255, 90, 100), brilho=False)
    esfera(img, 30, 35, 19, (190, 25, 45), (255, 120, 120))
    d = ImageDraw.Draw(img)
    d.line([(30 * E, 18 * E), (32 * E, 9 * E)], fill=(110, 70, 40, 255), width=3 * E)
    img = folha(img, 32, 12, 15, -25)
    salvar_sprite(img, "maca", t, t)


def laranja():
    t = 60
    img = tela(t, t)
    esfera(img, 30, 34, 21, (220, 100, 10), (255, 200, 90))
    d = ImageDraw.Draw(img)
    for _ in range(40):
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 18)
        x, y = 30 + r * math.cos(a), 34 + r * math.sin(a)
        d.ellipse(caixa(x - 0.6, y - 0.6, x + 0.6, y + 0.6), fill=(210, 110, 20, 120))
    d.ellipse(caixa(28, 12.5, 32, 15.5), fill=(110, 140, 40, 255))
    img = folha(img, 31, 14, 16, -35)
    salvar_sprite(img, "laranja", t, t)


def uva():
    t = 60
    img = tela(t, t)
    d = ImageDraw.Draw(img)
    d.line([(30 * E, 16 * E), (31 * E, 7 * E)], fill=(110, 80, 40, 255), width=3 * E)
    posicoes = [(22, 22), (30, 21), (38, 22), (18, 30), (26, 30), (34, 30), (42, 30),
                (22, 38), (30, 38), (38, 38), (26, 46), (34, 46), (30, 53)]
    for x, y in posicoes:
        esfera(img, x, y, 6.5, (80, 20, 120), (190, 120, 240))
    img = folha(img, 32, 12, 14, -20, (100, 200, 80))
    salvar_sprite(img, "uva", t, t)


def estrela_dourada():
    t = 60
    c = 30
    img = tela(t, t)
    d = ImageDraw.Draw(img)
    pontos = []
    for i in range(10):
        r = 24 if i % 2 == 0 else 10.5
        a = math.radians(-90 + i * 36)
        pontos.append(((c + r * math.cos(a)) * E, (c + 2 + r * math.sin(a)) * E))
    d.polygon(pontos, fill=(255, 180, 0, 255))
    menor = [((c + (x / E - c) * 0.62) * E, (c + 1 + (y / E - c - 2) * 0.62) * E)
             for x, y in pontos]
    d.polygon(menor, fill=(255, 225, 90, 255))
    d.ellipse(caixa(c - 6, c - 5, c - 1, c - 1), fill=(255, 255, 230, 230))
    brilho = img.getchannel("A").filter(ImageFilter.GaussianBlur(5 * E))
    halo = Image.new("RGBA", img.size, (255, 230, 120, 0))
    halo.putalpha(brilho)
    salvar_sprite(compor(halo, img), "estrela", t, t)


def bomba():
    t = 60
    img = tela(t, t)
    esfera(img, 28, 36, 19, (20, 20, 40), (110, 110, 150))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(caixa(23, 13, 33, 20), radius=2 * E, fill=(70, 70, 90, 255))
    d.rounded_rectangle(caixa(24, 13, 32, 15), radius=1 * E, fill=(130, 130, 150, 255))
    pavio = [(28 + i * 0.9, 13 - 6 * math.sin(i / 10 * 2.6)) for i in range(11)]
    d.line([(x * E, y * E) for x, y in pavio], fill=(200, 170, 120, 255), width=2 * E)
    salvar_sprite(img, "bomba", t, t)


def cesta():
    w, h = 120, 70
    img = tela(w, h)
    d = ImageDraw.Draw(img)
    corpo = [(10, 22), (110, 22), (98, 64), (22, 64)]
    d.polygon([(x * E, y * E) for x, y in corpo], fill=(190, 120, 55, 255))
    # trançado
    for i in range(6):
        y = 27 + i * 7
        esq = 10 + (y - 22) * 12 / 42
        dir_ = 110 - (y - 22) * 12 / 42
        d.line([(esq * E, y * E), (dir_ * E, y * E)], fill=(150, 85, 35, 255), width=2 * E)
    for i in range(12):
        x_topo = 16 + i * 8.2
        x_base = 26 + i * 6.2
        d.line([(x_topo * E, 22 * E), (x_base * E, 64 * E)], fill=(220, 155, 80, 255),
               width=int(1.5 * E))
    # borda de cima
    d.rounded_rectangle(caixa(4, 15, 116, 26), radius=5 * E, fill=(140, 80, 35, 255))
    d.rounded_rectangle(caixa(6, 16, 114, 20), radius=3 * E, fill=(215, 150, 80, 255))
    salvar_sprite(img, "cesta", w, h)


def coracao(nome, cor, contorno):
    t = 34
    img = tela(t, t)
    d = ImageDraw.Draw(img)
    pontos = []
    for i in range(80):
        a = 2 * math.pi * i / 80
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pontos.append(((17 + x * 0.88) * E, (16 + y * 0.88) * E))
    d.polygon(pontos, fill=cor, outline=contorno, width=2 * E)
    if nome == "coracao":
        d.ellipse(caixa(8, 8, 13, 12), fill=(255, 255, 255, 170))
    reduzir(img, t, t).save(IMAGENS / f"{nome}.png")


def nuvem(nome, w, h, bolhas):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x, y, r in bolhas:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 235))
    img = img.filter(ImageFilter.GaussianBlur(2))
    sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for x, y, r in bolhas:
        ds.ellipse([x - r, y - r + 6, x + r, y + r + 6], fill=(200, 215, 240, 160))
    img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(4)), img)
    img.save(IMAGENS / f"{nome}.png")


def fundo():
    img = Image.new("RGBA", (LARGURA, ALTURA))
    d = ImageDraw.Draw(img)
    topo, base = (95, 175, 255), (255, 215, 175)
    for y in range(ALTURA):
        f = min(1, y / (ALTURA * 0.85))
        d.line([(0, y), (LARGURA, y)],
               fill=tuple(int(a + (b - a) * f) for a, b in zip(topo, base)) + (255,))
    # sol com brilho
    sol = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
    ImageDraw.Draw(sol).ellipse([600, 40, 760, 200], fill=(255, 240, 180, 160))
    sol = sol.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sol)
    ImageDraw.Draw(img).ellipse([645, 85, 715, 155], fill=(255, 245, 200, 255))

    def morro(cor, altura_base, amplitude, frequencia, fase):
        camada = Image.new("RGBA", (LARGURA * 2, ALTURA * 2), (0, 0, 0, 0))
        pontos = [(0, ALTURA * 2)]
        for x in range(0, LARGURA * 2 + 1, 8):
            y = altura_base + amplitude * math.sin(x / 2 / LARGURA * frequencia * 2 * math.pi + fase)
            pontos.append((x, y * 2))
        pontos.append((LARGURA * 2, ALTURA * 2))
        ImageDraw.Draw(camada).polygon(pontos, fill=cor)
        return camada.resize((LARGURA, ALTURA), Image.LANCZOS)

    img = Image.alpha_composite(img, morro((150, 200, 160, 255), 470, 30, 1.5, 0.5))
    img = Image.alpha_composite(img, morro((110, 190, 110, 255), 510, 22, 2.2, 2.0))
    img = Image.alpha_composite(img, morro((80, 170, 80, 255), 560, 10, 3.0, 1.0))
    # tufos de grama
    d = ImageDraw.Draw(img)
    for _ in range(140):
        x = random.randint(0, LARGURA)
        y = random.randint(572, ALTURA)
        d.line([(x, y), (x + random.randint(-3, 3), y - random.randint(4, 9))],
               fill=(60, 140, 60, 255), width=2)
    img.convert("RGB").save(IMAGENS / "fundo.png")


def painel(nome, w, h):
    img = Image.new("RGBA", (w * E, h * E), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6 * E, 10 * E, w * E - 1, h * E - 1], radius=26 * E, fill=(60, 40, 90, 60))
    d.rounded_rectangle([0, 0, (w - 6) * E, (h - 10) * E], radius=26 * E,
                        fill=(255, 255, 255, 225), outline=(255, 180, 90, 255), width=4 * E)
    reduzir(img, w, h).save(IMAGENS / f"{nome}.png")


# ---------------------------------------------------------------- sons

TAXA = 22050


def salvar_som(nome, amostras):
    with wave.open(str(SONS / f"{nome}.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(TAXA)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, a)) * 26000))
                               for a in amostras))


def tom(freq_ini, freq_fim, dur, vol=0.4, queda=8.0):
    out = []
    fase = 0.0
    for i in range(int(TAXA * dur)):
        t = i / TAXA
        freq = freq_ini + (freq_fim - freq_ini) * (t / dur)
        fase += 2 * math.pi * freq / TAXA
        out.append(math.sin(fase) * vol * min(1, t / 0.004) * math.exp(-queda * t))
    return out


def juntar(*partes, atraso=0.0):
    total = []
    for n, p in enumerate(partes):
        ini = int(n * atraso * TAXA)
        while len(total) < ini + len(p):
            total.append(0.0)
        for i, a in enumerate(p):
            total[ini + i] += a
    return total


def sons():
    salvar_som("pegar", tom(500, 1100, 0.14, 0.45, 14))
    salvar_som("estrela", juntar(*[tom(f, f, 0.25, 0.25, 9) for f in (784, 988, 1175, 1568)],
                                 atraso=0.06))
    ruido = []
    filtro = 0.0
    for i in range(int(TAXA * 0.6)):
        t = i / TAXA
        filtro += (random.uniform(-1, 1) - filtro) * 0.08
        grave = math.sin(2 * math.pi * (80 - 40 * t) * t)
        ruido.append((filtro * 2.2 + grave * 0.8) * math.exp(-5 * t) * 0.8)
    salvar_som("bomba", ruido)
    salvar_som("nivel", juntar(tom(523, 523, 0.18, 0.3, 8), tom(659, 659, 0.18, 0.3, 8),
                               tom(784, 784, 0.35, 0.3, 6), atraso=0.1))
    salvar_som("fim", juntar(tom(523, 523, 0.25, 0.3, 6), tom(415, 415, 0.25, 0.3, 6),
                             tom(330, 300, 0.5, 0.3, 4), atraso=0.2))


if __name__ == "__main__":
    IMAGENS.mkdir(exist_ok=True)
    SONS.mkdir(exist_ok=True)
    maca()
    laranja()
    uva()
    estrela_dourada()
    bomba()
    cesta()
    coracao("coracao", (240, 50, 80, 255), (170, 20, 50, 255))
    coracao("coracao_vazio", (255, 255, 255, 90), (170, 120, 140, 255))
    nuvem("nuvem1", 180, 100, [(45, 50, 28), (85, 38, 36), (125, 48, 30), (150, 56, 20)])
    nuvem("nuvem2", 130, 80, [(35, 40, 22), (68, 30, 28), (98, 40, 22)])
    fundo()
    painel("painel", 460, 340)
    sons()
    print("Imagens e sons gerados.")
