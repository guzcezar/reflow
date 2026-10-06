---
name: reflow-convert
description: Fase 4 do reflow. Converte a parte de UI/RPA do projeto em flows Robin para Power Automate Desktop (output/<projeto>/04-pad/) usando o agent reflow-pad-converter.
argument-hint: <projeto>
---

Projeto: `$ARGUMENTS` (obrigatório).

1. Leia o frontmatter de `output/$ARGUMENTS/03-classification/classification.md`. Se o arquivo não existir, rode a skill
   `reflow-classify` antes.
2. Se `verdict: NOT_PAD`, **pare**: informe que não há escopo PAD e não gere nada.
3. Delegue ao agent **`reflow-pad-converter`** com o prompt:
   `Projeto: $ARGUMENTS. Converta o escopo PAD conforme suas instruções.`
4. Esta fase sempre **sobrescreve** `04-pad/`. Se `05-test/` já existir, avise: **"04 regerado — 05 pode estar
   desatualizado"**.
5. Repasse o resumo do agent e destaque: a quantidade de `TODO reflow` (ações fora da whitelist) e o lembrete de que os snippets
   `[não validado]` em `reference/robin-actions.md` precisam ser validados no PAD.
