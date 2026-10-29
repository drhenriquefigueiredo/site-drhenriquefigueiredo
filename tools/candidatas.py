#!/usr/bin/env python3
"""Opções de imagem para escolher antes de montar as capas.

content/capas/candidatas/pedidos.json = [{"slug", "busca": "termos em inglês"}, ...]
  -> busca no Pexels (fotos reais, uso comercial livre; segredo PEXELS_API_KEY) e grava as 8 primeiras
     como content/capas/candidatas/<slug>-p<id>.jpg (miniaturas) + <slug>.json (dados das fotos).
A escolhida vai para o pedido da capa como "pexels_id" (e "centro" [x, y] se precisar ajustar o recorte).
"""
import json, os, sys, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(os.path.dirname(AQUI), 'content', 'capas', 'candidatas')


def main():
    chave = os.environ.get('PEXELS_API_KEY')
    if not chave:
        sys.exit('Falta o segredo PEXELS_API_KEY no GitHub.')
    h = {'Authorization': chave, 'User-Agent': 'drhenriquefigueiredo-capas/1.0'}
    for p in json.load(open(os.path.join(PASTA, 'pedidos.json'), encoding='utf-8')):
        if not p.get('busca'):
            continue
        q = urllib.parse.urlencode({'query': p['busca'], 'per_page': p.get('quantas', 8), 'orientation': 'landscape'})
        r = json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.pexels.com/v1/search?{q}', headers=h), timeout=60))
        info = []
        for f in r.get('photos', []):
            destino = os.path.join(PASTA, f"{p['slug']}-p{f['id']}.jpg")
            if not os.path.exists(destino):
                open(destino, 'wb').write(urllib.request.urlopen(urllib.request.Request(f['src']['medium'], headers=h), timeout=60).read())
            info.append({'id': f['id'], 'fotografo': f.get('photographer'), 'alt': f.get('alt'), 'url': f.get('url')})
        json.dump(info, open(os.path.join(PASTA, f"{p['slug']}.json"), 'w'), ensure_ascii=False, indent=1)
        print(p['slug'], len(info), 'fotos')


if __name__ == '__main__':
    main()
