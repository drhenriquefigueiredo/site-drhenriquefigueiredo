#!/usr/bin/env python3
"""Prepara um artigo aprovado para publicação (usado pela tarefa diária).

preparar.py --linha ARQUIVO.json --data AAAA-MM-DD
  ARQUIVO.json: a linha do artigo na página de aprovação (campos do artigo).
  --data: dia em que ele vai ao ar (o dia de publicação de hoje).
Grava content/posts/<data>-<slug>.json com status "aprovado" e gera as capas
em content/capas/. Não mexe em site/: quem publica é o tools/build.py, rodado
pelo GitHub Actions logo depois do push (uma única atualização do site).
"""
import argparse, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CAMPOS = ['date', 'topic', 'slug', 'title', 'seo_title', 'description', 'excerpt', 'keywords', 'condition',
          'body_html', 'faq', 'refs', 'gbp', 'instagram']
ROTULO = {'mao': 'Mão e punho', 'ortopedia': 'Ortopedia', 'dor': 'Dor', 'regenerativa': 'Medicina regenerativa',
          'esporte': 'Lesões e esporte'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--linha', required=True)
    ap.add_argument('--data', required=True)
    a = ap.parse_args()
    linha = json.load(open(a.linha, encoding='utf-8'))
    linha = linha.get('data', linha)
    falta = [c for c in ['topic', 'slug', 'title', 'description', 'excerpt', 'body_html'] if not linha.get(c)]
    if falta:
        sys.exit(f'Linha incompleta, faltam: {falta}')
    post = {c: linha.get(c) for c in CAMPOS if c in linha}
    post['date'] = a.data
    post['status'] = 'aprovado'
    destino = os.path.join(RAIZ, 'content', 'posts', f"{a.data}-{post['slug']}.json")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    json.dump(post, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(AQUI, 'capa.py'), '--slug', post['slug'], '--titulo', post['title'],
                    '--tema', ROTULO[post['topic']], '--saida', os.path.join(RAIZ, 'content', 'capas')], check=True)
    print(json.dumps({'post': os.path.relpath(destino, RAIZ), 'slug': post['slug']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
