"""Crawler de quotes.toscrape.com: coleta todas as citações e grava quotes.csv nesta pasta."""

import csv
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://quotes.toscrape.com/"
OUTPUT = Path(__file__).parent / "quotes.csv"
MAX_PAGES = 10  # trava: nunca lê mais que isso, mesmo que o site cresça
DELAY_SECONDS = 0.5  # pausa educada entre páginas


def crawl() -> list[dict]:
    quotes = []
    url = START_URL
    for _ in range(MAX_PAGES):
        print(f"Lendo {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # falha alto: nunca grava um resultado parcial sem avisar
        soup = BeautifulSoup(response.text, "html.parser")

        for div in soup.select("div.quote"):
            quotes.append(
                {
                    "text": div.select_one("span.text").get_text(strip=True).strip("“”"),
                    "author": div.select_one("small.author").get_text(strip=True),
                    "tags": "|".join(a.get_text(strip=True) for a in div.select("a.tag")),
                    "author_url": urljoin(url, div.select_one("a[href^='/author']")["href"]),
                }
            )

        next_link = soup.select_one("li.next a")
        if not next_link:
            break
        url = urljoin(url, next_link["href"])
        time.sleep(DELAY_SECONDS)
    return quotes


def save(quotes: list[dict]) -> None:
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "author", "tags", "author_url"])
        writer.writeheader()
        writer.writerows(quotes)


def main() -> None:
    quotes = crawl()
    if not quotes:
        raise SystemExit("Nenhuma citação encontrada.")
    save(quotes)
    print(f"{len(quotes)} citações gravadas em {OUTPUT}")


if __name__ == "__main__":
    main()
