# Fontes de dados

| Fonte | Tipo | Objeto (tabela/aba/pasta) | Leitura/Escrita | Usado em | Evidência |
|---|---|---|---|---|---|
| quotes.csv | arquivo CSV | `quotes.csv` na pasta do script | E | UC-03 | `main.py:12`, `main.py:45-48` |

> O inventário não registrou fontes de dados (`data_sources: []`). A gravação do CSV foi identificada na leitura do código. O site quotes.toscrape.com é tratado como integração (ver [integrations.md](integrations.md)).

## Detalhes
### quotes.csv
- **Conexão**: caminho local `Path(__file__).parent / "quotes.csv"` (`main.py:12`). Não há credenciais.
- **Queries/Operações**: abre o arquivo em modo escrita (`"w"`), o que sobrescreve o conteúdo anterior. Encoding UTF-8 e `newline=""` (`main.py:45`). Grava o cabeçalho e uma linha por citação com `csv.DictWriter` (`main.py:46-48`).
- **Colunas**:
  | Coluna | Conteúdo | Evidência |
  |---|---|---|
  | `text` | texto da citação, sem as aspas tipográficas | `main.py:29` |
  | `author` | nome do autor | `main.py:30` |
  | `tags` | tags separadas por `\|` | `main.py:31` |
  | `author_url` | link absoluto da página do autor | `main.py:32` |
- **Observações**: o repositório já contém um `quotes.csv` com 102 linhas, provavelmente de uma execução anterior [inferido]. O processo não lê esse arquivo, apenas o sobrescreve.
