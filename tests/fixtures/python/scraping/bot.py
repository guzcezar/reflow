import requests
from bs4 import BeautifulSoup
from selenium import webdriver

cfg = {"url": "x"}
url = cfg.get("url")
session = requests.Session()
html = session.get("https://portal.example/lista.aspx").text
soup = BeautifulSoup(html, "html.parser")
rows = soup.select("table tr")

def helper(driver):
    driver.find_element("id", "x").click()
