from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time

class VitibrasilScraper:

    url_comercializacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'
    url_producao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02'

    url_processamento_viniferas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03'
    url_americanas_hibridas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03'
    url_uvas_de_mesa = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03'
    url_sem_classificacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03'

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_processamento(self):
        return {
            "viniferas": self._scrape_tabela_com_categorias(self.url_processamento_viniferas),
            "americanas_hibridas": self._scrape_tabela_com_categorias(self.url_americanas_hibridas),
            "uvas_de_mesa": self._scrape_tabela_com_categorias(self.url_uvas_de_mesa),
            "sem_classificacao": self._scrape_tabela_com_categorias(self.url_sem_classificacao, sem_classificacao=True)
        }

    def _scrape_tabela_com_categorias(self, url, sem_classificacao=False):
        try:
            self.driver.get(url)
            time.sleep(3)
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            titulo = soup.find("p", string=lambda x: x and "[" in x and "]" in x)
            ano = None
            if titulo:
                match = re.search(r"\[(\d{4})\]", titulo.get_text())
                if match:
                    ano = match.group(1)

            tabela = None
            for t in soup.find_all("table"):
                primeira_linha = t.find("tr")
                if not primeira_linha:
                    continue
                cabecalho = [th.get_text(strip=True).upper() for th in primeira_linha.find_all(["th", "td"])]
                if ("CULTIVAR" in cabecalho and "QUANTIDADE (KG)" in cabecalho) or ("SEM DEFINIÇÃO" in cabecalho and "QUANTIDADE (KG)" in cabecalho):
                    tabela = t
                    break

            if not tabela:
                return []

            dados = []
            tipo_atual = None

            for linha in tabela.find_all("tr"):
                colunas = linha.find_all("td")

                if len(colunas) == 1:
                    texto = colunas[0].get_text(strip=True)
                    if texto.upper() not in ["CULTIVAR", "QUANTIDADE (KG)", "TOTAL", "DOWNLOAD", "TOPO"]:
                        tipo_atual = texto
                    continue

                if len(colunas) == 2:
                    cultivar = colunas[0].get_text(strip=True)
                    quantidade = colunas[1].get_text(strip=True)

                    if not cultivar or not quantidade:
                        continue

                    if cultivar.isupper() and quantidade.replace('.', '').replace('-', '').isdigit():
                        tipo_atual = cultivar

                    dados.append({
                        "ano": ano,
                        "cultivar": cultivar,
                        "quantidade_kg": quantidade,
                        "tipo": tipo_atual if not sem_classificacao else "SEM CLASSIFICACAO"
                    })
            return dados

        except Exception as e:
            print(f"Erro ao processar URL {url}: {e}")
            return []

    def __del__(self):
        if self.driver:
            self.driver.quit()
