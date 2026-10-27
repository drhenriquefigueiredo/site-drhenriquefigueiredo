#!/usr/bin/env python3
"""Gera as capas de um artigo com a identidade visual do site.

capa.py --slug SLUG --titulo "Título" --tema "Mão e punho" --saida DIR
Gera:
  DIR/blog-<slug>.jpg   1200x600  (site, Google, Facebook, og:image)
  DIR/blog-<slug>.webp  1200x600
  DIR/ig-<slug>.jpg     1080x1350 (Instagram, 4:5)
"""
import argparse, hashlib, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SITE = os.path.join(RAIZ, 'site') if os.path.isdir(os.path.join(RAIZ, 'site')) else RAIZ
IMG = os.path.join(SITE, 'assets', 'img')
F = lambda n, s: ImageFont.truetype(os.path.join(AQUI, 'fonts', n), s)

NAVY = (14, 30, 58); NAVY2 = (21, 41, 75); GOLD = (184, 151, 90); GOLD_SOFT = (216, 197, 157); WHITE = (255, 255, 255)
RODAPE = 'Médico ortopedista · CRM-SP 199.832 · RQE 102783 / 124871'


IMAGEM_IA = None  # caminho da imagem gerada por IA (tools/ia_imagem.py); sem ela, usa um fundo gráfico


def foto_para(slug):
    if IMAGEM_IA and os.path.exists(IMAGEM_IA):
        return Image.open(IMAGEM_IA).convert('RGB')
    return fundo_grafico(slug)


def fundo_grafico(slug):
    """Fundo abstrato navy/dourado (sem fotos pessoais), usado se a imagem de IA faltar."""
    import random
    rnd = random.Random(slug)
    im = Image.new('RGB', (900, 900), NAVY2)
    d = ImageDraw.Draw(im)
    for _ in range(9):
        r = rnd.randint(120, 420); x = rnd.randint(-100, 900); y = rnd.randint(-100, 900)
        d.ellipse([x - r, y - r, x + r, y + r], outline=GOLD, width=rnd.choice([1, 1, 2]))
    return im.filter(ImageFilter.GaussianBlur(0.6))


def cobrir(im, w, h, foco_y=0.3):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int(max(0, min(im.height - h, (im.height - h) * foco_y)))
    return im.crop((x, y, x + w, y + h))


def quebrar(draw, texto, fonte, largura):
    palavras, linhas, atual = texto.split(), [], ''
    for p in palavras:
        teste = (atual + ' ' + p).strip()
        if draw.textlength(teste, font=fonte) <= largura:
            atual = teste
        else:
            if atual: linhas.append(atual)
            atual = p
    if atual: linhas.append(atual)
    return linhas


def titulo_ajustado(draw, texto, largura, max_linhas, tamanhos):
    for t in tamanhos:
        f = F('Cormorant-SemiBold.ttf', t)
        ls = quebrar(draw, texto, f, largura)
        if len(ls) <= max_linhas:
            return f, ls
    return f, ls[:max_linhas]


def gradiente_h(w, h, inicio, fim, cor):
    g = Image.new('L', (w, 1))
    for x in range(w):
        t = 0 if x < inicio else (1 if x > fim else (x - inicio) / (fim - inicio))
        g.putpixel((x, 0), int(255 * t))
    g = g.resize((w, h))
    camada = Image.new('RGB', (w, h), cor)
    return camada, g


def logo(w):
    lg = Image.open(os.path.join(IMG, 'logo-branco.png')).convert('RGBA')
    r = w / lg.width
    return lg.resize((w, round(lg.height * r)), Image.LANCZOS)


def capa_larga(slug, titulo, tema, saida):
    W, H = 1200, 600
    base = Image.new('RGB', (W, H), NAVY)
    foto = cobrir(foto_para(slug), 520, H, 0.15)
    base.paste(foto, (W - 520, 0))
    # degradê navy -> foto
    camada, mask = gradiente_h(W, H, W - 560, W - 300, NAVY)
    mask = Image.eval(mask, lambda v: 255 - v)
    base = Image.composite(camada, base, mask)
    d = ImageDraw.Draw(base)
    # moldura dourada fina
    d.rectangle([28, 28, W - 29, H - 29], outline=GOLD + (0,), width=1)
    x = 72
    ft = F('Manrope-Bold.ttf', 20)
    d.text((x, 92), tema.upper(), font=ft, fill=GOLD, spacing=4)
    d.line([x, 128, x + 56, 128], fill=GOLD, width=2)
    f, linhas = titulo_ajustado(d, titulo, 640, 4, [64, 58, 52, 46, 42])
    y = 156
    for l in linhas:
        d.text((x, y), l, font=f, fill=WHITE)
        y += int(f.size * 1.08)
    lg = logo(190)
    base.paste(lg, (x, H - 72 - lg.height), lg)
    fr = F('Manrope-Medium.ttf', 15)
    d.text((x + 210, H - 72 - lg.height // 2 - 9), RODAPE, font=fr, fill=GOLD_SOFT)
    base.save(os.path.join(saida, f'blog-{slug}.jpg'), quality=86, optimize=True, progressive=True)
    base.save(os.path.join(saida, f'blog-{slug}.webp'), quality=80, method=6)


def capa_instagram(slug, titulo, tema, saida):
    W, H = 1080, 1350
    base = Image.new('RGB', (W, H), NAVY)
    foto = cobrir(foto_para(slug), W, 760, 0.12)
    base.paste(foto, (0, 0))
    # degradê vertical da foto para o navy
    g = Image.new('L', (1, H))
    for yy in range(H):
        t = 0 if yy < 420 else (1 if yy > 760 else (yy - 420) / 340)
        g.putpixel((0, yy), int(255 * t))
    base = Image.composite(Image.new('RGB', (W, H), NAVY), base, g.resize((W, H)))
    d = ImageDraw.Draw(base)
    d.rectangle([32, 32, W - 33, H - 33], outline=GOLD, width=1)
    x = 84
    ft = F('Manrope-Bold.ttf', 26)
    d.text((x, 720), tema.upper(), font=ft, fill=GOLD)
    d.line([x, 764, x + 70, 764], fill=GOLD, width=3)
    f, linhas = titulo_ajustado(d, titulo, W - 2 * x, 5, [84, 76, 68, 62, 56])
    y = 796
    for l in linhas:
        d.text((x, y), l, font=f, fill=WHITE)
        y += int(f.size * 1.06)
    lg = logo(230)
    base.paste(lg, (x, H - 84 - lg.height), lg)
    fr = F('Manrope-Medium.ttf', 20)
    d.text((x + 250, H - 84 - lg.height // 2 - 12), 'Médico ortopedista · CRM-SP 199.832', font=fr, fill=GOLD_SOFT)
    base.save(os.path.join(saida, f'ig-{slug}.jpg'), quality=88, optimize=True, progressive=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', required=True); ap.add_argument('--titulo', required=True)
    ap.add_argument('--tema', required=True); ap.add_argument('--saida', required=True)
    ap.add_argument('--imagem', help='imagem de IA para o fundo (padrão: <saida>/ia-<slug>.jpg, se existir)')
    a = ap.parse_args()
    IMAGEM_IA = a.imagem or os.path.join(a.saida, f'ia-{a.slug}.jpg')
    os.makedirs(a.saida, exist_ok=True)
    capa_larga(a.slug, a.titulo, a.tema, a.saida)
    capa_instagram(a.slug, a.titulo, a.tema, a.saida)
    print('ok')
