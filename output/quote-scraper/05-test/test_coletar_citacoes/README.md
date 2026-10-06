# test_coletar_citacoes

Confere o `quotes.csv` que o flow `coletar_citacoes` gerou. Não chama o flow convertido: rode ele antes.

## Como rodar
1. Rode o flow `coletar_citacoes` (ver `04-pad/coletar_citacoes/README.md`) até o fim, com `out_status` = `OK`.
2. No Power Automate Desktop, crie um desktop flow novo chamado `test_coletar_citacoes`.
3. Abra o subflow `Main`, clique na área de ações e cole o conteúdo inteiro de `Main.robin` (Ctrl+V).
4. Salve e rode.

Não precisa criar pasta, variável nem credencial, nem abrir o browser.

## Onde ver o resultado
`C:\Users\Public\Documents\test_coletar_citacoes.log`, sobrescrito a cada execução: uma linha `CT-xx PASS` ou
`CT-xx FAIL <motivo>` por cenário e, no fim, `Total: N PASS, N FAIL`.

Se o `quotes.csv` não existir, o teste para no CT-01 com o erro do PAD (arquivo não encontrado). Conte como falha
do CT-01.

## Resultado esperado

| Cenário | Regra | Confere | Esperado hoje |
|---|---|---|---|
| CT-01 | RN-11 | `quotes.csv` existe e não está vazio | PASS |
| CT-02 | RN-12 | arquivo começa com `text,author,tags,author_url` | PASS |
| CT-03 | RN-07 | nenhuma aspa tipográfica `“` `”` no arquivo | PASS |
| CT-04 | RN-09 | `author_url` absoluto (`https://quotes.toscrape.com/author/...`), nenhum `/author/` relativo | PASS |

Total esperado: `4 PASS, 0 FAIL`.

Se o CT-03 falhar, confira o regex `[^“”]+` da coluna `text` do `ExtractTable` no flow convertido (ponto a validar
em `notas-conversao.md`).
