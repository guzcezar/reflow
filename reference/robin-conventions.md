# Convenções Robin (Power Automate Desktop)

Este arquivo é lido pelos agents `reflow-pad-converter` e `reflow-pad-tester`. O objetivo é um flow que a pessoa
**cola e roda**, sem preparar nada antes.

## Como o Robin entra no PAD

O PAD não importa projetos, e colar texto **não cria subflow** (nem com `FUNCTION ... END FUNCTION`). Por isso cada
flow é **um único `Main.robin`**: a pessoa cria o desktop flow, cola o arquivo inteiro no `Main` (Ctrl+V) e roda.

## Estrutura de saída

```
04-pad/<nome_do_flow>/
  Main.robin            # o flow inteiro, pronto para colar
  README.md             # passo a passo (criar flow, colar, rodar) e resultado esperado
  notas-conversao.md    # legado × flow, divergências, pendências e TODOs
  ui-elements.md        # SÓ se o flow usar appmask (ver regra 5)
```

## Regras

1. **Zero preparo.** Nada de arquivo de configuração, pasta para criar à mão ou variável de input/output para declarar.
   - Configuração vira `SET cfg_...` no começo do `Main`, com os valores do legado.
   - Arquivos de saída vão para uma pasta que sempre existe no Windows: `C:\Users\Public\Documents\`.
   - `out_` são variáveis comuns (`SET out_status ...`). Só declare input/output na UI do PAD quando outro flow for
     chamar este (`PARTIAL`), e diga isso no README.
   - Exceção: secret. Ele nunca é literal; vem de `in_` sensível criado à mão ou de credencial do Power Automate, e o
     README explica como criar.
2. **Organização dentro do `Main`**, nesta ordem:
   1. comentário de cabeçalho (o que o flow faz e `# Legado: <arquivo>`);
   2. bloco de `SET cfg_...` e inicialização dos `out_` (`out_status`, `out_error_message` e os específicos);
   3. uma seção por use case, aberta por `# UC-xx: <o que faz> (<arquivo:linha>)`, com 2 linhas em branco antes;
   4. no fim, `out_status = 'OK'` ou `'ERRO'` com `out_error_message`.
3. **Nomes**: tudo em minúsculo, snake_case (variáveis, flow, tela e elemento de UI). Prefixos `in_`, `out_`, `cfg_`.
   Nomes de negócio em pt-BR (`tabela_citacoes`, `numero_pagina`).
4. **Erros.** Bloco de erro ainda não tem forma útil validada (o corpo do `ON BLOCK ERROR` não aceita ações livres):
   não use `BLOCK`. Erro técnico para o flow com a mensagem do PAD. Erro de negócio (lista vazia, dado faltando) usa
   `IF`: `out_status = 'ERRO'`, `out_error_message` preenchido, e as ações seguintes ficam no `ELSE`.
5. **Evite UI elements.** Cada `appmask` obriga a pessoa a capturar o elemento antes de colar. No browser:
   - navegue pela URL (`GoToWebPage`) em vez de clicar em links. Paginação: monte a URL de cada página
     (`/page/%numero_pagina%/`) num `LOOP` até o limite do legado; não procure o link "Próxima" (ver `ExtractTable`
     na whitelist);
   - leia dados com `ExtractTable` usando seletor CSS literal (não precisa de captura).
   Use `appmask` só quando não houver alternativa (app desktop, botão sem URL) e liste cada um em `ui-elements.md`
   com o seletor esperado e o `arquivo:linha` do legado.
6. **Browser**: Edge com a extensão Microsoft Power Automate (`WebAutomation.LaunchEdge.LaunchEdge`).
7. **Esperas**: as ações de browser já esperam a página carregar. `WAIT <segundos>` fixo só para reproduzir pausa do
   legado, com comentário.
8. **Só ações da whitelist** (`reference/robin-actions.md`), copiando a sintaxe exata. Prefira as marcadas
   `[validado PAD: rodou]`. Ação ausente vira `# TODO reflow: ação não mapeada — <o que precisa fazer>`, listada em
   `notas-conversao.md`. Ação que o PAD **não tem** (listada na whitelist como inexistente) nunca é usada.
9. **Bug óbvio do legado é corrigido** e registrado em `notas-conversao.md` ("Divergências do legado") com o risco
   (`R-xx`) e o `arquivo:linha`. Na dúvida entre bug e regra de negócio, reproduza o legado e registre a pergunta.
10. **KISS: nada além do legado.** Não crie log, arquivo auxiliar ou temporário que o legado não tem. Arquivo de saída:
    cabeçalho com `Overwrite` e uma linha por registro com `Append`, como no snippet "Escrever CSV" da whitelist.
11. **README curto**: só os passos para colar e rodar, pré-requisitos reais (ex.: extensão do Edge) e o resultado
    esperado. Análise vai para `notas-conversao.md`.

## Fronteira (projetos PARTIAL)

O flow recebe tudo o que precisa via `in_` e devolve via `out_` (declarados na UI do PAD; o README lista cada um).
Não acessa banco nem API que pertença à parte não-UI. O contrato fica em `04-pad/boundary.md`.

## Teste (fase Test)

`05-test/test_<nome_do_flow>/` é **um desktop flow separado, também um único `Main.robin`**, que a pessoa roda
**depois** do flow convertido. Ele confere o que o flow deixou de resultado observável (arquivo gerado, conteúdo,
quantidade de linhas) com ações da whitelist e grava PASS/FAIL por cenário em
`C:\Users\Public\Documents\test_<nome_do_flow>.log`. Mesmas regras: zero preparo, sem `BLOCK`, sem subflows.
