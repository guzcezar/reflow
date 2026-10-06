---
name: reflow-classify
description: Fase 3 do reflow. Classifica o projeto como PAD, PARTIAL ou NOT_PAD (output/<projeto>/03-classification/classification.md) usando a rubrica e o agent reflow-classifier.
argument-hint: <projeto>
---

Projeto: `$ARGUMENTS` (obrigatório).

1. Confira se `output/$ARGUMENTS/02-docs/use-cases.md` existe. Se não existir, rode a skill `reflow-document` antes.
2. Delegue ao agent **`reflow-classifier`** com o prompt:
   `Projeto: $ARGUMENTS. Classifique conforme reference/classification-rubric.md e suas instruções.`
3. Esta fase sempre **sobrescreve** `03-classification/classification.md`. Se `04-pad/` ou `05-test/` já existirem, avise:
   **"03 regerado — 04..05 podem estar desatualizados"**.
4. Mostre ao usuário a linha de veredito do agent.
