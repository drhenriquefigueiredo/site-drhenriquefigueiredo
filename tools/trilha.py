#!/usr/bin/env python3
"""Compõe a trilha de fundo dos Reels automáticos: música original, calma e sem direito autoral de terceiros.

Gerada por síntese (piano suave + acordes de fundo + baixo), em dó maior, ~75 bpm, 32 s.
Saída: content/redes/trilha-reel.m4a. Uso: python3 tools/trilha.py
"""
import os
import subprocess
import tempfile
import wave

import numpy as np
from scipy.signal import butter, lfilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "content", "redes", "trilha-reel.m4a")
SR = 44100
BPM = 76
BATIDA = 60 / BPM
DUR = 32.0


def nota(n):
    """Número MIDI -> frequência."""
    return 440.0 * 2 ** ((n - 69) / 12)


def piano(f, dur, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 2.2) * (1 - np.exp(-t * 400))
    som = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * k * 0.6) for k, a in ((1, 1), (2, .45), (3, .18), (4, .08)))
    return vel * env * som


def pad(freqs, dur):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    som = np.zeros_like(t)
    for f in freqs:
        for d in (-0.15, 0.0, 0.15):  # leve desafinação = som mais cheio
            som += np.sin(2 * np.pi * (f + d) * t) + 0.25 * np.sin(2 * np.pi * 2 * (f + d) * t)
    b, a = butter(2, 1400 / (SR / 2))
    return 0.05 * env * lfilter(b, a, som)


def reverb(x):
    saida = x.copy()
    for atraso, ganho in ((0.031, .35), (0.047, .3), (0.071, .25), (0.113, .2), (0.163, .15)):
        n = int(atraso * SR)
        eco = np.zeros_like(x)
        eco[n:] = x[:-n] * ganho
        for _ in range(3):
            saida += eco
            eco = np.concatenate([np.zeros(n), eco[:-n]]) * 0.55
    return saida


def somar(mix, ini, sinal):
    fim = min(len(mix), ini + len(sinal))
    if fim > ini:
        mix[ini:fim] += sinal[: fim - ini]


def compor():
    total = int(SR * DUR)
    mix = np.zeros(total + SR * 3)
    # C, G/B, Am, F (2 compassos de 4 tempos cada acorde), repetido
    acordes = [(48, [60, 64, 67, 72]), (47, [59, 62, 67, 71]), (45, [57, 60, 64, 69]), (41, [53, 57, 60, 65])]
    compasso = 4 * BATIDA
    t0, i = 0.0, 0
    while t0 < DUR:
        baixo, notas = acordes[i % 4]
        dur = 2 * compasso
        ini = int(t0 * SR)
        p = pad([nota(n) for n in notas[:3]], dur + 0.8)
        somar(mix, ini, p)
        somar(mix, ini, 0.18 * piano(nota(baixo), dur, 1))
        # arpejo em colcheias: sobe e desce, com pequenas variações de força
        arp = notas + [notas[2], notas[1]]
        for k in range(16):
            tn = t0 + k * BATIDA / 2
            if tn >= DUR:
                break
            n = arp[k % len(arp)] + (12 if k in (6, 14) else 0)
            s = piano(nota(n), 1.6, 0.16 + 0.05 * (k % 4 == 0))
            somar(mix, int(tn * SR), s)
        t0 += dur
        i += 1
    mix = reverb(mix)[:total]
    fade = int(SR * 2.5)
    mix[:int(SR * 0.3)] *= np.linspace(0, 1, int(SR * 0.3))
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = mix / np.max(np.abs(mix)) * 0.8
    return mix


def main():
    mix = compor()
    est = np.stack([mix, np.roll(mix, int(SR * 0.012))], axis=1)  # estéreo suave
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "t.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((est * 32767).astype("<i2").tobytes())
        os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "loudnorm=I=-20:TP=-2",
                        "-c:a", "aac", "-b:a", "128k", SAIDA], check=True)
    print(f"Trilha: {os.path.relpath(SAIDA, RAIZ)} ({os.path.getsize(SAIDA)//1024} KB)")


if __name__ == "__main__":
    main()
