# Site do Dr. Henrique Figueiredo

- `site/` — o site publicado no Netlify (diretório base do Netlify: `site`).
- `content/posts/` — artigos do blog em JSON. Só são publicados os que têm `"status": "aprovado"`, na data marcada.
- `content/legacy.json` — os artigos antigos do blog, para a lista e o sitemap.
- `content/calendario.json` — calendário editorial de 6 meses.
- `tools/build.py` — gera as páginas dos artigos, a lista do blog, o sitemap, o llms.txt e o feed RSS.
- `tools/capa.py` — gera as capas (site/Google e Instagram) com a identidade visual.
- `.github/workflows/threads.yml` + `tools/threads.py` — publica todo dia no Threads (API oficial, grátis) o mesmo post aprovado do Instagram, com legenda adaptada a 500 caracteres e assinatura com CRM/RQE.
- `tools/semana_tiktok.py` — lista os posts de artigos da semana para agendar no TikTok pelo Metricool (plano gratuito, até 20 por mês).
- `.github/workflows/publicar.yml` — roda todo dia às 06:05 (Brasília) e atualiza o feed das redes sem gastar créditos da Netlify; o site só é publicado às segundas (ou ao rodar o workflow manualmente), com os artigos aprovados da semana inteira de uma vez.
