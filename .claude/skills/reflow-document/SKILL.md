---
name: reflow-document
description: Fase 2 do reflow. Gera a documentação de negócio do projeto (output/<projeto>/02-docs/) usando o agent reflow-documenter.
argument-hint: <projeto>
---

Projeto: `$ARGUMENTS` (obrigatório: nome da subpasta em `input/`).

1. Confira se `output/$ARGUMENTS/01-inventory/inventory.json` existe. Se não existir, rode a skill `reflow-extract` para o projeto antes.
2. Delegue ao agent **`reflow-documenter`** com o prompt:
   `Projeto: $ARGUMENTS. Documente conforme suas instruções. Inventário em output/$ARGUMENTS/01-inventory/inventory.json, código em input/$ARGUMENTS/.`
3. Esta fase sempre **sobrescreve** `02-docs/`. Se `03-classification/classification.md`, `04-pad/` ou `05-test/` já existirem,
   avise: **"02 regerado — 03..05 podem estar desatualizados"**. Não apague nada.
4. Repasse ao usuário o resumo do agent.
