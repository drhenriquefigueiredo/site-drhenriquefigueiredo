#!/usr/bin/env python3
"""Opções de imagem (fotos reais do Pexels) para escolher antes de montar as capas.

content/capas/candidatas/pedidos.json = [{"slug", "ids": [pexels_id, ...]}, ...]
  -> grava content/capas/candidatas/<slug>-p<id>.jpg (1280 px de largura) para conferência.
A escolhida vai para o pedido da capa como "pexels_id".
"""
import json, os, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(os.path.dirname(AQUI), 'content', 'capas', 'candidatas')
H = {'User-Agent': 'Mozilla/5.0 (drhenriquefigueiredo-capas)'}


def main():
    for p in json.load(open(os.path.join(PASTA, 'pedidos.json'), encoding='utf-8')):
        for pid in p.get('ids', []):
            destino = os.path.join(PASTA, f"{p['slug']}-p{pid}.jpg")
            if os.path.exists(destino):
                continue
            url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1280"
            try:
                open(destino, 'wb').write(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60).read())
                print('ok', p['slug'], pid, flush=True)
            except Exception as e:
                print('falhou', p['slug'], pid, e, flush=True)


if __name__ == '__main__':
    main()
