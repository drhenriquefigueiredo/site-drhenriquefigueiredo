#!/usr/bin/env python3
"""Lista os posts aprovados de artigos da semana, para agendar no TikTok pelo Metricool.

O TikTok não tem API gratuita aberta para publicar; o Metricool (plano gratuito: 20 publicações por mês)
já tem o TikTok conectado. Para caber no limite, vão para o TikTok só os posts de ARTIGO do blog
(arte única ou carrossel do artigo), cerca de 15 por mês. Posts avulsos e stories ficam fora.

Usa a mesma regra do feed do Instagram (tools/redes.py), dia a dia, então sai exatamente o que foi aprovado.
Uso: python3 tools/semana_tiktok.py [AAAA-MM-DD início] [dias=7]  -> JSON com data, título, legenda e imagens.
"""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import redes  # noqa: E402

LIMITE_LEGENDA = 2000


def main():
    ini = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    dias = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    saida = []
    for n in range(dias):
        dia = (ini + dt.timedelta(days=n)).isoformat()
        for x in redes.itens(dia):
            if x['date'] != dia or x['tipo'] == 'story' or '/blog/' not in x['link']:
                continue
            saida.append({'data': dia, 'guid': x['guid'], 'titulo': x['title'][:90],
                          'legenda': x['caption'][:LIMITE_LEGENDA],
                          'imagens': [redes.RAW + i for i in x['imgs']]})
    print(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
