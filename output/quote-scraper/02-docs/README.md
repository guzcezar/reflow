# Coleta de citações do quotes.toscrape.com

> Projeto legado: `input/quote-scraper` · Origem: `python` · Gerado pelo reflow em 2026-10-05

## Objetivo de negócio
O processo coleta todas as citações publicadas no site público quotes.toscrape.com (`main.py:1`, `main.py:11`). De cada citação ele extrai o texto, o autor, as tags e o link da página do autor (`main.py:29-32`). Ao final grava tudo num arquivo `quotes.csv` na mesma pasta do script (`main.py:12`, `main.py:44-48`).

Pela documentação do próprio projeto, o site é "feito para praticar scraping" e o projeto é um exemplo do reflow (`README.md:3-7`). Não há um consumidor de negócio identificado para o CSV gerado [inferido].

## Resumo
| Item | Valor |
|---|---|
| Gatilho | Manual, por linha de comando (`python main.py`) (`README.md:11-14`, `main.py:59-60`). Nenhum agendamento no código. |
| Frequência | não identificado |
| Volumetria | Até 10 páginas por execução (`main.py:13`). O `quotes.csv` existente tem 102 linhas, ou seja, cerca de 100 citações [inferido] (`quotes.csv`) |
| Entradas principais | Páginas HTML de `https://quotes.toscrape.com/` e seguintes, via link "Next" (`main.py:11`, `main.py:36-39`) |
| Saídas principais | Arquivo `quotes.csv` (colunas `text`, `author`, `tags`, `author_url`) (`main.py:46`). Log no console (`main.py:21`, `main.py:56`) |
| Sistemas envolvidos | [quotes.toscrape.com](integrations.md), [arquivo quotes.csv](integrations.md) |

## Mapa da documentação
- [Use cases](use-cases.md)
- [Fluxo do processo](process-flow.md)
- [Fontes de dados](data-sources.md)
- [Integrações](integrations.md)
- [Regras de negócio](business-rules.md)
- [Riscos e perguntas em aberto](risks.md)
