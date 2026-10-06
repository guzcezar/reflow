import os

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

PORTAL_URL = "https://nfse.prefeitura.example/consulta"


def consultar(cnpj):
    driver = webdriver.Chrome()
    driver.get(PORTAL_URL)
    driver.find_element(By.ID, "usuario").send_keys(os.getenv("PORTAL_USER"))
    driver.find_element(By.ID, "consultar").click()
    linhas = driver.find_elements(By.CSS_SELECTOR, "table#notas tr")
    requests.post("https://hooks.example/notify", json={"cnpj": cnpj})
    return [linha.text for linha in linhas]
