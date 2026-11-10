"""Gera as imagens (images/) e os sons (sounds/) do Coletor de Estrelas.

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
ESCALA = 4  # desenha 4x maior e reduz, para as bordas ficarem suaves

random.seed(7)


# ---------------------------------------------------------------- imagens

def tela(w, h):
    return Image.new("RGBA", (w * ESCALA, h * ESCALA), (0, 0, 0, 0))


def reduzir(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def brilho(forma, cor, raio, forca=1.0):
    """Cria um halo borrado a partir do canal alfa de uma forma."""
    alfa = forma.getchannel("A").filter(ImageFilter.GaussianBlur(raio * ESCALA))
    if forca != 1.0:
        alfa = alfa.point(lambda v: min(255, int(v * forca)))
    halo = Image.new("RGBA", forma.size, cor + (0,))
    halo.putalpha(alfa)
    return halo


def compor(*camadas):
    base = camadas[0].copy()
    for c in camadas[1:]:
        base = Image.alpha_composite(base, c)
    return base


def pts(lista, dx, dy):
    return [((x + dx) * ESCALA, (y + dy) * ESCALA) for x, y in lista]


def nave():
    w, h = 96, 64
    dx, dy = 16, 12  # margem para o brilho
    corpo = tela(w, h)
    d = ImageDraw.Draw(corpo)
    # asas
    d.polygon(pts([(14, 2), (36, 20), (22, 20)], dx, dy), fill=(70, 80, 160, 255))
    d.polygon(pts([(14, 38), (36, 20), (22, 20)], dx, dy), fill=(70, 80, 160, 255))
    d.polygon(pts([(14, 2), (30, 16), (36, 20), (22, 20)], dx, dy), fill=(110, 120, 220, 255))
    # fuselagem
    d.polygon(pts([(4, 13), (40, 16), (64, 20), (40, 24), (4, 27), (10, 20)], dx, dy),
              fill=(225, 232, 255, 255))
    d.polygon(pts([(4, 20), (64, 20), (40, 24), (4, 27), (10, 20)], dx, dy),
              fill=(170, 180, 225, 255))
    # cabine
    d.ellipse(pts([(30, 16.5), (48, 23.5)], dx, dy)[0] + pts([(48, 23.5)], dx, dy)[0],
              fill=(60, 230, 255, 255))
    d.ellipse(pts([(33, 17.5), (41, 19.5)], dx, dy)[0] + pts([(41, 19.5)], dx, dy)[0],
              fill=(210, 255, 255, 255))
    # faixas neon
    d.line(pts([(12, 16), (36, 18)], dx, dy), fill=(255, 70, 200, 255), width=ESCALA)
    d.line(pts([(12, 24), (36, 22)], dx, dy), fill=(255, 70, 200, 255), width=ESCALA)
    # motor
    d.rectangle(pts([(1, 15), (6, 25)], dx, dy)[0] + pts([(6, 25)], dx, dy)[0],
                fill=(60, 60, 90, 255))
    img = compor(brilho(corpo, (80, 200, 255), 6, 0.9), corpo)
    reduzir(img, w, h).save(IMAGENS / "nave.png")


def estrela_forma(cx, cy, r_ext, r_int, pontas=5, giro=-90):
    lista = []
    for i in range(pontas * 2):
        r = r_ext if i % 2 == 0 else r_int
        a = math.radians(giro + i * 180 / pontas)
        lista.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return lista


def estrela():
    t = 72
    c = t / 2
    forma = tela(t, t)
    d = ImageDraw.Draw(forma)
    d.polygon(pts(estrela_forma(c, c, 20, 9), 0, 0), fill=(255, 200, 40, 255))
    d.polygon(pts(estrela_forma(c, c - 1.5, 13, 5.5), 0, 0), fill=(255, 236, 130, 255))
    d.ellipse(pts([(c - 3, c - 5), (c + 3, c + 1)], 0, 0)[0] + pts([(c + 3, c + 1)], 0, 0)[0],
              fill=(255, 255, 240, 255))
    img = compor(brilho(forma, (255, 170, 30), 9, 1.6), brilho(forma, (255, 230, 120), 3), forma)
    reduzir(img, t, t).save(IMAGENS / "estrela.png")


def meteoro(nome, t, raio):
    c = t / 2
    forma = tela(t, t)
    d = ImageDraw.Draw(forma)
    contorno = []
    lados = 11
    for i in range(lados):
        a = 2 * math.pi * i / lados
        r = raio * random.uniform(0.78, 1.0)
        contorno.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts(contorno, 0, 0), fill=(92, 74, 98, 255))
    # sombra embaixo e luz em cima
    sombra = tela(t, t)
    ImageDraw.Draw(sombra).ellipse(pts([(c - raio * 0.6, c - raio * 0.2),
                                        (c + raio * 1.4, c + raio * 1.6)], 0, 0)[0]
                                   + pts([(c + raio * 1.4, c + raio * 1.6)], 0, 0)[0],
                                   fill=(30, 20, 40, 170))
    sombra = sombra.filter(ImageFilter.GaussianBlur(3 * ESCALA))
    luz = tela(t, t)
    ImageDraw.Draw(luz).ellipse(pts([(c - raio * 0.9, c - raio * 0.9),
                                     (c + raio * 0.1, c + raio * 0.1)], 0, 0)[0]
                                + pts([(c + raio * 0.1, c + raio * 0.1)], 0, 0)[0],
                                fill=(200, 160, 190, 110))
    luz = luz.filter(ImageFilter.GaussianBlur(3 * ESCALA))
    rocha = compor(forma, sombra, luz)
    d = ImageDraw.Draw(rocha)
    for _ in range(4):
        rc = raio * random.uniform(0.12, 0.24)
        x = c + random.uniform(-raio * 0.45, raio * 0.45)
        y = c + random.uniform(-raio * 0.45, raio * 0.45)
        d.ellipse(pts([(x - rc, y - rc), (x + rc, y + rc)], 0, 0)[0]
                  + pts([(x + rc, y + rc)], 0, 0)[0], fill=(55, 40, 62, 255))
        d.arc(pts([(x - rc, y - rc), (x + rc, y + rc)], 0, 0)[0]
              + pts([(x + rc, y + rc)], 0, 0)[0], 200, 340,
              fill=(150, 120, 150, 255), width=ESCALA)
    # recorta pelo contorno e põe um brilho vermelho de perigo
    mascara = forma.getchannel("A")
    rocha.putalpha(mascara)
    img = compor(brilho(forma, (255, 60, 70), 6, 0.8), rocha)
    reduzir(img, t, t).save(IMAGENS / f"{nome}.png")


def relogio():
    t = 56
    c = t / 2
    forma = tela(t, t)
    d = ImageDraw.Draw(forma)
    r = 15
    d.ellipse(pts([(c - r, c - r), (c + r, c + r)], 0, 0)[0] + pts([(c + r, c + r)], 0, 0)[0],
              fill=(20, 60, 90, 255), outline=(90, 240, 255, 255), width=3 * ESCALA)
    d.line(pts([(c, c), (c, c - 9)], 0, 0), fill=(220, 255, 255, 255), width=3 * ESCALA)
    d.line(pts([(c, c), (c + 7, c + 3)], 0, 0), fill=(220, 255, 255, 255), width=3 * ESCALA)
    d.ellipse(pts([(c - 2, c - 2), (c + 2, c + 2)], 0, 0)[0] + pts([(c + 2, c + 2)], 0, 0)[0],
              fill=(90, 240, 255, 255))
    img = compor(brilho(forma, (60, 220, 255), 7, 1.4), forma)
    reduzir(img, t, t).save(IMAGENS / "relogio.png")


def fundo():
    img = Image.new("RGB", (LARGURA, ALTURA))
    d = ImageDraw.Draw(img)
    topo, base = (6, 5, 22), (24, 8, 42)
    for y in range(ALTURA):
        f = y / ALTURA
        d.line([(0, y), (LARGURA, y)], fill=tuple(int(a + (b - a) * f) for a, b in zip(topo, base)))
    neb = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
    dn = ImageDraw.Draw(neb)
    for cor, x, y, rx, ry in [((150, 40, 200, 70), 600, 140, 260, 140),
                              ((40, 90, 220, 60), 180, 420, 300, 150),
                              ((220, 60, 140, 45), 450, 520, 220, 90),
                              ((60, 180, 230, 35), 120, 120, 180, 100)]:
        dn.ellipse([x - rx, y - ry, x + rx, y + ry], fill=cor)
    neb = neb.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img.convert("RGBA"), neb)
    # granulado leve
    gr = Image.effect_noise((LARGURA, ALTURA), 14).convert("L")
    gr = gr.point(lambda v: max(0, v - 128) // 6)
    grao = Image.new("RGBA", (LARGURA, ALTURA), (255, 255, 255, 0))
    grao.putalpha(gr)
    img = Image.alpha_composite(img, grao)
    img.convert("RGB").save(IMAGENS / "fundo.png")


def vinheta(nome, forca):
    """Borda vermelha translúcida que pisca quando a nave é atingida."""
    img = Image.new("RGBA", (LARGURA, ALTURA), (255, 30, 60, 0))
    alfa = Image.new("L", (LARGURA, ALTURA), 0)
    d = ImageDraw.Draw(alfa)
    d.rectangle([0, 0, LARGURA, ALTURA], fill=int(255 * forca))
    d.rounded_rectangle([60, 60, LARGURA - 60, ALTURA - 60], radius=80, fill=0)
    img.putalpha(alfa.filter(ImageFilter.GaussianBlur(45)))
    img.save(IMAGENS / f"{nome}.png")


def painel(nome, w, h, cor_borda, alfa_fundo=170, raio=18):
    img = Image.new("RGBA", (w * ESCALA, h * ESCALA), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * ESCALA - 1, h * ESCALA - 1], radius=raio * ESCALA,
                        fill=(14, 10, 36, alfa_fundo), outline=cor_borda, width=2 * ESCALA)
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


def tom(freq, dur, vol=0.5, queda=6.0, forma="sen"):
    out = []
    for i in range(int(TAXA * dur)):
        t = i / TAXA
        fase = 2 * math.pi * freq * t
        onda = math.sin(fase) if forma == "sen" else (2 * (t * freq % 1) - 1) * 0.6
        ataque = min(1, t / 0.005)
        out.append(onda * vol * ataque * math.exp(-queda * t))
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
    salvar_som("pegar", juntar(tom(988, 0.25, 0.35, 12), tom(1480, 0.35, 0.3, 10), atraso=0.06))
    salvar_som("relogio", juntar(tom(660, 0.2, 0.3, 10), tom(880, 0.2, 0.3, 10),
                                 tom(1320, 0.4, 0.3, 8), atraso=0.07))
    ruido = []
    filtro = 0.0
    for i in range(int(TAXA * 0.45)):
        t = i / TAXA
        filtro += (random.uniform(-1, 1) - filtro) * 0.12
        grave = math.sin(2 * math.pi * (110 - 60 * t) * t)
        ruido.append((filtro * 1.6 + grave * 0.7) * math.exp(-7 * t) * 0.8)
    salvar_som("batida", ruido)
    salvar_som("clique", tom(1200, 0.06, 0.25, 40))
    salvar_som("fim", juntar(tom(784, 0.3, 0.3, 6, "serra"), tom(587, 0.3, 0.3, 6, "serra"),
                             tom(440, 0.6, 0.3, 4, "serra"), atraso=0.18))
    salvar_som("recorde", juntar(*[tom(f, 0.3, 0.25, 7) for f in (523, 659, 784, 1047, 1319)],
                                 atraso=0.09))


if __name__ == "__main__":
    IMAGENS.mkdir(exist_ok=True)
    SONS.mkdir(exist_ok=True)
    nave()
    estrela()
    meteoro("meteoro_grande", 72, 26)
    meteoro("meteoro_pequeno", 52, 17)
    relogio()
    fundo()
    vinheta("dano_forte", 0.6)
    vinheta("dano_medio", 0.36)
    vinheta("dano_fraco", 0.16)
    painel("painel", 440, 420, (120, 90, 255, 230))
    painel("botao", 260, 54, (120, 90, 255, 200), 150, 14)
    painel("botao_ativo", 260, 54, (255, 200, 60, 255), 220, 14)
    sons()
    print("Imagens e sons gerados.")
