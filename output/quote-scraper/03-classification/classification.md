---
verdict: PAD
pad_use_cases: [UC-01, UC-02, UC-03]
alerts: []
---

# Classificação: quote-scraper

## Veredito
`PAD`: o processo faz raspagem de HTML de um portal sem API (C3), e a única parte não-UI é gravar um CSV, que é simples e fica no flow.

## Critérios de UI

| # | Critério | Atendido | Justificativa | Evidências |
|---|---|---|---|---|
| C1 | Automação de UI web | não | Não há navegador, cliques nem digitação. As páginas são baixadas por HTTP direto. | `main.py:22` |
| C2 | Automação de UI desktop | não | Não há janelas nem controles desktop no inventário. | `inventory.json` (`ui_interactions` só tem `bs4`) |
| C3 | Raspagem de tela/HTML sem API | **sim** | O script lê o HTML do site público quotes.toscrape.com com BeautifulSoup e extrai o texto da citação, o autor, as tags e o link do autor por seletores CSS, além de seguir o link "Next" para paginar. O site não oferece API. | `main.py:24`, `main.py:26`, `main.py:29`, `main.py:30`, `main.py:31`, `main.py:32`, `main.py:36` |
| C4 | Terminal, SAP GUI, Citrix, imagem | não | Não há evidências. | — |
| C5 | API "não convencional" | não | O GET é anônimo, sem cookie, sessão ou endpoint interno de front. | `main.py:22` |

## Critérios de não-UI

| # | Critério | Atendido | Justificativa | Evidências |
|---|---|---|---|---|
| N1 | Transformação de dados | não | Há só limpeza de texto: tirar as aspas tipográficas, juntar as tags com `\|` e montar a URL absoluta. Pela rubrica (passo 4), isso é simples. Não há pandas, joins nem agregações. | `main.py:29`, `main.py:31`, `main.py:32`, `main.py:39` |
| N2 | API REST/SOAP documentada | não | O único HTTP é o GET da página HTML, que já faz parte da raspagem (C3), e não de uma API. | `main.py:22` |
| N3 | Banco de dados | não | Não há acesso a banco (`data_sources` está vazio no inventário). | `inventory.json` |
| N4 | Arquivos sem UI do Excel | sim | Grava `quotes.csv` em UTF-8 com cabeçalho fixo e sobrescreve o arquivo anterior. É uma operação simples com ação nativa. | `main.py:12`, `main.py:45-48` |
| N5 | E-mail, notificações, logs | sim | Há só `print` no console para o progresso e o total gravado. É simples. | `main.py:21`, `main.py:56` |

Nenhum gatilho G1–G3 disparou. Não há regra de negócio densa (G1), não há integração que exija código (G2) e o volume é de no máximo 10 páginas com cerca de 100 linhas (G3: `main.py:13`, `input/quote-scraper/quotes.csv`, com 102 linhas). Por isso, o veredito é `PAD`.

## Escopo PAD

O processo vai inteiro para o PAD.

- **UC-01: Extrair citações de uma página** (`main.py:21-34`)
  - Registra no log a página atual (`main.py:21`).
  - Baixa a página com timeout de 10 s e para se houver erro HTTP (`main.py:22-23`).
  - Para cada `div.quote`, lê `span.text` (sem as aspas “ ”), `small.author`, as tags `a.tag` unidas por `|` e o link absoluto de `a[href^='/author']` (`main.py:26-33`).
- **UC-02: Percorrer as páginas** (`main.py:17-41`)
  - Começa em `START_URL` e faz no máximo `MAX_PAGES` = 10 iterações (`main.py:11`, `main.py:13`, `main.py:19-20`).
  - Procura o link `li.next a` e para se ele não existir (`main.py:36-38`).
  - Monta a próxima URL e espera 0,5 s (`main.py:39-40`).
- **UC-03: Exportar para CSV** (parte não-UI simples, fica no flow) (`main.py:44-56`)
  - Para com erro se não houver citações e não grava o arquivo (`main.py:53-54`).
  - Grava `quotes.csv` em UTF-8 com as colunas `text,author,tags,author_url`, sobrescrevendo o anterior (`main.py:45-48`).
  - Registra no log o total gravado e o caminho (`main.py:56`).

## Alertas de portabilidade

Nenhum alerta se aplica.

- A1: não há DLL nem componente custom (as dependências são só `requests` e `beautifulsoup4`).
- A2: os seletores são CSS e não dependem de coordenadas, resolução ou imagem (`main.py:26-36`).
- A3: o site é público, sem login, captcha ou MFA (`main.py:22`).
- A4: a única lógica nos passos de extração é a limpeza de texto (`main.py:29-32`), sem regra de negócio.
- A5: não há credenciais (`credentials` está vazio no inventário).
