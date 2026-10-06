---
name: reflow-test
description: Fase 5 do reflow. Gera um desktop flow de teste em Robin (output/<projeto>/05-test/) que executa o flow convertido e valida as integrações principais, usando o agent reflow-pad-tester.
argument-hint: <projeto>
---

Projeto: `$ARGUMENTS` (obrigatório).

1. Confira se `output/$ARGUMENTS/04-pad/` tem pelo menos um flow (`*/Main.robin`). Se não tiver, informe e pare: o teste
   depende da conversão.
2. Delegue ao agent **`reflow-pad-tester`** com o prompt:
   `Projeto: $ARGUMENTS. Gere o flow de teste conforme suas instruções.`
3. Esta fase sempre **sobrescreve** `05-test/`.
4. Repasse o resumo do agent.
