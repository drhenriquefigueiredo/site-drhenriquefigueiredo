#!/usr/bin/env python3
"""Rede de segurança antes de publicar: todo artigo em content/posts/ precisa das capas em content/capas/.

Se faltar blog-<slug>.jpg ou ig-<slug>.jpg, monta as capas com tools/capa.py usando a imagem de IA
(content/capas/ia-<slug>.jpg) se existir, ou o fundo gráfico navy/dourado se não existir.
Também aceita o JSON exatamente como vem da página de aprovação ({"data": {...}}) e o normaliza.
"""
import glob, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CAPAS = os.path.join(RAIZ, 'content', 'capas')
CAMPOS = ['date', 'topic', 'slug', 'title', 'seo_title', 'description', 'excerpt', 'keywords', 'condition',
          'body_html', 'faq', 'refs', 'gbp', 'instagram', 'status']
ROTULO = {'mao': 'Mão e punho', 'ortopedia': 'Ortopedia', 'dor': 'Dor', 'regenerativa': 'Medicina regenerativa',
          'esporte': 'Lesões e esporte'}


def main():
    for f in sorted(glob.glob(os.path.join(RAIZ, 'content', 'posts', '*.json'))):
        post = json.load(open(f, encoding='utf-8'))
        if 'data' in post and isinstance(post['data'], dict) and 'slug' not in post:
            post = post['data']
            post = {c: post[c] for c in CAMPOS if c in post}
            json.dump(post, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f'normalizado {os.path.basename(f)}')
        slug = post.get('slug')
        if not slug or post.get('status') != 'aprovado':
            continue
        if all(os.path.exists(os.path.join(CAPAS, n)) for n in (f'blog-{slug}.jpg', f'blog-{slug}.webp', f'ig-{slug}.jpg')):
            continue
        subprocess.run([sys.executable, os.path.join(AQUI, 'capa.py'), '--slug', slug, '--titulo', post['title'],
                        '--tema', ROTULO.get(post.get('topic'), 'Ortopedia'), '--saida', CAPAS], check=True)
        print(f'capas montadas na hora: {slug}')


if __name__ == '__main__':
    main()
