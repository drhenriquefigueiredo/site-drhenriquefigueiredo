#!/usr/bin/env python3
"""Gera as imagens de IA das capas (roda no GitHub Actions, de graça, sem conta em serviço externo).

Lê content/capas/pedidos/*.json  ->  {"slug", "title", "topic", "prompt"}
Para cada pedido sem content/capas/ia-<slug>.jpg:
  1. gera a imagem com um modelo aberto (LCM Dreamshaper v7, licença MIT) na CPU
  2. monta as capas com tools/capa.py (título, tema, logo, CRM/RQE) em content/capas/
Nada em site/ muda aqui: as capas só entram no site no dia da publicação (tools/build.py).
"""
import glob, hashlib, json, os, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CAPAS = os.path.join(RAIZ, 'content', 'capas')
ROTULO = {'mao': 'Mão e punho', 'ortopedia': 'Ortopedia', 'dor': 'Dor', 'regenerativa': 'Medicina regenerativa',
          'esporte': 'Lesões e esporte'}
ESTILO = ('editorial medical illustration, soft realistic 3d render, calm navy blue and warm gold palette, '
          'clean minimal background, soft studio lighting, high detail, professional healthcare magazine style')
SEM = 'no text, no letters, no faces, no blood'
NEGATIVO = ('text, letters, words, watermark, logo, signature, face, portrait, blood, wound, surgery, gore, '
            'deformed hands, extra fingers, nsfw, low quality, blurry')


def cloudflare(p):
    """FLUX.1 [schnell] (licença Apache 2.0) no Cloudflare Workers AI: cota gratuita diária."""
    import base64, io, urllib.request
    from PIL import Image
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    corpo = json.dumps({'prompt': f"{p['prompt']}, {ESTILO}, {SEM}", 'steps': 6,
                        'seed': int(hashlib.md5(p['slug'].encode()).hexdigest(), 16) % (2 ** 31)}).encode()
    req = urllib.request.Request(url, data=corpo, headers={'Authorization': f"Bearer {os.environ['CF_API_TOKEN']}",
                                                         'Content-Type': 'application/json'})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=120))
        img = Image.open(io.BytesIO(base64.b64decode(r['result']['image']))).convert('RGB')
    except Exception as e:  # sem cota, token inválido etc.
        print(f"Cloudflare falhou para {p['slug']}: {e}")
        return False
    w, h = img.size
    alvo = int(w * 0.8)  # recorte 5:4 para servir às duas capas
    img = img.crop((0, (h - alvo) // 2, w, (h - alvo) // 2 + alvo)) if h > alvo else img
    img.resize((1280, 1024)).save(os.path.join(CAPAS, f"ia-{p['slug']}.jpg"), quality=90)
    print(f"imagem {p['slug']}: Cloudflare FLUX")
    return True


def montar(p):
    ia = os.path.join(CAPAS, f"ia-{p['slug']}.jpg")
    subprocess.run([sys.executable, os.path.join(AQUI, 'capa.py'), '--slug', p['slug'], '--titulo', p['title'],
                    '--tema', ROTULO[p['topic']], '--saida', CAPAS, '--imagem', ia], check=True)


def _h(txt):
    return hashlib.md5(txt.encode('utf-8')).hexdigest()[:12]


def conferir_mudancas(pedidos):
    """content/capas/meta/<slug>.json guarda o prompt e o título usados. Se o pedido mudar,
    apaga o que precisa ser refeito: prompt novo = imagem nova; título/tema novo = capas novas."""
    os.makedirs(os.path.join(CAPAS, 'meta'), exist_ok=True)
    for p in pedidos:
        m = os.path.join(CAPAS, 'meta', f"{p['slug']}.json")
        atual = {'prompt': _h(p['prompt']), 'capa': _h(p['title'] + '|' + p['topic'])}
        antes = json.load(open(m)) if os.path.exists(m) else None
        if antes and antes.get('prompt') != atual['prompt']:
            for n in (f"ia-{p['slug']}.jpg",):
                if os.path.exists(os.path.join(CAPAS, n)): os.remove(os.path.join(CAPAS, n))
        if antes and (antes != atual):
            for n in (f"blog-{p['slug']}.jpg", f"blog-{p['slug']}.webp", f"ig-{p['slug']}.jpg"):
                if os.path.exists(os.path.join(CAPAS, n)): os.remove(os.path.join(CAPAS, n))
        json.dump(atual, open(m, 'w'))


def main():
    """Gera a imagem de IA quando falta; monta as capas quando faltam. Para trocar a imagem ou o
    título basta atualizar o pedido (content/capas/pedidos/<slug>.json): o resto é refeito sozinho."""
    pedidos = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(CAPAS, 'pedidos', '*.json')))]
    conferir_mudancas(pedidos)
    gerar = [p for p in pedidos if not os.path.exists(os.path.join(CAPAS, f"ia-{p['slug']}.jpg"))]
    if gerar and os.environ.get('CF_ACCOUNT_ID') and os.environ.get('CF_API_TOKEN'):
        gerar = [p for p in gerar if not cloudflare(p)]  # o que falhar cai no modelo local
    if gerar:
        import torch
        from diffusers import DiffusionPipeline
        torch.set_num_threads(os.cpu_count() or 2)
        pipe = DiffusionPipeline.from_pretrained('SimianLuo/LCM_Dreamshaper_v7', torch_dtype=torch.float32,
                                                 safety_checker=None)
        pipe.to('cpu')
        for p in gerar:
            t0 = time.time()
            prompt = f"{p['prompt']}, {ESTILO}, {SEM}"
            g = torch.Generator('cpu').manual_seed(int(hashlib.md5(p['slug'].encode()).hexdigest(), 16) % (2 ** 31))
            img = pipe(prompt=prompt, width=640, height=512, num_inference_steps=6,
                       guidance_scale=8.0, generator=g).images[0]
            img.resize((1280, 1024)).save(os.path.join(CAPAS, f"ia-{p['slug']}.jpg"), quality=90)
            print(f"imagem {p['slug']}: {time.time() - t0:.0f}s")
    for p in pedidos:
        if not all(os.path.exists(os.path.join(CAPAS, n)) for n in (f"blog-{p['slug']}.jpg", f"ig-{p['slug']}.jpg")):
            montar(p)
            print(f"capas {p['slug']}")


if __name__ == '__main__':
    main()
