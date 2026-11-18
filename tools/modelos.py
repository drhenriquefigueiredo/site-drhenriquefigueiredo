#!/usr/bin/env python3
"""Modelos de capa do Instagram (1080x1350, 4:5), em rodízio para o feed não ficar repetitivo.

Três modelos, sempre na identidade azul-marinho, creme e dourado:
  foto     foto em tela cheia, degradê suave só na base, gancho grande em branco (o mais "revista")
  claro    fundo creme, só tipografia: gancho bem grande em azul, palavra entre *asteriscos* em dourado
  recorte  fundo creme com a foto recortada no alto e o texto embaixo (claro, mas com imagem)

Escolha do modelo (campo "modelo" do pedido, ou automático):
  - "modelo": "foto" | "claro" | "recorte" no pedido manda.
  - Sem o campo, vai pela data de publicação (fila das redes, posts ou calendário): o dia do ano em rodízio
    de 3, então dois dias seguidos (ou em dias alternados) nunca repetem o modelo.
  - Sem foto disponível, "foto" e "recorte" viram "claro".

Texto da capa: "gancho" (2 a 6 palavras, vai grande) e "apoio" (frase curta embaixo). Sem esses campos, o
título é dividido sozinho no primeiro ":" ou "?" (ex.: "Cotovelo de tenista: 5 fatos..." -> gancho
"Cotovelo de tenista", apoio "5 fatos..."). O título completo continua na legenda e no 2º card.
"""
import datetime as dt, glob, hashlib, json, os, re, unicodedata
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CONTENT = os.path.join(RAIZ, 'content')
IMG = os.path.join(RAIZ, 'site', 'assets', 'img')
F = lambda n, s: ImageFont.truetype(os.path.join(AQUI, 'fonts', n), s)

NAVY = (14, 30, 58); GOLD = (184, 151, 90); GOLD_SOFT = (216, 197, 157); WHITE = (255, 255, 255)
CREAM = (245, 241, 232); INK = (30, 42, 61); MUTED = (91, 103, 121); GOLD_DARK = (150, 118, 62)
MODELOS = ('foto', 'claro', 'recorte')
NOME = 'Dr. Henrique Figueiredo'
ID = 'Médico ortopedista · CRM-SP 199.832 · RQE 102783 / 124871'


def nfc(t):
    return unicodedata.normalize('NFC', str(t or '')).strip()


# ---------- escolha do modelo ----------

def data_de(slug):
    """Data de publicação do item: fila das redes > artigo aprovado > calendário > data no começo do id."""
    for f in glob.glob(os.path.join(CONTENT, 'redes', 'fila', '*.json')):
        try:
            q = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if q.get('id') == slug or q.get('artigo') == slug:
            return q.get('date')
    for f in glob.glob(os.path.join(CONTENT, 'posts', '*.json')):
        try:
            p = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if p.get('slug') == slug:
            return p.get('date')
    try:
        for c in json.load(open(os.path.join(CONTENT, 'calendario.json'), encoding='utf-8')):
            if c.get('slug') == slug and c.get('date'):
                return c['date']
    except Exception:
        pass
    m = re.search(r'(\d{4}-\d{2}-\d{2})', slug or '')
    return m.group(1) if m else None


def escolher(slug, pedido_modelo=None, tem_foto=True):
    m = (pedido_modelo or '').strip().lower()
    if m not in MODELOS:
        d = data_de(slug)
        try:
            n = dt.date.fromisoformat(d).toordinal()
        except Exception:
            n = int(hashlib.md5((slug or '').encode()).hexdigest(), 16)
        m = MODELOS[n % 3]
    if m != 'claro' and not tem_foto:
        m = 'claro'
    return m


def dividir(titulo, gancho=None, apoio=None):
    """Gancho curto + apoio. Respeita o que veio no pedido; senão divide o título no 1º ':' ou '?'."""
    titulo = nfc(titulo)
    if gancho:
        return nfc(gancho), nfc(apoio)
    m = re.match(r'^(.{6,60}?)([:?])\s+(.+)$', titulo)
    if m:
        g = m.group(1) + ('?' if m.group(2) == '?' else '')
        a = m.group(3)
        return g, a[:1].upper() + a[1:]
    return titulo, nfc(apoio)


# ---------- desenho ----------

def cobrir(im, w, h, centro=(0.5, 0.4)):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = int((im.width - w) * centro[0]); y = int((im.height - h) * centro[1])
    return im.crop((x, y, x + w, y + h))


def _palavras(texto):
    """[(palavra, destaque)] — *assim* marca destaque em dourado."""
    out, dest = [], False
    for p in nfc(texto).split():
        ini, fim = p.startswith('*'), p.endswith('*') and len(p) > 1
        if ini: dest = True
        out.append((p.strip('*'), dest))
        if fim or (ini and p.endswith('*')): dest = False
    return out


def quebrar(d, texto, fonte, largura):
    linhas, atual = [], []
    for w, h in _palavras(texto):
        teste = ' '.join(x for x, _ in atual + [(w, h)])
        if atual and d.textlength(teste, font=fonte) > largura:
            linhas.append(atual); atual = [(w, h)]
        else:
            atual.append((w, h))
    if atual: linhas.append(atual)
    return linhas


def larga_demais(d, linhas, fonte, largura):
    """Palavra comprida (ex.: "Viscossuplementação") que sozinha passa da margem."""
    return any(d.textlength(' '.join(w for w, _ in l), font=fonte) > largura for l in linhas)


def caber(d, texto, nome, tamanhos, largura, max_linhas):
    for t in list(tamanhos) + [t for t in range(min(tamanhos) - 6, 40, -6)]:
        f = F(nome, t)
        ls = quebrar(d, texto, f, largura)
        if len(ls) <= max_linhas and not larga_demais(d, ls, f, largura):
            return f, ls
    return f, ls[:max_linhas]


def escrever(d, x, y, linhas, fonte, cor, cor_dest=None, entre=1.06):
    for linha in linhas:
        cx = x
        for i, (w, h) in enumerate(linha):
            txt = w + (' ' if i < len(linha) - 1 else '')
            d.text((cx, y), txt, font=fonte, fill=(cor_dest or cor) if h else cor)
            cx += d.textlength(txt, font=fonte)
        y += int(fonte.size * entre)
    return y


def apoio_linhas(d, apoio, fonte, largura, n):
    """Linhas da frase de apoio; se não couber em n linhas, fica de fora (nunca corta no meio)."""
    ls = quebrar(d, apoio, fonte, largura) if apoio else []
    return ls if len(ls) <= n else []


def altura(linhas, fonte, entre=1.06):
    return len(linhas) * int(fonte.size * entre)


def assinatura(escuro, h):
    lg = Image.open(os.path.join(IMG, 'assinatura-branca.png' if escuro else 'assinatura-azul.png')).convert('RGBA')
    return lg.resize((round(lg.width * h / lg.height), h), Image.LANCZOS)


def rodape(base, d, x, y_base, escuro):
    """Monograma "H." + nome + CRM/RQE (identificação exigida pelo CFM), discreto."""
    ass = assinatura(escuro, 74)
    base.paste(ass, (x, y_base - ass.height), ass)
    tx = x + ass.width + 18
    d.text((tx, y_base - 64), NOME, font=F('Manrope-SemiBold.ttf', 23), fill=WHITE if escuro else NAVY)
    d.text((tx, y_base - 32), ID, font=F('Manrope-Medium.ttf', 18), fill=GOLD_SOFT if escuro else MUTED)


def rotulo(d, x, y, tema, cor):
    f = F('Manrope-Bold.ttf', 24)
    cx = x
    for ch in nfc(tema).upper():  # letras um pouco espaçadas
        d.text((cx, y), ch, font=f, fill=cor)
        cx += d.textlength(ch, font=f) + 2.5
    d.line([x, y + 42, x + 64, y + 42], fill=cor, width=3)
    return y + 42


def pontos(d, W, y, total, atual, escuro):
    r, gap = 7, 26
    x0 = W // 2 - (total - 1) * gap // 2
    for i in range(total):
        cor = GOLD if i == atual else ((70, 88, 120) if escuro else (205, 200, 190))
        d.ellipse([x0 + i * gap - r, y - r, x0 + i * gap + r, y + r], fill=cor)


def capa_ig(foto, tema, gancho, apoio, modelo, carrossel_total=None, centro=(0.5, 0.4)):
    """Devolve a capa 1080x1350. carrossel_total = nº de artes (mostra "Arraste" e os pontinhos)."""
    W, H, x = 1080, 1350, 84
    larg = W - 2 * x
    escuro = modelo == 'foto'
    if modelo == 'foto':
        base = cobrir(foto, W, H, centro)
        # degradê só na base: a foto respira, o texto fica legível
        g = Image.new('L', (1, H))
        for yy in range(H):
            t = 0 if yy < H * 0.40 else min(1, (yy - H * 0.40) / (H * 0.36))
            g.putpixel((0, yy), int(235 * (t ** 1.3)))
        base = Image.composite(Image.new('RGB', (W, H), NAVY), base, g.resize((W, H)))
    else:
        base = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(base)
    fundo = H - 92 - (70 if carrossel_total else 0)  # linha de base do rodapé
    rodape(base, d, x, fundo, escuro)
    if carrossel_total:
        fa = F('Manrope-SemiBold.ttf', 24)
        seta = 'Arraste para o lado  »'
        d.text((W - x - d.textlength(seta, font=fa), fundo - 50), seta, font=fa, fill=GOLD_SOFT if escuro else GOLD_DARK)
        pontos(d, W, H - 62, carrossel_total, 0, escuro)

    fa = F('Manrope-Medium.ttf', 36)
    if modelo == 'foto':
        fg, lg = caber(d, gancho, 'EBGaramond-SemiBold.ttf', [112, 104, 96, 88, 80, 72], larg, 3)
        la = apoio_linhas(d, apoio, fa, larg, 2)
        y = fundo - 120 - (altura(la, fa, 1.35) + 30 if la else 0) - altura(lg, fg, 1.02)
        rotulo(d, x, y - 78, tema, GOLD)
        y = escrever(d, x, y, lg, fg, WHITE, GOLD_SOFT, 1.02)
        if la:
            escrever(d, x, y + 30, la, fa, GOLD_SOFT, None, 1.35)
    elif modelo == 'claro':
        rotulo(d, x, 120, tema, GOLD_DARK)
        fg, lg = caber(d, gancho, 'EBGaramond-SemiBold.ttf', [136, 124, 112, 102, 92, 84], larg, 4)
        fa = F('Manrope-Medium.ttf', 40)
        la = apoio_linhas(d, apoio, fa, larg, 3)
        bloco = altura(lg, fg, 1.0) + (80 + altura(la, fa, 1.38) if la else 0)
        y = 250 + max(0, (fundo - 150 - 250 - bloco) // 2)
        y = escrever(d, x, y, lg, fg, NAVY, GOLD_DARK, 1.0)
        if la:
            d.line([x, y + 40, x + 64, y + 40], fill=GOLD, width=3)
            escrever(d, x, y + 80, la, fa, INK, None, 1.38)
    else:  # recorte
        m = 56
        alto = 660 if carrossel_total else 720
        base.paste(cobrir(foto, W - 2 * m, alto, centro), (m, m))
        y = m + alto + 50
        y = rotulo(d, x, y, tema, GOLD_DARK) + 30
        espaco = fundo - 110 - y
        fa = F('Manrope-Medium.ttf', 34)
        la = apoio_linhas(d, apoio, fa, larg, 2)
        for t in [104, 96, 88, 80, 74, 68, 62, 56]:
            fg = F('EBGaramond-SemiBold.ttf', t)
            lg = quebrar(d, gancho, fg, larg)
            if len(lg) <= 3 and not larga_demais(d, lg, fg, larg) and altura(lg, fg, 1.02) + (24 + altura(la, fa, 1.35) if la else 0) <= espaco:
                break
        else:
            la = []
        y = escrever(d, x, y, lg, fg, NAVY, GOLD_DARK, 1.02)
        if la:
            escrever(d, x, y + 24, la, fa, INK, None, 1.35)
    return base
