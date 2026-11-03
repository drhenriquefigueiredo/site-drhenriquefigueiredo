#!/usr/bin/env python3
"""Publica no Threads, pela API oficial e gratuita, o mesmo post aprovado do Instagram.

Lê content/redes/feed.xml (gerado por tools/redes.py), pega os itens de feed (foto ou carrossel, não story)
com data de hoje (ou dos 2 dias anteriores, se algum ficou para trás) que ainda não foram para o Threads,
adapta a legenda ao limite de 500 caracteres do Threads (tira as hashtags, corta numa frase inteira e,
se for artigo, termina com o link do blog) e publica a imagem ou o carrossel.

Segredos no GitHub (Settings > Secrets and variables > Actions):
  THREADS_USER_ID  (opcional) ID do perfil do Threads; sem ele usa o dono do token
  THREADS_TOKEN    token de longa duração (60 dias), permissões threads_basic e threads_content_publish
  THREADS_CHAVE    senha qualquer, só para guardar o token renovado de forma cifrada
O token é renovado sozinho a cada 7 dias e fica cifrado em content/redes/threads_token.enc
(o repositório é público; sem a THREADS_CHAVE o arquivo não serve para nada).
Sem os segredos o script só avisa e sai sem erro: nada quebra.

Controle: content/redes/threads_publicados.json guarda os guid já publicados (nunca repete).
Uso: python3 tools/threads.py [--teste]   (--teste mostra o que sairia, sem publicar)
"""
import datetime as dt, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
REDES = os.path.join(RAIZ, 'content', 'redes')
FEED = os.path.join(REDES, 'feed.xml')
FEITOS = os.path.join(REDES, 'threads_publicados.json')
COFRE = os.path.join(REDES, 'threads_token.enc')
API = 'https://graph.threads.net/v1.0'
LIMITE = 500


def texto_threads(legenda, link):
    """Legenda do Instagram -> texto do Threads (até 500 caracteres)."""
    linhas = [l for l in legenda.splitlines() if not re.fullmatch(r'\s*(#[\wÀ-ÿ]+\s*)+', l)]
    corpo = re.sub(r'(\s#[\wÀ-ÿ]+)+\s*$', '', '\n'.join(linhas)).strip()
    corpo = re.sub(r'\n{3,}', '\n\n', corpo)
    # CFM: publicidade médica sempre com CRM e RQE -> a linha de assinatura nunca é cortada
    assin = next((l.strip() for l in linhas if 'CRM' in l), 'Dr. Henrique Figueiredo | CRM-SP 199832 | RQE 102783/124871')
    corpo = '\n'.join(l for l in corpo.splitlines() if 'CRM' not in l).strip()
    fim = f'\n\nLeia o artigo completo: {link}' if '/blog/' in (link or '') else ''
    fim += f'\n\n{assin}'
    cabe = LIMITE - len(fim)
    if len(corpo) > cabe:
        trecho = corpo[:cabe]
        corte = max(trecho.rfind('. '), trecho.rfind('! '), trecho.rfind('? '), trecho.rfind('.\n'))
        corpo = trecho[:corte + 1] if corte > cabe * 0.5 else trecho[:trecho.rfind(' ')].rstrip(',;:') + '…'
    return (corpo + fim).strip()


def http(metodo, caminho, dados):
    q = urllib.parse.urlencode(dados)
    if metodo == 'GET':
        req = urllib.request.Request(f'{API}/{caminho}?{q}')
    else:
        req = urllib.request.Request(f'{API}/{caminho}', data=q.encode())
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def openssl(args, entrada):
    return subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-a', '-A', '-pass', 'env:THREADS_CHAVE'] + args,
                          input=entrada.encode(), capture_output=True, check=True).stdout.decode()


def token_atual():
    """Token mais novo (cofre cifrado, se houver) e renovação a cada 7 dias."""
    token, renovado = os.environ['THREADS_TOKEN'], None
    chave = os.environ.get('THREADS_CHAVE')
    if chave and os.path.exists(COFRE):
        try:
            salvo = json.loads(openssl(['-d'], open(COFRE).read().strip()))
            token, renovado = salvo['token'], salvo['renovado']
        except Exception as e:
            print(f'Threads: cofre ilegível ({e}); usando o THREADS_TOKEN.')
    hoje = dt.date.today()
    if chave and (not renovado or (hoje - dt.date.fromisoformat(renovado)).days >= 7):
        try:
            novo = http('GET', 'refresh_access_token', {'grant_type': 'th_refresh_token', 'access_token': token})
            token = novo['access_token']
            open(COFRE, 'w').write(openssl([], json.dumps({'token': token, 'renovado': hoje.isoformat()})) + '\n')
            print('Threads: token renovado.')
        except urllib.error.HTTPError as e:
            print(f'Threads: não renovou o token: {e.code} {e.read()[:200]!r}')
    return token


def esperar(cid, token):
    for _ in range(30):
        st = http('GET', cid, {'fields': 'status,error_message', 'access_token': token})
        if st.get('status') == 'FINISHED':
            return
        if st.get('status') == 'ERROR':
            raise RuntimeError(st.get('error_message'))
        time.sleep(5)


def publicar(uid, token, texto, imgs):
    if len(imgs) == 1:
        cid = http('POST', f'{uid}/threads', {'media_type': 'IMAGE', 'image_url': imgs[0], 'text': texto, 'access_token': token})['id']
    else:
        filhos = []
        for url in imgs[:20]:
            f = http('POST', f'{uid}/threads', {'media_type': 'IMAGE', 'image_url': url, 'is_carousel_item': 'true', 'access_token': token})['id']
            esperar(f, token)
            filhos.append(f)
        cid = http('POST', f'{uid}/threads', {'media_type': 'CAROUSEL', 'children': ','.join(filhos), 'text': texto, 'access_token': token})['id']
    esperar(cid, token)
    return http('POST', f'{uid}/threads_publish', {'creation_id': cid, 'access_token': token})['id']


def pendentes(feitos, hoje):
    for it in ET.parse(FEED).getroot().iter('item'):
        if (it.findtext('category') or '') == 'story':
            continue
        guid = it.findtext('guid')
        data = dt.datetime.strptime(it.findtext('pubDate'), '%a, %d %b %Y %H:%M:%S %z').date()
        if guid in feitos or data > hoje or (hoje - data).days > 2:
            continue
        yield guid, texto_threads(it.findtext('description') or '', it.findtext('link')), [e.get('url') for e in it.findall('enclosure')]


def main():
    teste = '--teste' in sys.argv
    hoje = dt.datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    if '--hoje' in sys.argv:
        hoje = dt.date.fromisoformat(sys.argv[sys.argv.index('--hoje') + 1])
    feitos = json.load(open(FEITOS)) if os.path.exists(FEITOS) else []
    if teste:
        for guid, texto, imgs in pendentes(feitos, hoje):
            print(f'--- {guid} ({len(texto)} caracteres, {len(imgs)} imagem/ns)\n{texto}\n')
        return
    uid, token = os.environ.get('THREADS_USER_ID') or 'me', os.environ.get('THREADS_TOKEN')
    if not token:
        print('Threads: segredo THREADS_TOKEN ainda não configurado; nada a fazer.')
        return
    lanc = json.load(open(os.path.join(RAIZ, 'content', 'lancamento.json'), encoding='utf-8'))
    if not lanc.get('iniciado') or hoje.isoformat() < lanc.get('data_inicio', ''):
        print('Threads: antes da largada (content/lancamento.json); nada é publicado.')
        return
    token = token_atual()
    novos = 0
    for guid, texto, imgs in pendentes(feitos, hoje):
        try:
            pid = publicar(uid, token, texto, imgs)
        except (urllib.error.HTTPError, RuntimeError) as e:
            detalhe = e.read()[:300] if isinstance(e, urllib.error.HTTPError) else e
            print(f'Threads: falha em {guid}: {detalhe!r}')
            break
        feitos.append(guid)
        novos += 1
        print(f'Threads publicado: {guid} ({pid})')
    json.dump(feitos[-300:], open(FEITOS, 'w'), indent=0)
    print(json.dumps({'threads_publicados': novos}))
    if novos == 0 and any(True for _ in pendentes(feitos, hoje)):
        sys.exit(1)


if __name__ == '__main__':
    main()
