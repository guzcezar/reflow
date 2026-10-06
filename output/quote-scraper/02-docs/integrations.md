# Integrações

| Sistema | Forma de interação | Detalhe | Credencial (referência) | Usado em | Evidência |
|---|---|---|---|---|---|
| quotes.toscrape.com | UI web (scraping) | HTTP GET das páginas (`requests`, timeout 10 s) e leitura do HTML com BeautifulSoup: seletores `div.quote`, `span.text`, `small.author`, `a.tag`, `a[href^='/author']`, `li.next a` | nenhuma (site público) | UC-01, UC-02 | `main.py:22`, `main.py:24`, `main.py:26`, `main.py:29-32`, `main.py:36` |
| Sistema de arquivos local | arquivo | Escrita de `quotes.csv` | nenhuma | UC-03 | `main.py:12`, `main.py:45-48` |

Formas de interação: `API REST`, `API SOAP`, `UI web`, `UI web (scraping)`, `UI desktop`, `terminal`, `SAP GUI`,
`arquivo`, `e-mail`, `API não convencional` (descrever).

## Observações
- O scraping é feito por HTTP direto, sem navegador: não há login, cliques nem execução de JavaScript (`main.py:22`, `main.py:24`).
- Dependências declaradas: `requests>=2.31.0` e `beautifulsoup4>=4.12.0` (`requirements.txt`).
