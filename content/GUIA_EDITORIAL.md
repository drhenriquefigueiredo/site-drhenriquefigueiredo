# Guia editorial — Blog do Dr. Henrique Figueiredo

Médico ortopedista e cirurgião da mão em Campinas/SP. CRM-SP 199.832 · RQE 102783 (Ortopedia e Traumatologia) · RQE 124871 (Cirurgia da Mão). Atua também com Medicina Regenerativa e Intervenção em Dor. Atende na Clínica Kairós, Med Plex Campinas.

## Público e tom
- Pacientes leigos, adultos, de Campinas e região. Português do Brasil, frases curtas, sem jargão (ou com o termo técnico explicado na primeira vez).
- Tom acolhedor, claro e seguro. Primeira pessoa só em situações naturais ("no consultório, é comum…"); sem autopromoção.
- Evitar travessões longos em excesso, "não é X, mas Y", frases de efeito e clichês.

## Voz humana (desde 20/11; vale para redes, Google, respostas e blog)
Escreva como o Dr. Henrique fala com um paciente no consultório, não como um folheto ou um robô:
- Abra por uma cena comum e reconhecível, sem identificar ninguém: "Toda semana alguém me conta que acorda com a mão dormente." / "Uma pergunta que ouço quase todo dia no consultório:". Nunca descreva um paciente real.
- Nas redes, primeira pessoa natural ("eu costumo explicar assim", "no consultório eu mostro"); no blog, com moderação.
- Palavras do paciente antes do termo técnico ("formiga", "trava", "dá choque", "estala"). Uma ideia por parágrafo, frases de até 20 palavras.
- Varie a forma de um post para o outro (pergunta, história curta, mito, número com fonte, "o que eu faria"); dois posts seguidos nunca começam do mesmo jeito.
- Proibido o que denuncia texto de máquina: "Descubra", "Neste post", "Vamos lá", "Você sabia que", listas sempre de 3 itens, travessões em série, emojis decorativos, fechamento genérico ("Cuide-se!", "Sua saúde agradece").
- Termine com uma pergunta de verdade, fácil de responder em uma palavra ("Em qual mão você sente mais?"), para puxar conversa nos comentários.
- Respostas a comentários e avaliações: 1 a 3 frases, começam pelo nome da pessoa quando houver, respondem exatamente o que ela disse, agradecem sem exagero, nunca dão diagnóstico, dose ou conduta e nunca confirmam que a pessoa é paciente; dúvida individual = convite gentil para avaliação pelo WhatsApp do link da bio. Nada de texto igual para duas pessoas.

## Regras obrigatórias (Resolução CFM 2.336/2023)
- Nada de superlativos ou comparação: "o melhor", "referência", "o mais procurado", "líder", "único".
- Nada de promessa ou garantia de resultado, "cura definitiva", "sem dor", "100%".
- Nada de antes e depois, depoimentos, fotos ou dados de pacientes, casos identificáveis.
- Nada de preço, desconto, promoção, sorteio ou brinde.
- Não incentivar automedicação: medicamentos só de forma geral ("medicações prescritas pelo médico"), nunca doses.
- Procedimentos com restrição regulatória (PRP, células-tronco, terapias biológicas): só conteúdo educativo, citando que a indicação segue as normas do CFM e as evidências científicas; nunca apresentar como tratamento oferecido com resultado garantido. Células-tronco: deixar claro o que ainda é pesquisa.
- Toda página/post termina com identificação: nome, "Médico ortopedista", CRM e RQE (o site já inclui no rodapé e no box do autor; os textos de redes sociais incluem a linha final padrão).

## Estrutura do artigo (body_html)
- 550 a 900 palavras. HTML simples: `<p>`, `<h2>`, `<ul><li>`, `<strong>`. Sem `<h1>` (o título já é o h1), sem imagens, sem scripts, sem estilos.
- Abertura: 1 parágrafo com a situação do dia a dia e o nome da condição em **negrito**.
- 4 a 6 seções `<h2>` cobrindo: o que é, por que acontece/quem tem risco, sintomas, diagnóstico, tratamento (do conservador ao cirúrgico, quando couber), o que fazer/quando procurar avaliação.
- Pelo menos uma frase baseada em evidência citando o tipo de estudo e o ano ("uma revisão sistemática publicada em 2024…"), fiel ao resumo do artigo no PubMed.
- 3 perguntas frequentes (faq) com respostas de 1 a 3 frases.
- 1 a 3 referências (refs) reais do PubMed, preferindo revisões sistemáticas, meta-análises, diretrizes e revisões dos últimos 10 anos, com `url` = link do DOI. Nunca inventar referência: só usar o que veio do PubMed.
- Pode mencionar Campinas no máximo 1 vez, de forma natural.

## Campos do JSON
date, slug (sem acento, minúsculas, hífens, até ~80 caracteres), topic (mao | ortopedia | dor | regenerativa | esporte), title (≤ 70 caracteres, pergunta ou benefício claro), seo_title (até 60 caracteres no total; termine com " em Campinas" quando couber naturalmente, ex.: "Rizartrose: dor na base do polegar e tratamento em Campinas"; o site corta a assinatura do médico se passar de 65), description (140–160 caracteres), excerpt (1 frase, ≤ 120 caracteres, para o card), keywords (4–6, incluir 1 com "Campinas"), condition (nome técnico da condição), body_html, faq [{q,a}], refs [{text,url}], gbp, instagram, status ("rascunho").

## Textos de redes
- gbp (Perfil do Google): 300–600 caracteres. Gancho em pergunta/situação + 1–2 frases educativas + convite para ler o artigo. Sem link, telefone ou hashtag no texto. Termina com:
  "\n\nConteúdo informativo; não substitui a avaliação médica.\nDr. Henrique Figueiredo · Médico ortopedista e cirurgião da mão · CRM-SP 199.832 · RQE 102783 / 124871" (temas fora da mão: "Médico ortopedista").
- instagram (também usado no Facebook): 400–700 caracteres, parágrafos curtos, no máximo 1 emoji, sem hashtags em excesso (0 a 3, ao final, antes da assinatura). Termina com:
  "\n\nLeia o artigo completo no link da bio.\n\nConteúdo informativo; não substitui a avaliação médica.\nDr. Henrique Figueiredo · Médico ortopedista · CRM-SP 199.832 · RQE 102783 / 124871"

## Ritmo e fluxo
- 15 artigos por ciclo de cobrança da Netlify (dia 13 ao dia 12), em dias alternados. As datas estão em content/calendario.json (campo date; temas sem data são reserva).
- Todo domingo: o agente semanal (content/AGENTE_SEMANAL.md) monta o pacote da semana — relatório, carrosséis, posts e stories do Instagram, respostas a avaliações, roteiro de vídeo opcional (coleção "conteudos") e os artigos da semana seguinte (coleção "artigos", id = data).
- Instagram, tudo estático (nada depende de gravação): no máximo 1 publicação de feed por dia, às 18h30, pico de seguidores online segundo o Metricool (carrossel do artigo no lugar da arte do artigo, carrossel extra ou post de arte única; carrossel = 7 artes), pelo Make lendo content/redes/feed.xml (servido pelo GitHub; não gasta créditos da Netlify). No feed, <category> diz a rota do Make: "foto" (rota 1, arte única) ou "carrossel" (rota 2, exatamente 7 imagens). O Facebook recebe o mesmo feed pelo Make (módulo da página).
- Story: 2 por semana (terça e sexta), às 19h (DEPOIS do post do feed das 18h30, porque o story chama para ele), agendado no Metricool (marca 7757578, Instagram e Facebook conectados) pela tarefa diária depois da aprovação; imagem = raw do GitHub content/capas/story-<id>.jpg. O workflow stories.yml (API da Meta) fica como reserva e não faz nada sem os segredos IG_USER_ID/IG_TOKEN.
- TikTok e Threads (Metricool, marca 7757578): a tarefa diária agenda o PRIMEIRO carrossel aprovado de cada semana no TikTok às 18h (mesmas 7 imagens e legenda; só depois que o TikTok business estiver conectado) e 1 thread de texto por semana às 12h30. Limite do Metricool gratuito: 20 publicações por mês, cada rede conta 1. Divisão: 2 stories + 1 thread + 1 TikTok por semana; antes de agendar, a tarefa conta o que já tem metricool_id ou tiktok_metricool_id no mês e não passa de 20 (prioridade: TikTok, stories, Threads).
- Melhores horários (Metricool, seguidores online): Instagram pico 18h–20h (feed 18h30); Facebook 10h–12h e 17h (vai junto do Instagram às 18h30); stories 19h (sempre depois do feed das 18h30); Threads 12h30; TikTok 18h (melhor horário medido em 20/11); Google de manhã.
- Google: post diário pelo Windsor (plano gratuito), fora da conta do Metricool.
- Fila das redes: content/redes/fila/<id>.json = {"date","id","tipo": "post"|"carrossel"|"story","title","topic","caption","artigo"?} (story sem caption; "artigo" = slug no carrossel do artigo, que substitui a arte única no dia dele). Só entra na fila o que foi aprovado na página.
- WhatsApp: as mensagens prontas dizem a origem ("Vim pelo Instagram/Google/site…"); o integracao.js troca "pelo site" pelo canal de chegada. O botão Agendar do Google abre o WhatsApp com "Vim pelo Google".
- Dia de publicação, 6h: a tarefa diária pega o artigo aprovado mais antigo ainda não publicado e grava content/posts/<data>-<slug>.json (campos do artigo + date do dia + status "aprovado") com mcp__github__push_files. O GitHub Actions confere as capas (tools/garantir_capas.py), roda tools/build.py e grava site/ num único commit do robô (a Netlify só atualiza quando site/ muda). Depois: Google (Windsor), Instagram e Facebook (Make, pelo feed /blog/redes.xml).
- Acesso das tarefas agendadas: leitura com git clone https://github.com/drhenriquefigueiredo/site-drhenriquefigueiredo (funciona sem senha no ambiente das tarefas); escrita SÓ com mcp__github__push_files na branch main e SÓ em content/; acompanhamento com mcp__github__actions_list. Nunca grave em site/.

## Capas
Cada artigo tem um pedido em content/capas/pedidos/<slug>.json ({"slug","title","topic","prompt"}; prompt em inglês, cena neutra, sem rostos, sem texto). O workflow "Gerar capas com IA" gera content/capas/ia-<slug>.jpg e monta blog-<slug>.jpg/.webp e ig-<slug>.jpg; o build copia para site/assets no dia da publicação. Para trocar a imagem ou o título, basta atualizar o pedido (prompt novo = imagem nova; título novo = capas novas). Para testar localmente: `python3 tools/preparar.py --linha LINHA.json --data AAAA-MM-DD`. Para conferir uma capa avulsa: `python3 tools/capa.py --slug SLUG --titulo "Título" --tema "Rótulo" --saida /tmp/capas`. Rótulos: mao=Mão e punho, ortopedia=Ortopedia, dor=Dor, regenerativa=Medicina regenerativa, esporte=Lesões e esporte.

Instagram (ig-<slug>.jpg e a capa dos carrosséis) em 3 modelos que se revezam pela data de publicação (tools/modelos.py): "foto" (foto em tela cheia), "claro" (só tipografia em fundo creme) e "recorte" (foto recortada em fundo creme). Campos opcionais no pedido: "modelo" (força um dos três), "gancho" (texto grande e curto da capa) e "apoio" (frase pequena embaixo); sem eles, o título é dividido no 1º ":" ou "?". O rodapé de toda capa leva o monograma "H." com nome, CRM e RQE. A capa larga do site/Google (blog-<slug>) não muda.

## Como as redes se conversam (desde 20/11/2026)

Um conteúdo aprovado vira, sem ninguém repostar à mão:
- **Instagram feed 18h30 + Página do Facebook 18h30** (Make, cenário do feed RSS). A Página tem pouco alcance (25 seguidores); o alcance do Facebook vem do perfil pessoal, que recebe os posts e stories do Instagram pelo compartilhamento automático da Central de Contas da Meta (configuração dele no app, não é automação nossa).
- **Story 19h** (Metricool) chamando para o post que acabou de sair.
- **TikTok 18h** (Metricool): o primeiro carrossel da semana.
- **Threads 12h30** (Metricool): 1 texto por semana, com pergunta no fim.
- **Google** todo dia de manhã (tarefa diária), levando ao artigo do blog.
- **Comentários do Instagram**: Make (08h00) → planilha "Comentários — respostas humanizadas" → rascunho na voz dele (08h17) → ele marca "sim" → Make publica na manhã seguinte.
- **Direct e Messenger**: perguntas sugeridas (onde fica, convênio, horário) e boas-vindas no Messenger, no Meta Business Suite. No Instagram já existe um robô de boas-vindas anterior; não duplicar.
- Limites gratuitos: Metricool 20 publicações por mês (cada rede conta 1); Make 1.000 créditos e 2 cenários ativos (os dois em uso).
