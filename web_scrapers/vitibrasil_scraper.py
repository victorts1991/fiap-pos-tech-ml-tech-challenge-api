from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time

class ScrapingError(Exception):
    """Exceção personalizada para erros de scraping."""
    pass

class VitibrasilScraper:

    url_comercializacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'
    url_producao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02'

    url_processamento_viniferas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03'
    #url_processamento_viniferas = 'file:///Users/mac/Desktop/dev/teste%202/processamento_viniferas.html'
    url_americanas_hibridas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03'
    # url_americanas_hibridas = 'file:///Users/mac/Desktop/dev/teste%202/processamento_americanas_hibridas.html'
    url_uvas_de_mesa = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03'
    # url_uvas_de_mesa = 'file:///Users/mac/Desktop/dev/teste%202/processamento_uvas_de_mesa.html'
    url_sem_classificacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03'
    #url_sem_classificacao = 'file:///Users/mac/Desktop/dev/teste%202/processamento_sem_classificacao.html'
    

    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Deixe comentado por enquanto
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--remote-debugging-port=9222')


        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_processamento_viniferas(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_processamento_viniferas, 'viniferas', max_retries, retry_delay)

    def scrape_processamento_americanas_hibridas(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_americanas_hibridas, 'americanas_hibridas', max_retries, retry_delay)

    def scrape_processamento_uvas_de_mesa(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_uvas_de_mesa, 'uvas_de_mesa', max_retries, retry_delay)

    def scrape_processamento_sem_classificacao(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_sem_classificacao, 'sem_classificacao', max_retries, retry_delay)

    def scrape_producao(self, max_retries=3, retry_delay=5):
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1}: acessando página de produção...")
                self.driver.get(self.url_producao)

                # Espera até que qualquer tabela apareça na página
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                html = self.driver.page_source

                # Salva o HTML para debug
                with open("debug_producao.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("✅ HTML salvo em debug_producao.html")

                soup = BeautifulSoup(html, 'html.parser')

                # Extrai o ano do título (ex: [2023])
                titulo = soup.find("p", string=lambda x: x and "[" in x and "]" in x)
                ano = None
                if titulo:
                    match = re.search(r"\[(\d{4})\]", titulo.get_text())
                    if match:
                        ano = match.group(1)

<<<<<<< HEAD
                tabela = None
                for t in soup.find_all("table"):
                    linhas = t.find_all("tr")
                    if not linhas:
                        continue
                    cabecalho = linhas[0]
                    colunas = [
                        c.get_text(strip=True).lower().replace("(l)", "").replace("(litros)", "").strip()
                        for c in cabecalho.find_all(["th", "td"])
                    ]
                    if any("produto" in c for c in colunas) and any("quantidade" in c for c in colunas):
                        tabela = t
                        break
=======
                tabela = soup.find("table", class_="tb_dados")
>>>>>>> origin/main

                if not tabela:
                    raise ScrapingError("Tabela de produção não encontrada.")

                linhas = tabela.find_all("tr")
                cabecalho = [th.get_text(strip=True) for th in linhas[0].find_all(["th", "td"])]
                dados = []

<<<<<<< HEAD
                for linha in linhas[1:]:  # ignora o cabeçalho
                    colunas = linha.find_all("td")
                    if len(colunas) != len(cabecalho):
                        continue  # ignora linhas malformadas

                    item = {"ano": ano}
                    for i in range(len(cabecalho)):
                        chave = (
                            cabecalho[i]
                            .strip()
                            .lower()
                            .replace(" ", "_")
                            .replace("(", "")
                            .replace(")", "")
                        )
                        valor = colunas[i].get_text(strip=True)
                        item[chave] = valor
                    dados.append(item)

                return dados
=======
                    if not dados and categoria != 'sem_classificacao':
                        raise ScrapingError(f"A tabela com classe 'tb_dados' para a categoria '{categoria}' foi encontrada, mas não contém dados significativos. Possível erro de carregamento.")

                    return {"categoria": categoria, "dados": dados}
                else:
                    print(f"Tabela com classe 'tb_dados' não encontrada na URL {url} na tentativa {attempt + 1}.")
                    time.sleep(retry_delay)
>>>>>>> origin/main

            except Exception as e:
                print(f"[Erro - Produção] Tentativa {attempt + 1}: {e}")
                time.sleep(retry_delay)
                raise

<<<<<<< HEAD
        raise ScrapingError("Erro ao obter os dados da produção após várias tentativas.")
=======
        raise ScrapingError(f"Falha ao encontrar a tabela com classe 'tb_dados' após {max_retries} tentativas na URL: {url}")

    def __del__(self):
        if self.driver:
            self.driver.quit()
>>>>>>> origin/main
