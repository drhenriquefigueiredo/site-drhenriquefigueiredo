#!/usr/bin/env python3
"""Artes estáticas do Instagram na identidade do site: carrossel (1080x1350) e story (1080x1920).

Uso (normalmente chamado por tools/ia_imagem.py a partir de content/capas/pedidos/<id>.json):
  arte.py --pedido PEDIDO.json --saida DIR [--imagem IA.jpg]

Pedido de carrossel:
  {"slug": id, "formato": "carrossel", "topic": "mao", "title": "Título da capa",
   "slides": [{"titulo": "...", "texto": "..."}, ...],          # 3 a 7 slides de conteúdo
   "final": {"titulo": "Salve para lembrar", "texto": "..."}}   # opcional
  -> DIR/car-<id>-01.jpg (capa) ... DIR/car-<id>-NN.jpg (final)

Pedido de story:
  {"slug": id, "formato": "story", "topic": "dor", "rotulo": "Você sabia?",
   "title": "Frase principal", "texto": "Complemento curto", "rodape": "Novo post no perfil"}
  -> DIR/story-<id>.jpg
"""
import argparse, json, os, unicodedata
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
IMG = os.path.join(RAIZ, 'site', 'assets', 'img')
F = lambda n, s: ImageFont.truetype(os.path.join(AQUI, 'fonts', n), s)

NAVY = (14, 30, 58); GOLD = (184, 151, 90); GOLD_SOFT = (216, 197, 157); WHITE = (255, 255, 255)
CREAM = (245, 241, 232); INK = (30, 42, 61); MUTED = (91, 103, 121)
ROTULO = {'mao': 'Mão e punho', 'ortopedia': 'Ortopedia', 'dor': 'Dor', 'regenerativa': 'Medicina regenerativa',
          'esporte': 'Lesões e esporte'}
ID_LONGA = 'Médico ortopedista · CRM-SP 199.832 · RQE 102783 / 124871'
AVISO = 'Conteúdo informativo; não substitui a avaliação médica.'


def nfc(t):
    return unicodedata.normalize('NFC', str(t or ''))


def quebrar(d, texto, fonte, largura):
    linhas = []
    for par in nfc(texto).split('\n'):
        atual = ''
        for p in par.split():
            teste = (atual + ' ' + p).strip()
            if d.textlength(teste, font=fonte) <= largura:
                atual = teste
            else:
                if atual: linhas.append(atual)
                atual = p
        linhas.append(atual)
    return linhas


def caber(d, texto, nome, tamanhos, largura, max_linhas):
    for t in tamanhos:
        f = F(nome, t)
        ls = quebrar(d, texto, f, largura)
        if len(ls) <= max_linhas:
            return f, ls
    return f, ls[:max_linhas]


def escrever(d, x, y, linhas, fonte, cor, entre=1.12):
    for l in linhas:
        d.text((x, y), l, font=fonte, fill=cor)
        y += int(fonte.size * entre)
    return y


def logo(nome, w):
    lg = Image.open(os.path.join(IMG, nome)).convert('RGBA')
    return lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)


def cobrir(im, w, h, foco_y=0.35):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int(max(0, min(im.height - h, (im.height - h) * foco_y)))
    return im.crop((x, y, x + w, y + h))


def pontos(d, W, y, total, atual, escuro):
    r, gap = 7, 26
    x0 = W // 2 - (total - 1) * gap // 2
    for i in range(total):
        cor = GOLD if i == atual else ((200, 200, 200) if not escuro else (70, 88, 120))
        d.ellipse([x0 + i * gap - r, y - r, x0 + i * gap + r, y + r], fill=cor)


def slide_capa(p, ia, total, saida):
    W, H = 1080, 1350
    base = Image.new('RGB', (W, H), NAVY)
    if ia and os.path.exists(ia):
        base.paste(cobrir(Image.open(ia).convert('RGB'), W, 760, 0.3), (0, 0))
    g = Image.new('L', (1, H))
    for yy in range(H):
        g.putpixel((0, yy), int(255 * (0 if yy < 400 else (1 if yy > 760 else (yy - 400) / 360))))
    base = Image.composite(Image.new('RGB', (W, H), NAVY), base, g.resize((W, H)))
    d = ImageDraw.Draw(base)
    d.rectangle([32, 32, W - 33, H - 33], outline=GOLD, width=1)
    x = 84
    d.text((x, 700), ROTULO.get(p.get('topic'), 'Ortopedia').upper(), font=F('Manrope-Bold.ttf', 26), fill=GOLD)
    d.line([x, 744, x + 70, 744], fill=GOLD, width=3)
    f, ls = caber(d, nfc(p['title']), 'EBGaramond-SemiBold.ttf', [80, 72, 66, 60, 54], W - 2 * x, 4)
    escrever(d, x, 772, ls, f, WHITE, 1.05)
    fa = F('Manrope-SemiBold.ttf', 24)
    seta = 'Arraste para o lado  »'
    d.text((W - x - d.textlength(seta, font=fa), H - 215), seta, font=fa, fill=GOLD_SOFT)
    lg = logo('logo-branco.png', 200)
    base.paste(lg, (x, H - 84 - lg.height), lg)
    d.text((x + 220, H - 84 - lg.height // 2 - 10), ID_LONGA, font=F('Manrope-Medium.ttf', 18), fill=GOLD_SOFT)
    pontos(d, W, H - 56, total, 0, True)
    nome = os.path.join(saida, f"car-{p['slug']}-01.jpg")
    base.save(nome, quality=90, optimize=True, progressive=True)
    return nome


def slide_texto(p, s, i, total, saida):
    W, H = 1080, 1350
    base = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(base)
    d.rectangle([32, 32, W - 33, H - 33], outline=GOLD, width=1)
    x, larg = 96, W - 192
    topo, fundo = 110, H - 210
    ft, lt = caber(d, s['titulo'], 'EBGaramond-SemiBold.ttf', [72, 66, 60, 55, 50], larg, 3)
    alt_t = len(lt) * int(ft.size * 1.05)
    for t in [48, 45, 42, 39, 36, 33, 30, 28]:
        fb = F('Manrope-Medium.ttf', t)
        lb = quebrar(d, s.get('texto', ''), fb, larg)
        alt_b = len(lb) * int(t * 1.45)
        bloco = 150 + 34 + alt_t + 40 + alt_b
        if bloco <= fundo - topo:
            break
    y = topo + max(0, (fundo - topo - bloco) // 2 - 40)
    d.text((x, y - 20), f'{i:02d}', font=F('EBGaramond-SemiBold.ttf', 116), fill=GOLD)
    d.line([x, y + 150, x + 70, y + 150], fill=GOLD, width=3)
    y = escrever(d, x, y + 184, lt, ft, NAVY, 1.05) + 40
    escrever(d, x, y, lb, fb, INK, 1.45)
    lg = logo('logo-azul.png', 170)
    base.paste(lg, (x, H - 80 - lg.height), lg)
    fr = F('Manrope-Medium.ttf', 18)
    rq = 'CRM-SP 199.832 · RQE 102783 / 124871'
    d.text((W - x - d.textlength(rq, font=fr), H - 80 - lg.height // 2 - 10), rq, font=fr, fill=MUTED)
    pontos(d, W, H - 56, total, i, False)
    nome = os.path.join(saida, f"car-{p['slug']}-{i + 1:02d}.jpg")
    base.save(nome, quality=90, optimize=True, progressive=True)
    return nome


def slide_final(p, total, saida):
    W, H = 1080, 1350
    fim = p.get('final') or {}
    base = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(base)
    d.rectangle([32, 32, W - 33, H - 33], outline=GOLD, width=1)
    ass = logo('assinatura-branca.png', 170)
    larg = W - 220
    ft, lt = caber(d, fim.get('titulo', 'Salve para lembrar e compartilhe com quem precisa'),
                   'EBGaramond-SemiBold.ttf', [68, 62, 56, 50], larg, 3)
    fb = F('Manrope-Medium.ttf', 34)
    lb = quebrar(d, fim.get('texto', 'Dúvidas sobre o seu caso? Agende uma avaliação pelo link da bio.'), fb, larg)
    bloco = ass.height + 60 + len(lt) * int(ft.size * 1.08) + 30 + len(lb) * int(fb.size * 1.45)
    y = max(110, (H - 240 - bloco) // 2)
    base.paste(ass, ((W - ass.width) // 2, y), ass)
    y += ass.height + 60
    for l in lt:
        d.text(((W - d.textlength(l, font=ft)) // 2, y), l, font=ft, fill=WHITE); y += int(ft.size * 1.08)
    y += 30
    for l in lb:
        d.text(((W - d.textlength(l, font=fb)) // 2, y), l, font=fb, fill=GOLD_SOFT); y += int(fb.size * 1.45)
    fa = F('Manrope-Medium.ttf', 22)
    for k, l in enumerate([AVISO, 'Dr. Henrique Figueiredo · ' + ID_LONGA]):
        d.text(((W - d.textlength(l, font=fa)) // 2, H - 190 + k * 36), l, font=fa, fill=GOLD_SOFT)
    pontos(d, W, H - 56, total, total - 1, True)
    nome = os.path.join(saida, f"car-{p['slug']}-{total:02d}.jpg")
    base.save(nome, quality=90, optimize=True, progressive=True)
    return nome


def carrossel(p, ia, saida):
    slides = p['slides'][:8]
    total = len(slides) + 2
    feitos = [slide_capa(p, ia, total, saida)]
    for i, s in enumerate(slides, start=1):
        feitos.append(slide_texto(p, s, i, total, saida))
    feitos.append(slide_final(p, total, saida))
    return feitos


def story(p, ia, saida):
    """Story 1080x1920. Áreas livres para a interface do Instagram: 250 px no topo e 340 px na base."""
    W, H = 1080, 1920
    escuro = bool(ia and os.path.exists(ia))
    base = Image.new('RGB', (W, H), NAVY if escuro else CREAM)
    if escuro:  # imagem de IA no topo, texto sobre o azul
        base.paste(cobrir(Image.open(ia).convert('RGB'), W, 820, 0.3), (0, 0))
        g = Image.new('L', (1, H))
        for yy in range(H):
            g.putpixel((0, yy), int(255 * (0.15 if yy < 300 else (1 if yy > 820 else 0.15 + 0.85 * (yy - 300) / 520))))
        base = Image.composite(Image.new('RGB', (W, H), NAVY), base, g.resize((W, H)))
    d = ImageDraw.Draw(base)
    cor_t, cor_b, cor_r = (WHITE, GOLD_SOFT, GOLD_SOFT) if escuro else (NAVY, INK, MUTED)
    x, larg = 100, W - 200
    limite = H - 560  # o bloco de texto termina antes do logo
    ft, lt = caber(d, p['title'], 'EBGaramond-SemiBold.ttf', [86, 78, 70, 64, 58], larg, 4)
    fb = F('Manrope-Medium.ttf', 40)
    lb = quebrar(d, p.get('texto', ''), fb, larg)[:6] if p.get('texto') else []
    alt = 84 + len(lt) * int(ft.size * 1.05) + (40 + len(lb) * int(40 * 1.42) if lb else 0) + (110 if p.get('rodape') else 0)
    y = 760 if escuro else max(300, (300 + limite - alt) // 2)
    y = min(y, limite - alt)
    rot = nfc(p.get('rotulo') or ROTULO.get(p.get('topic'), 'Ortopedia')).upper()
    d.text((x, y), rot, font=F('Manrope-Bold.ttf', 30), fill=GOLD)
    d.line([x, y + 50, x + 80, y + 50], fill=GOLD, width=3)
    y = escrever(d, x, y + 84, lt, ft, cor_t, 1.05)
    if lb:
        y = escrever(d, x, y + 40, lb, fb, cor_b, 1.42)
    if p.get('rodape'):
        fr = F('Manrope-Bold.ttf', 30)
        rod = nfc(p['rodape'])
        d.rounded_rectangle([x, y + 30, x + d.textlength(rod, font=fr) + 56, y + 100], radius=35, outline=GOLD, width=2)
        d.text((x + 28, y + 47), rod, font=fr, fill=GOLD)
    lg = logo('logo-branco.png' if escuro else 'logo-azul.png', 190)
    base.paste(lg, ((W - lg.width) // 2, H - 470), lg)
    fa = F('Manrope-Medium.ttf', 22)
    l = 'CRM-SP 199.832 · RQE 102783 / 124871'
    d.text(((W - d.textlength(l, font=fa)) // 2, H - 470 + lg.height + 14), l, font=fa, fill=cor_r)
    nome = os.path.join(saida, f"story-{p['slug']}.jpg")
    base.save(nome, quality=90, optimize=True, progressive=True)
    return [nome]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pedido', required=True); ap.add_argument('--saida', required=True); ap.add_argument('--imagem')
    a = ap.parse_args()
    p = json.load(open(a.pedido, encoding='utf-8'))
    os.makedirs(a.saida, exist_ok=True)
    feitos = carrossel(p, a.imagem, a.saida) if p.get('formato') == 'carrossel' else story(p, a.imagem, a.saida)
    print(json.dumps([os.path.basename(f) for f in feitos]))


if __name__ == '__main__':
    main()
