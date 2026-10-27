#!/usr/bin/env python3
"""Feed das redes sociais (Instagram; o Facebook recebe por compartilhamento do Instagram).

Gera content/redes/feed.xml, lido pelo Make todo dia às 8h. Fica FORA de site/ e é servido pelo
GitHub (raw.githubusercontent.com), então publicar nas redes não gasta créditos da Netlify.

Itens (no máximo 1 por dia; o artigo do dia tem prioridade):
  - artigos aprovados de content/posts/ com data <= hoje  -> legenda = campo "instagram", arte = content/capas/ig-<slug>.jpg
  - posts aprovados de content/redes/fila/*.json com data <= hoje:
      {"date", "id", "tipo": "post", "title", "topic", "caption"}  -> arte = content/capas/ig-<id>.jpg
Um item só entra quando a arte existe (gerada pelo workflow "Gerar capas com IA").
"""
import datetime as dt, glob, json, os, sys
from xml.sax.saxutils import escape as e
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CONTENT = os.path.join(RAIZ, 'content')
RAW = 'https://raw.githubusercontent.com/drhenriquefigueiredo/site-drhenriquefigueiredo/main/'
DOM = 'https://drhenriquefigueiredo.com.br'


def itens(hoje):
    por_dia = {}
    for f in sorted(glob.glob(os.path.join(CONTENT, 'posts', '*.json'))):
        p = json.load(open(f, encoding='utf-8'))
        if p.get('status') == 'aprovado' and p['date'] <= hoje and p.get('instagram'):
            img = f"content/capas/ig-{p['slug']}.jpg"
            if os.path.exists(os.path.join(RAIZ, img)):
                por_dia[p['date']] = {'guid': f"redes-{p['slug']}", 'date': p['date'], 'title': p['title'],
                                      'link': f"{DOM}/blog/{p['slug']}/", 'caption': p['instagram'], 'img': img}
    for f in sorted(glob.glob(os.path.join(CONTENT, 'redes', 'fila', '*.json'))):
        q = json.load(open(f, encoding='utf-8'))
        if q.get('date', '9999') > hoje or not q.get('caption'):
            continue
        dia = q['date']
        while dia in por_dia and dia < hoje:  # dia ocupado por artigo: vai para o próximo dia livre
            dia = (dt.date.fromisoformat(dia) + dt.timedelta(days=1)).isoformat()
        if dia in por_dia:
            continue
        img = f"content/capas/ig-{q['id']}.jpg"
        if os.path.exists(os.path.join(RAIZ, img)):
            por_dia[dia] = {'guid': f"post-{q['id']}", 'date': dia, 'title': q.get('title', ''),
                                  'link': f"{DOM}/blog/", 'caption': q['caption'], 'img': img}
    return [por_dia[d] for d in sorted(por_dia, reverse=True)][:20]


def main():
    hoje = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()
    corpo = ''.join(f'''
  <item>
    <title>{e(x["title"])}</title>
    <link>{x["link"]}</link>
    <guid isPermaLink="false">{x["guid"]}</guid>
    <pubDate>{dt.datetime.fromisoformat(x["date"] + "T06:00:00-03:00").strftime("%a, %d %b %Y %H:%M:%S -0300")}</pubDate>
    <description>{e(x["caption"])}</description>
    <enclosure url="{RAW}{x["img"]}" type="image/jpeg" length="{os.path.getsize(os.path.join(RAIZ, x["img"]))}"/>
  </item>''' for x in itens(hoje))
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Redes: Dr. Henrique Figueiredo</title>
  <link>{DOM}/</link>
  <description>Legendas e artes aprovadas para o Instagram (1 por dia).</description>
  <language>pt-BR</language>{corpo}
</channel>
</rss>
'''
    destino = os.path.join(CONTENT, 'redes', 'feed.xml')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    antes = open(destino, encoding='utf-8').read() if os.path.exists(destino) else None
    if antes != feed:
        open(destino, 'w', encoding='utf-8').write(feed)
    print(json.dumps({'feed_mudou': antes != feed, 'itens': corpo.count('<item>')}))


if __name__ == '__main__':
    main()
