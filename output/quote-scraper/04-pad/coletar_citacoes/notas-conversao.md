# Notas de conversão: coletar_citacoes

Veredito `PAD` (`03-classification/classification.md`). O processo inteiro (UC-01, UC-02 e UC-03) foi convertido para um
único `Main.robin`. O flow não usa UI elements (`appmask`): navega por URL e extrai com seletor CSS literal.

## Legado × flow

| Legado | Flow | Observação |
|---|---|---|
| `main.py:11-14` (constantes) | bloco `SET cfg_...` | `cfg_url_inicial`, `cfg_url_site`, `cfg_max_paginas` = 10, `cfg_timeout_pagina_segundos` = 10. A pausa de 0,5 s ficou literal (`WAIT 0.5`), porque o snippet validado de `WAIT` só usa número. |
| `main.py:12` (`OUTPUT` na pasta do script) | `cfg_caminho_saida` = `C:\Users\Public\Documents\quotes.csv` | Pasta que sempre existe no Windows (regra 1). Também resolve o R-07: o caminho fica configurável. |
| `main.py:19-20`, `main.py:36-39` (link "Next") | `LOOP numero_pagina FROM 1 TO cfg_max_paginas` com a URL `/page/%numero_pagina%/` | Paginação por URL (regra 5). O link "Next" não é procurado (o `ExtractTable` dá erro se o elemento não existir). |
| `main.py:21` (`print "Lendo"`) | — | Saída de console, sem equivalente no PAD. Não foi criado log (regra 10). |
| `main.py:22-24` (`requests.get` + BeautifulSoup) | `GoToWebPage` no Edge | O browser substitui o GET direto. |
| `main.py:26-34` (`select` / `select_one`) | um `ExtractTable` com `Control` em `div.quote` | Colunas por índice (`citacao[0]`...`[3]`, forma que rodou): `span.text` (Own Text com regex), `small.author` (Own Text), `div.tags > meta.keywords` (atributo `content`) e `span > a` (Href). |
| `main.py:32` (`urljoin`) | `StartsWith(..., '/')` e prefixo `cfg_url_site` | Só age se o PAD devolver o `Href` relativo. Em geral ele já vem absoluto. |
| `main.py:40` (`time.sleep`) | `WAIT 0.5` entre páginas | Pulado na última iteração, como no legado (que sai antes do `sleep`). |
| `main.py:45-48` (`csv.DictWriter`) | cabeçalho com `Overwrite` na página 1 e uma linha por citação com `Append` | Padrão "Escrever CSV" da whitelist. |
| `main.py:53-54` (`SystemExit`) | `IF out_total_citacoes = 0`: `out_status = 'ERRO'` e `out_error_message` | Erro de negócio por `IF` (regra 4). Ver RN-10 abaixo. |
| `main.py:56` (`print` do total) | `out_total_citacoes` e `out_caminho_csv` | Saída de console virou variável `out_`. |

## Simplificações
- O CSV é gravado página a página, em vez de juntar tudo em memória e gravar no fim. Não há ação na whitelist para
  acumular as linhas (DataTable) e a regra 10 proíbe arquivo temporário.
- Os `print` de progresso (`main.py:21`, `main.py:56`) não viraram log em arquivo (regra 10). O total vai em
  `out_total_citacoes`.
- A página 1 é carregada duas vezes (no `LaunchEdge` com `cfg_url_inicial` e no primeiro `GoToWebPage` em `/page/1/`).
  Isso mantém o loop uniforme.
- As tags vêm do `meta.keywords` de cada citação (`content` = tags separadas por vírgula), em vez de juntar cada
  `a.tag`. Uma coluna do `ExtractTable` devolve só um valor por linha.
- Todos os campos do CSV vão entre aspas duplas. O `csv` do Python só põe aspas quando é preciso. Os dois formatos são
  CSV válidos e equivalentes.

## Divergências do legado
- **Fim da paginação (RN-03, `main.py:36-38`)**: o legado para quando não há link "Next". O flow percorre as páginas
  1 a `cfg_max_paginas` pela URL. No site atual (10 páginas) o resultado é o mesmo. Se o site tiver menos páginas que o
  limite, a página sem citações faz o `ExtractTable` dar erro ("Data extraction element not found") e o flow para.
- **RN-06 / RN-10 / R-04 (tudo ou nada, `main.py:23`, `main.py:52-55`)**: o legado nunca grava um CSV parcial. O flow
  grava página a página, então uma falha na página N (N > 1) deixa o `quotes.csv` com as páginas anteriores, e o flow
  para com o erro do PAD (avisa, mas o arquivo fica parcial). Se a página 1 falhar ou não tiver citações, o
  `ExtractTable` dá erro antes de qualquer gravação e o `quotes.csv` anterior fica intacto. Pergunta para o dono do
  processo (já em `02-docs/risks.md`): resultado parcial é aceitável?
- **`raise_for_status` (`main.py:23`)**: o browser não expõe o status HTTP. Falha de carregamento ou timeout para o
  flow com o erro do PAD. Uma página 4xx/5xx sem `div.quote` faz o `ExtractTable` dar erro.
- **R-02 (`main.py:29-32`)**: o legado aborta se faltar um elemento numa citação. O `ExtractTable` devolve célula vazia
  e segue. Comportamento natural do PAD, mais tolerante; não tratado como bug.
- **R-03 (limite de 10 páginas)**: reproduzido (`cfg_max_paginas` = 10). A dúvida entre bug e regra continua aberta em
  `02-docs/risks.md`. Para mudar, basta alterar o `cfg_`.
- **R-05, R-06**: reproduzidos (sobrescreve sem backup e sem retry), como no legado.

## TODOs (ações não mapeadas)
1. **Trocar `,` por `|` nas tags** (`main.py:31`, RN-08). `Text.Replace` não existe no PAD com esse nome. Sem a ação,
   as tags saem separadas por vírgula, dentro de aspas. Precisa da ação de substituir texto do PAD, validada via Ctrl+C.
2. **Dobrar as aspas `"` internas do texto** (`main.py:48`, escape do CSV). Uma citação tem aspas retas internas
   (Dumbledore, linha 92 do `quotes.csv` legado). Sem o escape, essa linha sai como CSV malformado. Precisa da mesma
   ação de substituir texto.

## Pontos a validar no primeiro paste/execução
- O regex `[^“”]+` na coluna `text` do `ExtractTable`: o PAD deve devolver o texto sem as aspas tipográficas (RN-07).
  Se devolver a célula vazia ou o texto inteiro, troque por `''''''` e registre aqui.
- O atributo `content` do `meta.keywords`: confirme no PAD o nome do atributo.
- Acesso às colunas por índice (`citacao[0]`) dentro de `%...%` no `TextToWrite`.
- `IF numero_pagina < cfg_max_paginas` (comparador `<` ainda não colado no PAD).
