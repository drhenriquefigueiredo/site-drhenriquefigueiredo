# Guia editorial — Blog do Dr. Henrique Figueiredo

Médico ortopedista e cirurgião da mão em Campinas/SP. CRM-SP 199.832 · RQE 102783 (Ortopedia e Traumatologia) · RQE 124871 (Cirurgia da Mão). Atua também com Medicina Regenerativa e Intervenção em Dor. Atende na Clínica Kairós, Med Plex Campinas.

## Público e tom
- Pacientes leigos, adultos, de Campinas e região. Português do Brasil, frases curtas, sem jargão (ou com o termo técnico explicado na primeira vez).
- Tom acolhedor, claro e seguro. Primeira pessoa só em situações naturais ("no consultório, é comum…"); sem autopromoção.
- Evitar travessões longos em excesso, "não é X, mas Y", frases de efeito e clichês.

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
date, slug (sem acento, minúsculas, hífens, até ~80 caracteres), topic (mao | ortopedia | dor | regenerativa | esporte), title (≤ 70 caracteres, pergunta ou benefício claro), seo_title (≤ 65 + " | Dr. Henrique Figueiredo"), description (140–160 caracteres), excerpt (1 frase, ≤ 120 caracteres, para o card), keywords (4–6, incluir 1 com "Campinas"), condition (nome técnico da condição), body_html, faq [{q,a}], refs [{text,url}], gbp, instagram, status ("rascunho").

## Textos de redes
- gbp (Perfil do Google): 300–600 caracteres. Gancho em pergunta/situação + 1–2 frases educativas + convite para ler o artigo. Sem link, telefone ou hashtag no texto. Termina com:
  "\n\nConteúdo informativo; não substitui a avaliação médica.\nDr. Henrique Figueiredo · Médico ortopedista e cirurgião da mão · CRM-SP 199.832 · RQE 102783 / 124871" (temas fora da mão: "Médico ortopedista").
- instagram (também usado no Facebook): 400–700 caracteres, parágrafos curtos, no máximo 1 emoji, sem hashtags em excesso (0 a 3, ao final, antes da assinatura). Termina com:
  "\n\nLeia o artigo completo no link da bio.\n\nConteúdo informativo; não substitui a avaliação médica.\nDr. Henrique Figueiredo · Médico ortopedista · CRM-SP 199.832 · RQE 102783 / 124871"

## Ritmo e fluxo
- 15 artigos por ciclo de cobrança da Netlify (dia 13 ao dia 12), em dias alternados. As datas estão em content/calendario.json (campo date; temas sem data são reserva).
- Toda quarta-feira: rascunhos das datas da semana seguinte (segunda a domingo) vão para a página de aprovação (coleção "artigos", id = data).
- Dia de publicação, 6h: a tarefa diária pega o artigo aprovado mais antigo ainda não publicado e grava content/posts/<data>-<slug>.json (campos do artigo + date do dia + status "aprovado") com mcp__github__push_files. O GitHub Actions confere as capas (tools/garantir_capas.py), roda tools/build.py e grava site/ num único commit do robô (a Netlify só atualiza quando site/ muda). Depois: Google (Windsor), Instagram e Facebook (Make, pelo feed /blog/redes.xml).
- Acesso das tarefas agendadas: leitura com git clone https://github.com/drhenriquefigueiredo/site-drhenriquefigueiredo (funciona sem senha no ambiente das tarefas); escrita SÓ com mcp__github__push_files na branch main e SÓ em content/; acompanhamento com mcp__github__actions_list. Nunca grave em site/.

## Capas
Cada artigo tem um pedido em content/capas/pedidos/<slug>.json ({"slug","title","topic","prompt"}; prompt em inglês, cena neutra, sem rostos, sem texto). O workflow "Gerar capas com IA" gera content/capas/ia-<slug>.jpg e monta blog-<slug>.jpg/.webp e ig-<slug>.jpg; o build copia para site/assets no dia da publicação. Para trocar a imagem ou o título, basta atualizar o pedido (prompt novo = imagem nova; título novo = capas novas). Para testar localmente: `python3 tools/preparar.py --linha LINHA.json --data AAAA-MM-DD`. Para conferir uma capa avulsa: `python3 tools/capa.py --slug SLUG --titulo "Título" --tema "Rótulo" --saida /tmp/capas`. Rótulos: mao=Mão e punho, ortopedia=Ortopedia, dor=Dor, regenerativa=Medicina regenerativa, esporte=Lesões e esporte.
