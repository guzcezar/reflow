# Regras de negócio

| ID | Regra | Onde se aplica | Evidência |
|---|---|---|---|
| RN-01 | A coleta começa sempre em `https://quotes.toscrape.com/` | UC-02 | `main.py:11`, `main.py:19` |
| RN-02 | São lidas no máximo 10 páginas por execução, "mesmo que o site cresça" | UC-02 | `main.py:13`, `main.py:20` |
| RN-03 | A navegação termina quando a página não tem link "Next" (`li.next a`) | UC-02 | `main.py:36-38` |
| RN-04 | Há uma pausa de 0,5 s entre páginas ("pausa educada") | UC-02 | `main.py:14`, `main.py:40` |
| RN-05 | Cada requisição tem timeout de 10 s | UC-01 | `main.py:22` |
| RN-06 | Qualquer erro HTTP interrompe o processo, para "nunca gravar um resultado parcial sem avisar" | UC-01 | `main.py:23` |
| RN-07 | O texto da citação é gravado sem as aspas tipográficas “ ” das pontas e sem espaços extras | UC-01 | `main.py:29` |
| RN-08 | As tags de uma citação são unidas num único campo, separadas por `\|` | UC-01 | `main.py:31` |
| RN-09 | O link do autor é convertido em URL absoluta a partir da página atual | UC-01 | `main.py:32` |
| RN-10 | Se nenhuma citação for coletada, o processo termina com erro "Nenhuma citação encontrada." e não grava o arquivo | UC-03 | `main.py:53-54` |
| RN-11 | O arquivo de saída é sempre `quotes.csv` na pasta do script e é sobrescrito a cada execução | UC-03 | `main.py:12`, `main.py:45` |
| RN-12 | Ordem das colunas no CSV: `text`, `author`, `tags`, `author_url` | UC-03 | `main.py:46` |

Não há filtros, deduplicação nem validações de conteúdo das citações no código.
