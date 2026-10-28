#!/usr/bin/env python3
"""Gera várias opções de imagem para escolher a melhor antes de montar as capas.

Lê content/capas/candidatas/pedidos.json = [{"slug", "prompt", "seeds": [1, 2, 3]}, ...]
e grava content/capas/candidatas/<slug>-<seed>.jpg (FLUX via pollinations, gratuito).
A escolhida vira content/capas/ia-<slug>.jpg (com "seed" no pedido); as demais são apagadas.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ia_imagem as ia

PASTA = os.path.join(ia.CAPAS, 'candidatas')


def main():
    lista = json.load(open(os.path.join(PASTA, 'pedidos.json'), encoding='utf-8'))
    for p in lista:
        for seed in p.get('seeds', [1, 2, 3]):
            destino = os.path.join(PASTA, f"{p['slug']}-{seed}.jpg")
            if os.path.exists(destino):
                continue
            q = dict(p, slug=f"__tmp-{p['slug']}", seed=seed)
            if ia.pollinations(q):
                os.replace(os.path.join(ia.CAPAS, f"ia-{q['slug']}.jpg"), destino)


if __name__ == '__main__':
    main()
