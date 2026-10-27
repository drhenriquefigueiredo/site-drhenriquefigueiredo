#!/usr/bin/env python3
"""Publica os artigos aprovados do blog do Dr. Henrique Figueiredo.

Lê content/posts/*.json e publica só os que têm "status": "aprovado" e
"date" <= hoje (horário de Brasília). Para cada publicação:
  - gera site/blog/<slug>/index.html no layout do site
  - refaz a lista do blog, os 3 artigos da página inicial, o sitemap,
    a seção de artigos do llms.txt e o feed RSS (blog/feed.xml)
Pode rodar quantas vezes quiser: o resultado é sempre o mesmo para o mesmo dia.

Uso:  python3 tools/build.py [--hoje AAAA-MM-DD] [--previa SLUG]
  --previa gera a página de um rascunho mesmo sem aprovação (para conferência).
"""
import argparse, datetime as dt, glob, html, json, os, re, sys
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SITE = os.path.join(RAIZ, 'site')
CONTENT = os.path.join(RAIZ, 'content')
DOM = 'https://drhenriquefigueiredo.com.br'
WA = 'https://wa.me/5519999280514?text=Ol%C3%A1%21%20Gostaria%20de%20agendar%20uma%20consulta%20com%20o%20Dr.%20Henrique%20Figueiredo.'
TEMAS = {  # chave: (rótulo, área de atuação para o link do autor)
    'mao': ('Mão e punho', ('/areas-de-atuacao/cirurgia-da-mao/', 'Cirurgia da Mão')),
    'ortopedia': ('Ortopedia', ('/areas-de-atuacao/ortopedia-e-traumatologia/', 'Ortopedia e Traumatologia')),
    'dor': ('Dor', ('/areas-de-atuacao/medicina-regenerativa-e-dor/', 'Medicina Regenerativa e Dor')),
    'regenerativa': ('Medicina regenerativa', ('/areas-de-atuacao/medicina-regenerativa-e-dor/', 'Medicina Regenerativa e Dor')),
    'esporte': ('Lesões e esporte', ('/areas-de-atuacao/ortopedia-e-traumatologia/', 'Ortopedia e Traumatologia')),
}
ORDEM_TEMAS = ['mao', 'ortopedia', 'dor', 'regenerativa', 'esporte']
MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
SETA = '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
e = lambda s: html.escape(s or '', quote=True)


def data_br(d):
    y, m, dd = map(int, d.split('-'))
    return f'{dd} de {MESES[m - 1]} de {y}'


def ler(p):
    return open(p, encoding='utf-8').read()


def gravar(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p) and ler(p) == t:
        return False
    open(p, 'w', encoding='utf-8').write(t)
    return True


def copiar_capas(slug):
    """As capas ficam em content/capas até o dia da publicação; só então entram no site.
    Assim o site (e a Netlify) só muda nos dias de publicação."""
    for nome, destino in [(f'blog-{slug}.jpg', 'blog'), (f'blog-{slug}.webp', 'blog'), (f'ig-{slug}.jpg', 'social')]:
        org = os.path.join(CONTENT, 'capas', nome)
        dst = os.path.join(SITE, 'assets', destino, nome)
        if os.path.exists(org):
            dados = open(org, 'rb').read()
            if not os.path.exists(dst) or open(dst, 'rb').read() != dados:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'wb').write(dados)


def carregar(hoje, previa=None):
    posts = json.load(open(os.path.join(CONTENT, 'legacy.json'), encoding='utf-8'))
    novos = []
    for f in sorted(glob.glob(os.path.join(CONTENT, 'posts', '*.json'))):
        p = json.load(open(f, encoding='utf-8'))
        ok = p.get('status') == 'aprovado' and p['date'] <= hoje
        if ok or p['slug'] == previa:
            p['legacy'] = False
            p['img'] = f"/assets/blog/blog-{p['slug']}.jpg"
            if ok:
                copiar_capas(p['slug'])
            txt = re.sub(r'<[^>]+>', ' ', p['body_html'] + ' '.join(q['q'] + ' ' + q['a'] for q in p.get('faq', [])))
            p['read_min'] = max(2, round(len(txt.split()) / 200))
            novos.append(p)
    todos = posts + novos
    todos.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    return todos, novos


def card(p, tag='h3'):
    webp = p['img'].rsplit('.', 1)[0] + '.webp'
    return (f'<a class="post-card" href="/blog/{p["slug"]}/"><span class="post-thumb"><picture><source srcset="{webp}" type="image/webp">'
            f'<img src="{p["img"]}" alt="" width="800" height="400" loading="lazy" decoding="async"></picture></span>'
            f'<span class="post-meta"><span class="topic">{TEMAS[p["topic"]][0]}</span><time datetime="{p["date"]}">{data_br(p["date"])}</time></span>'
            f'<{tag}>{e(p["title"])}</{tag}><p>{e(p["excerpt"])}</p><span class="read">Ler artigo {SETA}</span></a>')


def pagina_artigo(p, todos, molde):
    cab, resto = molde.split('<main id="conteudo">', 1)
    rodape = resto.split('</main>', 1)[1]
    url = f'{DOM}/blog/{p["slug"]}/'
    img = DOM + p['img']
    titulo_seo = p.get('seo_title') or p['title']
    rotulo, (area_url, area_nome) = TEMAS[p['topic']]
    pub = f'{p["date"]}T09:00:00-03:00'
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": DOM + '/'},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": DOM + '/blog/'},
            {"@type": "ListItem", "position": 3, "name": p['title'], "item": url}]},
        {"@context": "https://schema.org", "@type": ["BlogPosting", "MedicalWebPage"], "headline": p['title'], "description": p['description'],
         "image": img, "datePublished": pub, "dateModified": p.get('modified', pub), "inLanguage": "pt-BR",
         "mainEntityOfPage": url, "url": url, "articleSection": rotulo,
         "author": {"@type": "Person", "name": "Dr. Henrique Figueiredo", "url": DOM + '/sobre/', "jobTitle": "Médico ortopedista e cirurgião da mão",
                    "identifier": "CRM-SP 199832"},
         "reviewedBy": {"@type": "Person", "name": "Dr. Henrique Figueiredo", "url": DOM + '/sobre/'},
         "lastReviewed": p['date'], "publisher": {"@id": DOM + '/#medico'},
         "about": {"@type": "MedicalCondition", "name": p.get('condition', p['title'])},
         "keywords": ', '.join(p.get('keywords', []))}]
    if p.get('refs'):
        ld[1]['citation'] = [r['text'] for r in p['refs']]
    if p.get('faq'):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q['q'], "acceptedAnswer": {"@type": "Answer", "text": q['a']}} for q in p['faq']]})
    jsonld = '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)

    head = cab.split('<meta name="viewport"', 1)[0]
    corpo_cab = '<body>' + cab.split('<body>', 1)[1]
    metas = f'''<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo_seo)}</title>
<meta name="description" content="{e(p['description'])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0E1E3A">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="article">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Dr. Henrique Figueiredo">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="600">
<meta property="og:image:alt" content="{e(p['title'])}">
<meta property="article:published_time" content="{pub}">
<meta property="article:author" content="Dr. Henrique Figueiredo">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(p['title'])}">
<meta name="twitter:description" content="{e(p['description'])}">
<meta name="twitter:image" content="{img}">
<link rel="alternate" type="application/rss+xml" title="Blog do Dr. Henrique Figueiredo" href="/blog/feed.xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
{jsonld}
</head>
'''
    faq_html = ''
    if p.get('faq'):
        faq_html = '<h2>Perguntas frequentes</h2>\n' + '\n'.join(
            f'<h3>{e(q["q"])}</h3>\n<p>{e(q["a"])}</p>' for q in p['faq'])
    refs_html = ''
    if p.get('refs'):
        itens = ''.join(
            f'<li>{e(r["text"])}' + (f' <a href="{e(r["url"])}" target="_blank" rel="noopener nofollow">Acessar</a>' if r.get('url') else '') + '</li>'
            for r in p['refs'])
        refs_html = f'<h2>Referências</h2>\n<ol class="refs">{itens}</ol>'
    mesmos = [x for x in todos if x['slug'] != p['slug'] and x['date'] <= p['date']]
    rel = [x for x in mesmos if x['topic'] == p['topic']][:3]
    rel += [x for x in mesmos if x not in rel][:3 - len(rel)]
    webp = p['img'].rsplit('.', 1)[0] + '.webp'
    main = f'''<main id="conteudo">

<article class="post">
  <header class="post-head">
    <div class="wrap">
      <nav aria-label="Você está em"><ol class="crumbs"><li><a href="/">Início</a></li><li><a href="/blog/">Blog</a></li><li aria-current="page">{e(p['title'])}</li></ol></nav>
      <div class="post-head-inner">
        <span class="post-meta"><a class="topic" href="/blog/#{p['topic']}">{rotulo}</a><time datetime="{p['date']}">{data_br(p['date'])}</time><span>{p.get('read_min', 4)} min de leitura</span></span>
        <h1>{e(p['title'])}</h1>
        <p class="byline"><img src="/assets/img/dr-henrique-retrato.jpg" alt="" width="44" height="44" loading="lazy"><span>Por <a href="/sobre/">Dr. Henrique Figueiredo</a>, ortopedista e cirurgião da mão · CRM-SP 199.832</span></p>
      </div>
    </div>
  </header>
  <div class="wrap">
    <figure class="post-cover"><picture><source srcset="{webp}" type="image/webp"><img src="{p['img']}" alt="{e(p['title'])}" width="1200" height="600" fetchpriority="high"></picture></figure>
    <div class="post-body">
{p['body_html'].strip()}
{faq_html}
{refs_html}
    </div>
    <div class="post-sign"><img class="signature" src="/assets/img/assinatura-azul.png" alt="Assinatura do Dr. Henrique Figueiredo" width="239" height="248" loading="lazy"></div>
    <aside class="post-author" aria-label="Sobre o autor">
      <img src="/assets/img/dr-henrique-jaleco.jpg" alt="Dr. Henrique Figueiredo" width="120" height="120" loading="lazy">
      <div>
        <p class="pa-name">Dr. Henrique Figueiredo</p>
        <p>Especialista em Ortopedia e Traumatologia e Cirurgia da Mão, com atuação em Medicina Regenerativa e Intervenção em Dor, em Campinas. CRM-SP 199.832 · RQE 102783 · RQE 124871.</p>
        <div class="pa-actions"><a class="btn btn-navy" href="{WA}" target="_blank" rel="noopener">Agendar avaliação</a><a class="text-link" href="{area_url}">Conheça: {area_nome}</a></div>
      </div>
    </aside>
    <p class="post-disclaimer">Conteúdo informativo. Não substitui a consulta médica, o diagnóstico ou o tratamento individualizado.</p>
  </div>
</article>
<section class="section section-mist">
  <div class="wrap">
    <div class="section-head"><h2>Continue lendo</h2><p><a class="text-link" href="/blog/">Ver todos os artigos</a></p></div>
    <div class="posts">{''.join(card(x) for x in rel)}</div>
  </div>
</section>
<section class="cta-band on-navy">
  <img class="mono" src="/assets/img/assinatura-branca.png" alt="" width="205" height="211" loading="lazy">
  <div class="wrap">
    <div><h2>Agende sua avaliação</h2><p>Se você apresenta dores persistentes, limitações de movimento ou deseja uma avaliação especializada, agende uma consulta. O primeiro passo para um tratamento adequado é compreender o que está acontecendo com o seu corpo.</p></div>
    <a class="btn btn-gold" href="{WA}" target="_blank" rel="noopener">Agendar pelo WhatsApp</a>
  </div>
</section>
</main>'''
    return head + metas + corpo_cab + main + rodape


def refazer_blog_index(todos):
    p = os.path.join(SITE, 'blog', 'index.html')
    t = ler(p)
    dest = todos[0]
    webp = dest['img'].rsplit('.', 1)[0] + '.webp'
    featured = (f'<a class="featured" id="destaque" href="/blog/{dest["slug"]}/">\n      <div>\n'
                f'        <span class="post-meta"><span class="topic">{TEMAS[dest["topic"]][0]}</span><time datetime="{dest["date"]}">{data_br(dest["date"])}</time><span>Mais recente</span></span>\n'
                f'        <h2>{e(dest["title"])}</h2>\n        <p class="lead">{e(dest["excerpt"])}</p>\n        <span class="text-link">Ler artigo</span>\n      </div>\n'
                f'      <div class="featured-img"><picture><source srcset="{webp}" type="image/webp"><img src="{dest["img"]}" alt="" width="800" height="400"></picture></div>\n    </a>')
    cont = {k: sum(1 for x in todos if x['topic'] == k) for k in ORDEM_TEMAS}
    filtros = (f'<div class="filters" role="group" aria-label="Filtrar artigos por tema"><button type="button" data-topic="todos" aria-pressed="true">Todos<span class="count">{len(todos)}</span></button>'
               + ''.join(f'<button type="button" data-topic="{k}" aria-pressed="false">{TEMAS[k][0]}<span class="count">{cont[k]}</span></button>' for k in ORDEM_TEMAS if cont[k])
               + '</div>')
    lista = '<ul class="blog-list">' + ''.join(
        f'<li data-topic="{x["topic"]}"' + (' data-feat="1" hidden' if i == 0 else '') + f'>{card(x, "h2")}</li>' for i, x in enumerate(todos)) + '</ul>'
    novo = re.sub(r'<a class="featured".*?</ul>', lambda m: featured + '\n    ' + filtros + '\n    ' + lista, t, count=1, flags=re.S)
    if '/blog/feed.xml' not in novo:
        novo = novo.replace('<link rel="icon"', '<link rel="alternate" type="application/rss+xml" title="Blog do Dr. Henrique Figueiredo" href="/blog/feed.xml">\n<link rel="icon"', 1)
    return gravar(p, novo)


def refazer_home(todos):
    p = os.path.join(SITE, 'index.html')
    t = ler(p)
    i = t.find('<div class="posts">', t.find('Ver todos os artigos'))
    if i < 0:
        return False
    j = t.find('</div>', t.rfind('</a>', i, t.find('</section>', i))) + len('</div>')
    novo = t[:i] + '<div class="posts">' + ''.join(card(x) for x in todos[:3]) + '</div>' + t[j:]
    return gravar(p, novo)


def refazer_sitemap(todos, hoje):
    p = os.path.join(SITE, 'sitemap.xml')
    t = ler(p)
    t = re.sub(r'\s*<url><loc>https://drhenriquefigueiredo\.com\.br/blog/[^<]+/</loc>.*?</url>', '', t)
    ult = max(x.get('modified', x['date']) for x in todos)
    m = re.search(r'<loc>https://drhenriquefigueiredo\.com\.br/blog/</loc><lastmod>([\d-]+)', t)
    if m and m.group(1) < ult:
        t = t.replace(m.group(0), m.group(0)[:-len(m.group(1))] + ult)
    blog = ''.join(f'\n  <url><loc>{DOM}/blog/{x["slug"]}/</loc><lastmod>{x.get("modified", x["date"])}</lastmod><changefreq>yearly</changefreq><priority>0.6</priority></url>' for x in todos)
    t = t.replace(f'<loc>{DOM}/blog/</loc>', f'<loc>{DOM}/blog/</loc>', 1)
    k = t.find('</url>', t.find(f'<loc>{DOM}/blog/</loc>')) + len('</url>')
    return gravar(p, t[:k] + blog + t[k:])


def refazer_llms(todos):
    p = os.path.join(SITE, 'llms.txt')
    t = ler(p)
    linhas = t.split('\n')
    linhas = [l for l in linhas if not l.startswith(f'- [') or f'({DOM}/blog/' not in l or l.find(f'({DOM}/blog/)') >= 0]
    t = '\n'.join(linhas)
    bloco = '## Artigos do blog\n\n' + '\n'.join(f'- [{x["title"]}]({DOM}/blog/{x["slug"]}/): {x["description"]}' for x in todos) + '\n'
    if '## Artigos do blog' in t:
        t = re.sub(r'## Artigos do blog\n.*?(?=\n## |\Z)', bloco, t, flags=re.S)
    else:
        t = t.replace('## Contato e perfis oficiais', bloco + '\n## Contato e perfis oficiais', 1)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return gravar(p, t)


def refazer_feed(todos):
    itens = ''.join(f'''
  <item>
    <title>{e(x["title"])}</title>
    <link>{DOM}/blog/{x["slug"]}/</link>
    <guid isPermaLink="true">{DOM}/blog/{x["slug"]}/</guid>
    <pubDate>{dt.datetime.fromisoformat(x["date"] + "T09:00:00-03:00").strftime("%a, %d %b %Y %H:%M:%S -0300")}</pubDate>
    <category>{TEMAS[x["topic"]][0]}</category>
    <description>{e(x["description"])}</description>
    <enclosure url="{DOM}{x["img"]}" type="image/jpeg" length="0"/>
  </item>''' for x in todos[:50])
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Blog do Dr. Henrique Figueiredo</title>
  <link>{DOM}/blog/</link>
  <atom:link href="{DOM}/blog/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Artigos sobre ortopedia, cirurgia da mão, dor e medicina regenerativa, escritos pelo Dr. Henrique Figueiredo, médico ortopedista em Campinas (CRM-SP 199.832).</description>
  <language>pt-BR</language>{itens}
</channel>
</rss>
'''
    return gravar(os.path.join(SITE, 'blog', 'feed.xml'), feed)


def refazer_redes(todos):
    """Feed só dos artigos novos, para a automação do Instagram/Facebook (Make):
    descrição = legenda pronta do Instagram; imagem = arte 1080x1350."""
    novos = [x for x in todos if not x.get('legacy') and x.get('instagram')][:20]
    itens = ''.join(f'''
  <item>
    <title>{e(x["title"])}</title>
    <link>{DOM}/blog/{x["slug"]}/</link>
    <guid isPermaLink="false">redes-{x["slug"]}</guid>
    <pubDate>{dt.datetime.fromisoformat(x["date"] + "T06:00:00-03:00").strftime("%a, %d %b %Y %H:%M:%S -0300")}</pubDate>
    <description>{e(x["instagram"])}</description>
    <enclosure url="{DOM}/assets/social/ig-{x["slug"]}.jpg" type="image/jpeg" length="0"/>
  </item>''' for x in novos)
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Redes: Blog do Dr. Henrique Figueiredo</title>
  <link>{DOM}/blog/</link>
  <description>Legendas e artes dos artigos novos para Instagram e Facebook.</description>
  <language>pt-BR</language>{itens}
</channel>
</rss>
'''
    return gravar(os.path.join(SITE, 'blog', 'redes.xml'), feed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hoje')
    ap.add_argument('--previa')
    a = ap.parse_args()
    hoje = a.hoje or dt.datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()
    todos, novos = carregar(hoje, a.previa)
    molde = ler(os.path.join(SITE, 'blog', 'tunel-do-carpo-causas-sintomas-e-quando-a-cirurgia-e-indicada', 'index.html'))
    mudou = []
    for p in novos:
        if gravar(os.path.join(SITE, 'blog', p['slug'], 'index.html'), pagina_artigo(p, todos, molde)):
            mudou.append(p['slug'])
    for nome, f in [('blog', lambda: refazer_blog_index(todos)), ('home', lambda: refazer_home(todos)),
                    ('sitemap', lambda: refazer_sitemap(todos, hoje)), ('llms', lambda: refazer_llms(todos)), ('feed', lambda: refazer_feed(todos)), ('redes', lambda: refazer_redes(todos))]:
        if f():
            mudou.append(nome)
    publicados_hoje = [p['slug'] for p in novos if p['date'] == hoje and p.get('status') == 'aprovado']
    print(json.dumps({'hoje': hoje, 'alterados': mudou, 'publicados_hoje': publicados_hoje, 'total_artigos': len(todos)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
