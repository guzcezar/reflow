---
name: reflow-extract
description: Fase 1 do reflow. Roda a extração determinística (Python) de um projeto em input/ e gera output/<projeto>/01-inventory/inventory.json.
argument-hint: <projeto> | --all
---

Rode, na raiz do repositório:

```bash
uv run python -m reflow extract $ARGUMENTS
```

- Sem argumento → use `--all`.
- Se der erro de "nenhuma origem suportada", informe que o reflow só cobre **A360**, **Python** e **.NET** (código-fonte C#/VB.NET) e pare para esse projeto.
- Se `02-docs/` ou fases seguintes já existirem para o projeto, avise: **"01 regerado — 02..05 podem estar
  desatualizados"**. Não apague nada.

Ao final, mostre por projeto: origem detectada e contagem de `ui_interactions`, `http_calls`, `data_sources` e
`credentials` (leia do JSON gerado).
