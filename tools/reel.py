#!/usr/bin/env python3
"""Transforma cada carrossel aprovado (7 artes car-<id>-01..07.jpg) num Reel vertical.

Por quê: no perfil, Reels alcançam muito mais gente que imagem e carrossel, e o Dr. Henrique
não precisa gravar nada. O vídeo usa exatamente as artes já aprovadas, na mesma ordem.

Saída: content/capas/reel-<id>.mp4 (1080x1920, 30 fps, H.264, ~25 s, áudio mudo).
Só gera o que ainda não existe ou o que teve arte refeita (reel-<id>.txt guarda a impressão digital das artes).
Uso: python3 tools/reel.py [--id <id>] [--forcar]
"""
import argparse
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(RAIZ, "content", "capas")
W, H = 1080, 1920
TOPO = 170          # arte um pouco acima do centro: a legenda do Reel cobre a parte de baixo da tela
FPS = 30
DUR = [3.2, 4.6, 4.6, 4.6, 4.6, 4.6, 3.6]   # capa, 5 cards (tempo de leitura), fechamento
TRANS = 0.45


def carrosseis():
    ids = {}
    for f in glob.glob(os.path.join(CAPAS, "car-*-0[1-7].jpg")):
        m = re.match(r"car-(.+)-0([1-7])\.jpg$", os.path.basename(f))
        if m:
            ids.setdefault(m.group(1), set()).add(int(m.group(2)))
    return sorted(i for i, s in ids.items() if s == set(range(1, 8)))


def quadro(arte, destino):
    """Arte no alto de um fundo azul-marinho da marca (degradê suave)."""
    im = Image.open(arte).convert("RGB")
    fundo = Image.new("RGB", (W, H))
    topo, base = (16, 33, 56), (9, 19, 34)
    for y in range(H):
        t = y / (H - 1)
        cor = tuple(int(topo[i] + (base[i] - topo[i]) * t) for i in range(3))
        fundo.paste(cor, (0, y, W, y + 1))
    frente = im.resize((W, int(im.height * W / im.width)))
    fundo.paste(frente, (0, TOPO))
    fundo.save(destino, quality=95)


def gerar(cid, forcar=False):
    artes = [os.path.join(CAPAS, f"car-{cid}-0{n}.jpg") for n in range(1, 8)]
    saida = os.path.join(CAPAS, f"reel-{cid}.mp4")
    # Só gera o que falta ou o que teve arte refeita (compara a impressão digital das 7 artes,
    # porque no GitHub as datas dos arquivos mudam a cada checkout).
    marca = os.path.join(CAPAS, f"reel-{cid}.txt")
    digital = hashlib.sha256(b"".join(open(a, "rb").read() for a in artes)).hexdigest()
    if os.path.exists(saida) and not forcar:
        if not os.path.exists(marca) or open(marca).read().strip() == digital:
            if not os.path.exists(marca):
                open(marca, "w").write(digital + "\n")
            return None
    tmp = tempfile.mkdtemp()
    try:
        entradas, filtros = [], []
        for n, arte in enumerate(artes):
            q = os.path.join(tmp, f"q{n}.jpg")
            quadro(arte, q)
            d = DUR[n] + (TRANS if n < 6 else 0)
            quadros = int(round(d * FPS))
            entradas += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", q]
            # zoom lento (até 4%) para o vídeo não parecer uma imagem parada
            filtros.append(
                f"[{n}:v]scale={W*2}:{H*2},zoompan=z='min(1+0.04*on/{quadros},1.04)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                f"trim=duration={d:.3f},setpts=PTS-STARTPTS,format=yuv420p[v{n}]"
            )
        atual, desloc = "v0", DUR[0]
        for n in range(1, 7):
            filtros.append(f"[{atual}][v{n}]xfade=transition=fade:duration={TRANS}:offset={desloc:.3f}[x{n}]")
            atual = f"x{n}"
            desloc += DUR[n]
        total = sum(DUR) + TRANS
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *entradas,
               "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
               "-filter_complex", ";".join(filtros), "-map", f"[{atual}]", "-map", "7:a",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
               "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "64k", "-shortest",
               "-movflags", "+faststart", saida]
        subprocess.run(cmd, check=True)
        open(marca, "w").write(digital + "\n")
        return saida
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        print("ffmpeg não encontrado", file=sys.stderr)
        sys.exit(1)
    ids = [a.id] if a.id else carrosseis()
    feitos = [s for s in (gerar(i, a.forcar) for i in ids) if s]
    for s in feitos:
        print(f"Reel gerado: {os.path.relpath(s, RAIZ)} ({os.path.getsize(s)//1024} KB)")
    if not feitos:
        print("Nenhum Reel novo.")


if __name__ == "__main__":
    main()
