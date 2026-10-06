---
name: reflow
description: Pipeline completo do reflow para um projeto (ou todos) de input/ — extract → document → classify → [confirmação] → convert → test. Retoma de onde parou.
argument-hint: "[projeto]"
---

Pipeline: `extract → document → classify → [checkpoint humano] → convert → test`.

## Projetos
- Com argumento (`$ARGUMENTS`): só esse projeto (subpasta de `input/`).
- Sem argumento: todas as subpastas de `input/`, em ordem alfabética, **uma de cada vez**. Cada projeto passa pelo
  pipeline inteiro, checkpoint incluído, antes do próximo.

## Para cada projeto: retomar de onde parou
Pule uma fase se o artefato dela já existir. Senão, rode a skill da fase:

| Fase | Artefato que indica "feito" | Skill |
|---|---|---|
| 1 | `output/<p>/01-inventory/inventory.json` | `reflow-extract <p>` |
| 2 | `output/<p>/02-docs/use-cases.md` | `reflow-document <p>` |
| 3 | `output/<p>/03-classification/classification.md` | `reflow-classify <p>` |
| 4 | `output/<p>/04-pad/*/Main.robin` | `reflow-convert <p>` |
| 5 | `output/<p>/05-test/*/Main.robin` | `reflow-test <p>` |

Se uma fase falhar, reporte o problema e passe para o próximo projeto.

## Checkpoint (antes da fase 4)
- `verdict: NOT_PAD` → encerre o projeto (só documentação) e siga para o próximo.
- `verdict: PAD` ou `PARTIAL` e a fase 4 ainda não feita → mostre o veredito, o resumo do "Escopo PAD" e os alertas de
  `03-classification/classification.md`, e **pergunte ao usuário** se pode converter (AskUserQuestion: Converter / Pular este
  projeto). Só siga para 4 e 5 com confirmação.

## Ao final
Mostre uma tabela: `projeto | origem | veredito | fases concluídas | TODOs Robin | observações`.
