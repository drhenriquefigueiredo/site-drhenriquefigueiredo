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
LAYOUT = '3'  # mude para refazer todas as capas quando o desenho (tools/capa.py) mudar
ESTILO_FOTO = ('professional editorial photography, photorealistic, natural soft light, shallow depth of field, '
               'muted navy blue and warm beige palette, clean minimal composition, anatomically correct')
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


def pollinations(p):
    """FLUX (gratuito, sem conta) via image.pollinations.ai. Muito melhor em mãos e anatomia que o modelo local.
    O campo opcional "seed" do pedido troca a variação (use quando a imagem sair com defeito)."""
    import io, urllib.parse, urllib.request
    from PIL import Image
    seed = p.get('seed') or int(hashlib.md5(p['slug'].encode()).hexdigest(), 16) % 100000
    prompt = urllib.parse.quote(f"{p['prompt']}, {ESTILO_FOTO}, {SEM}")
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1280&height=1024&model=flux&nologo=true&private=true&enhance=false&seed={seed}"
    for tentativa in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'drhenriquefigueiredo-capas/1.0'})
            dados = urllib.request.urlopen(req, timeout=180).read()
            img = Image.open(io.BytesIO(dados)).convert('RGB')
            if img.size[0] < 600:
                raise ValueError(f'imagem pequena {img.size}')
            img.resize((1280, 1024)).save(os.path.join(CAPAS, f"ia-{p['slug']}.jpg"), quality=92)
            print(f"imagem {p['slug']}: FLUX (pollinations) seed {seed}")
            return True
        except Exception as e:
            print(f"pollinations falhou para {p['slug']} (tentativa {tentativa + 1}): {e}")
            time.sleep(20)
    return False


def formato(p):
    return p.get('formato', 'post')  # post (capa do artigo ou post simples), carrossel, story


def arquivos(p):
    """Arquivos finais esperados de cada pedido (para saber se falta montar)."""
    f, sl = formato(p), p['slug']
    if f == 'carrossel':
        return [f"car-{sl}-{k:02d}.jpg" for k in range(1, len(p.get('slides', [])[:5]) + 3)]
    if f == 'story':
        return [f"story-{sl}.jpg"]
    return [f"blog-{sl}.jpg", f"blog-{sl}.webp", f"ig-{sl}.jpg"]


def montar(p):
    ia = os.path.join(CAPAS, f"ia-{p['slug']}.jpg")
    if formato(p) == 'carrossel' and len(p.get('slides', [])) != 5:
        print(f"AVISO {p['slug']}: o carrossel precisa de exatamente 5 slides de conteúdo (tem {len(p.get('slides', []))}); "
              "com outro número ele não entra no feed do Instagram.")
    if formato(p) in ('carrossel', 'story'):
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as t:
            json.dump(p, t, ensure_ascii=False)
        cmd = [sys.executable, os.path.join(AQUI, 'arte.py'), '--pedido', t.name, '--saida', CAPAS]
        if os.path.exists(ia):
            cmd += ['--imagem', ia]
        subprocess.run(cmd, check=True)
        os.remove(t.name)
        return
    subprocess.run([sys.executable, os.path.join(AQUI, 'capa.py'), '--slug', p['slug'], '--titulo', p['title'],
                    '--tema', ROTULO[p['topic']], '--saida', CAPAS, '--imagem', ia], check=True)


def _h(txt):
    return hashlib.md5(txt.encode('utf-8')).hexdigest()[:12]


def conferir_mudancas(pedidos):
    """content/capas/meta/<slug>.json guarda o prompt e o conteúdo usados. Se o pedido mudar,
    apaga o que precisa ser refeito: prompt novo = imagem nova; texto/título/tema novo = artes novas."""
    os.makedirs(os.path.join(CAPAS, 'meta'), exist_ok=True)
    for p in pedidos:
        m = os.path.join(CAPAS, 'meta', f"{p['slug']}.json")
        texto = p['title'] + '|' + p.get('topic', '') + '|' + LAYOUT
        if formato(p) != 'post':
            texto += '|' + json.dumps({k: p.get(k) for k in ('formato', 'slides', 'final', 'texto', 'rotulo', 'rodape')},
                                      ensure_ascii=False, sort_keys=True)
        atual = {'prompt': _h((p.get('prompt') or '') + '|' + str(p.get('seed', ''))), 'capa': _h(texto)}
        antes = json.load(open(m)) if os.path.exists(m) else None
        if antes and antes.get('prompt') != atual['prompt']:
            if os.path.exists(os.path.join(CAPAS, f"ia-{p['slug']}.jpg")): os.remove(os.path.join(CAPAS, f"ia-{p['slug']}.jpg"))
        if antes and (antes != atual):
            for n in glob.glob(os.path.join(CAPAS, f"car-{p['slug']}-*.jpg")) + [os.path.join(CAPAS, n) for n in
                     (f"blog-{p['slug']}.jpg", f"blog-{p['slug']}.webp", f"ig-{p['slug']}.jpg", f"story-{p['slug']}.jpg")]:
                if os.path.exists(n): os.remove(n)
        json.dump(atual, open(m, 'w'))


def main():
    """Gera a imagem de IA quando falta; monta as artes quando faltam. Para trocar a imagem ou o
    texto basta atualizar o pedido (content/capas/pedidos/<slug>.json): o resto é refeito sozinho.
    Formatos: post (padrão: capa do blog + arte do Instagram), carrossel (tools/arte.py) e story."""
    pedidos = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(CAPAS, 'pedidos', '*.json')))]
    conferir_mudancas(pedidos)
    gerar = [p for p in pedidos if p.get('prompt') and not os.path.exists(os.path.join(CAPAS, f"ia-{p['slug']}.jpg"))]
    if gerar and os.environ.get('CF_ACCOUNT_ID') and os.environ.get('CF_API_TOKEN'):
        gerar = [p for p in gerar if not cloudflare(p)]
    if gerar:
        gerar = [p for p in gerar if not pollinations(p)]  # o que falhar cai no modelo local (qualidade menor)
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
        if not all(os.path.exists(os.path.join(CAPAS, n)) for n in arquivos(p)):
            montar(p)
            print(f"artes {p['slug']} ({formato(p)})")


if __name__ == '__main__':
    main()
