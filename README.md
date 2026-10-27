# Site do Dr. Henrique Figueiredo

- `site/` — o site publicado no Netlify (diretório base do Netlify: `site`).
- `content/posts/` — artigos do blog em JSON. Só são publicados os que têm `"status": "aprovado"`, na data marcada.
- `content/legacy.json` — os artigos antigos do blog, para a lista e o sitemap.
- `content/calendario.json` — calendário editorial de 6 meses.
- `tools/build.py` — gera as páginas dos artigos, a lista do blog, o sitemap, o llms.txt e o feed RSS.
- `tools/capa.py` — gera as capas (site/Google e Instagram) com a identidade visual.
- `.github/workflows/publicar.yml` — roda todo dia às 06:05 (Brasília) e publica os artigos do dia.
