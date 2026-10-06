# quote-scraper

Crawler de [quotes.toscrape.com](https://quotes.toscrape.com), um site público feito para praticar scraping. Percorre
todas as páginas (seguindo o link "Next") e grava as citações em `quotes.csv`, nesta mesma pasta.

Versão simplificada de [galatadesalegn/web_scraper](https://github.com/galatadesalegn/web_scraper), usada como
projeto de exemplo do reflow.

## Executar

```bash
pip install -r requirements.txt
python main.py
```

## Saída: `quotes.csv`

| Coluna | Conteúdo |
|---|---|
| `text` | texto da citação, sem as aspas tipográficas |
| `author` | autor |
| `tags` | tags separadas por `\|` |
| `author_url` | link absoluto da página do autor |
