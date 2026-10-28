#!/usr/bin/env python3
"""Feed das redes sociais (Instagram; o Facebook recebe por compartilhamento do Instagram).

Gera content/redes/feed.xml, lido pelo Make todo dia às 8h. Fica FORA de site/ e é servido pelo
GitHub (raw.githubusercontent.com), então publicar nas redes não gasta créditos da Netlify.

Por dia: no máximo 1 publicação no feed (artigo, post ou carrossel; o artigo tem prioridade) e 1 story.
  - artigos aprovados de content/posts/ com data <= hoje -> legenda "instagram", arte content/capas/ig-<slug>.jpg
  - itens aprovados de content/redes/fila/*.json com data <= hoje:
      {"date", "id", "tipo": "post" | "carrossel" | "story", "title", "topic", "caption"}
      post -> content/capas/ig-<id>.jpg · carrossel -> content/capas/car-<id>-NN.jpg · story -> content/capas/story-<id>.jpg
Cada item leva <category> (foto | carrossel | story) e o carrossel tem sempre 7 imagens (capa + 5 + final), e um <enclosure> por imagem (o carrossel tem várias).
Um item só entra quando as artes existem (geradas pelo workflow "Gerar capas com IA").
"""
import datetime as dt, glob, json, os, sys
from xml.sax.saxutils import escape as e
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CONTENT = os.path.join(RAIZ, 'content')
RAW = 'https://raw.githubusercontent.com/drhenriquefigueiredo/site-drhenriquefigueiredo/main/'
DOM = 'https://drhenriquefigueiredo.com.br'
# rótulo lido pelo filtro do Make: rota 1 = foto (post simples ou arte de artigo), rota 2 = carrossel (exatamente 7 imagens)
CATEGORIA = {'post': 'foto', 'carrossel': 'carrossel', 'story': 'story'}


def imagens(q):
    """Arquivos (relativos à raiz) de um item da fila, em ordem."""
    t, i = q.get('tipo', 'post'), q['id']
    if t == 'carrossel':
        return sorted(os.path.relpath(f, RAIZ) for f in glob.glob(os.path.join(CONTENT, 'capas', f'car-{i}-*.jpg')))
    if t == 'story':
        return [f'content/capas/story-{i}.jpg']
    return [f'content/capas/ig-{i}.jpg']


def itens(hoje):
    feed, stories = {}, {}
    for f in sorted(glob.glob(os.path.join(CONTENT, 'posts', '*.json'))):
        p = json.load(open(f, encoding='utf-8'))
        if p.get('status') == 'aprovado' and p['date'] <= hoje and p.get('instagram'):
            img = f"content/capas/ig-{p['slug']}.jpg"
            if os.path.exists(os.path.join(RAIZ, img)):
                feed[p['date']] = {'guid': f"redes-{p['slug']}", 'date': p['date'], 'tipo': 'post', 'title': p['title'],
                                   'link': f"{DOM}/blog/{p['slug']}/", 'caption': p['instagram'], 'imgs': [img]}
    for f in sorted(glob.glob(os.path.join(CONTENT, 'redes', 'fila', '*.json'))):
        q = json.load(open(f, encoding='utf-8'))
        tipo = q.get('tipo', 'post')
        if q.get('date', '9999') > hoje or (tipo != 'story' and not q.get('caption')):
            continue
        alvo = stories if tipo == 'story' else feed
        dia = q['date']
        while dia in alvo and dia < hoje:  # dia ocupado: vai para o próximo dia livre
            dia = (dt.date.fromisoformat(dia) + dt.timedelta(days=1)).isoformat()
        if dia in alvo:
            continue
        imgs = imagens(q)
        if imgs and all(os.path.exists(os.path.join(RAIZ, x)) for x in imgs) and (tipo != 'carrossel' or len(imgs) == 7):
            alvo[dia] = {'guid': f"{tipo}-{q['id']}", 'date': dia, 'tipo': tipo, 'title': q.get('title', ''),
                         'link': f"{DOM}/", 'caption': q.get('caption', ''), 'imgs': imgs}
    todos = list(feed.values()) + list(stories.values())
    todos.sort(key=lambda x: (x['date'], x['tipo'] != 'story'), reverse=True)
    return todos[:30]


def item_xml(x):
    anexos = ''.join(f'\n    <enclosure url="{RAW}{img}" type="image/jpeg" length="{os.path.getsize(os.path.join(RAIZ, img))}"/>'
                     for img in x['imgs'])
    data = dt.datetime.fromisoformat(x['date'] + 'T06:00:00-03:00').strftime('%a, %d %b %Y %H:%M:%S -0300')
    return f'''
  <item>
    <title>{e(x["title"])}</title>
    <link>{x["link"]}</link>
    <guid isPermaLink="false">{x["guid"]}</guid>
    <pubDate>{data}</pubDate>
    <category>{CATEGORIA[x["tipo"]]}</category>
    <description>{e(x["caption"])}</description>{anexos}
  </item>'''


def main():
    hoje = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()
    lista = itens(hoje)
    corpo = ''.join(item_xml(x) for x in lista)
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Redes: Dr. Henrique Figueiredo</title>
  <link>{DOM}/</link>
  <description>Publicações aprovadas para o Instagram: até 1 no feed (post ou carrossel) e 1 story por dia.</description>
  <language>pt-BR</language>{corpo}
</channel>
</rss>
'''
    destino = os.path.join(CONTENT, 'redes', 'feed.xml')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    antes = open(destino, encoding='utf-8').read() if os.path.exists(destino) else None
    if antes != feed:
        open(destino, 'w', encoding='utf-8').write(feed)
    print(json.dumps({'feed_mudou': antes != feed, 'itens': len(lista)}))


if __name__ == '__main__':
    main()
