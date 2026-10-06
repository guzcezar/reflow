# coletar_citacoes

Coleta as citações de https://quotes.toscrape.com/ (até 10 páginas) e grava `quotes.csv`.

## Pré-requisitos
- Microsoft Edge com a extensão **Microsoft Power Automate** instalada e ativa.
- Acesso à internet.

## Como rodar
1. No Power Automate Desktop, crie um desktop flow novo chamado `coletar_citacoes`.
2. Abra o subflow `Main`, clique na área de ações e cole o conteúdo inteiro de `Main.robin` (Ctrl+V).
3. Salve e rode.

Não precisa criar pasta, variável de input/output nem credencial.

## Resultado esperado
- `C:\Users\Public\Documents\quotes.csv` em UTF-8, com o cabeçalho `text,author,tags,author_url` e uma linha por
  citação (100 citações nas 10 páginas do site).
- Variáveis ao fim: `out_status` = `OK`, `out_total_citacoes` = 100 e `out_caminho_csv` com o caminho do CSV.
- Se uma página não carregar ou não tiver citações, o flow para com o erro do PAD.
