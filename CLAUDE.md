# reflow

Recebe código legado (**Automation Anywhere A360**, **Python** e **.NET** C#/VB.NET), documenta, classifica e
converte para Power Automate Desktop (Robin) os processos com interação de UI/RPA, e gera um flow Robin de teste.

## Princípios
KISS acima de tudo, sem overengineering. SOLID e Clean Code no que for útil. Código organizado por módulos.

## Divisão de responsabilidades
- **Python (`reflow/`)**: só extração determinística, sem LLM. Gera `01-inventory/inventory.json` com fatos `arquivo:linha`
  e secrets mascarados. Usa só stdlib, Python 3.12+, uv, pytest e ruff.
  - Nova origem (ex.: A360 v11, UiPath) = novo módulo em `extractors/` implementando `Extractor` (`detect`/`extract`) e
    registrado em `extractors/__init__.py`.
- **Claude Code (`.claude/`)**: toda a interpretação. Uma skill por fase, mais `/reflow` que orquestra. Cada fase de LLM
  roda num agent isolado, que lê só os artefatos da fase anterior e as referências.

## Pipeline e artefatos (`output/<projeto>/`)
| Fase | Skill | Agent | Artefato |
|---|---|---|---|
| 1 extract | `/reflow-extract` | — | `01-inventory/inventory.json` |
| 2 document | `/reflow-document` | `reflow-documenter` | `02-docs/` |
| 3 classify | `/reflow-classify` | `reflow-classifier` | `03-classification/classification.md` (frontmatter `verdict`) |
| — | checkpoint humano por projeto (PAD/PARTIAL) | | |
| 4 convert | `/reflow-convert` | `reflow-pad-converter` | `04-pad/<flow>/Main.robin` (+ `boundary.md` se PARTIAL) |
| 5 test | `/reflow-test` | `reflow-pad-tester` | `05-test/test_<flow>/Main.robin` |

- `/reflow` retoma de onde parou. Uma skill de fase sempre sobrescreve a própria fase e avisa que as seguintes podem
  estar desatualizadas.
- O veredito pode ser `PAD`, `PARTIAL` ou `NOT_PAD`. Processo com UI vai inteiro para o PAD (`PAD`). Só se separa
  quando a parte não-UI é complexa (`PARTIAL`, KISS: na dúvida, `PAD`). No `PARTIAL`, o reflow entrega o contrato
  (`in_`/`out_` e o mapeamento legado → flow), sem mexer no código legado e sem gerar orquestrador.

## Referências editáveis (`reference/`)
- `classification-rubric.md`: critérios de classificação
- `robin-conventions.md`: estrutura e regras dos flows
- `robin-actions.md`: **whitelist** de ações Robin. Os snippets marcados `[não validado]` precisam ser validados no PAD
  (Ctrl+C no designer).
- `templates/docs/`: templates da documentação

## Convenções
- Código, nomes de skills e agents e prefixos Robin (`step_`, `in_`, `out_`, `cfg_`) em **inglês**. Nomes Robin todos em
  minúsculo, snake_case. Nomes de negócio e toda a documentação em **pt-BR**.
- `input/` (uma subpasta = um projeto) fica fora do git, exceto o exemplo público `input/quote-scraper/`. `output/` é
  versionado.
- **Nenhum valor de secret** em docs ou flows, só referências.

## Comandos
```bash
uv run python -m reflow extract <projeto> | --all
uv run pytest
uv run ruff check . && uv run ruff format .
```
