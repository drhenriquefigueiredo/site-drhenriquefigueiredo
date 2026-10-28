#!/usr/bin/env python3
"""Publica o story do dia no Instagram pela API oficial da Meta (Graph API), de graça.

O Make gratuito publica foto e carrossel, mas não tem módulo de story. Este script cobre o story:
lê content/redes/feed.xml (gerado por tools/redes.py), pega os itens <category>story</category>
com data <= hoje que ainda não foram publicados e publica cada um como story.

Precisa de dois segredos no GitHub (Settings > Secrets and variables > Actions):
  IG_USER_ID  ID da conta profissional do Instagram (ex.: 17841400171723702)
  IG_TOKEN    token de acesso que não expira (usuário do sistema do Meta Business, permissões
              instagram_basic, instagram_content_publish, pages_show_list, pages_read_engagement)
Sem os segredos o script só avisa e sai sem erro: nada quebra.

Controle: content/redes/stories_publicados.json guarda os guid já publicados (nunca repete).
"""
import datetime as dt, json, os, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FEED = os.path.join(RAIZ, 'content', 'redes', 'feed.xml')
FEITOS = os.path.join(RAIZ, 'content', 'redes', 'stories_publicados.json')
API = 'https://graph.facebook.com/v21.0'


def chamar(caminho, dados):
    corpo = urllib.parse.urlencode(dados).encode()
    with urllib.request.urlopen(urllib.request.Request(f'{API}/{caminho}', data=corpo), timeout=120) as r:
        return json.load(r)


def status(cid, token):
    q = urllib.parse.urlencode({'fields': 'status_code', 'access_token': token})
    with urllib.request.urlopen(f'{API}/{cid}?{q}', timeout=60) as r:
        return json.load(r).get('status_code')


def main():
    uid, token = os.environ.get('IG_USER_ID'), os.environ.get('IG_TOKEN')
    if not (uid and token):
        print('Stories: segredos IG_USER_ID/IG_TOKEN ainda não configurados; nada a fazer.')
        return
    lanc = json.load(open(os.path.join(RAIZ, 'content', 'lancamento.json'), encoding='utf-8'))
    if not lanc.get('iniciado'):
        print('Stories: modo de preparação (content/lancamento.json); nada é publicado.')
        return
    hoje = dt.datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    feitos = json.load(open(FEITOS)) if os.path.exists(FEITOS) else []
    novos = 0
    for it in ET.parse(FEED).getroot().iter('item'):
        if (it.findtext('category') or '') != 'story':
            continue
        guid = it.findtext('guid')
        data = dt.datetime.strptime(it.findtext('pubDate'), '%a, %d %b %Y %H:%M:%S %z').date()
        if guid in feitos or data > hoje or (hoje - data).days > 2:
            continue
        url = it.find('enclosure').get('url')
        try:
            cid = chamar(f'{uid}/media', {'image_url': url, 'media_type': 'STORIES', 'access_token': token})['id']
            for _ in range(20):
                if status(cid, token) == 'FINISHED':
                    break
                time.sleep(6)
            chamar(f'{uid}/media_publish', {'creation_id': cid, 'access_token': token})
        except urllib.error.HTTPError as e:
            print(f'Stories: falha em {guid}: {e.code} {e.read()[:300]!r}')
            sys.exit(1)
        feitos.append(guid)
        novos += 1
        print(f'Story publicado: {guid}')
    json.dump(feitos[-200:], open(FEITOS, 'w'), indent=0)
    print(json.dumps({'stories_publicados': novos}))


if __name__ == '__main__':
    main()
