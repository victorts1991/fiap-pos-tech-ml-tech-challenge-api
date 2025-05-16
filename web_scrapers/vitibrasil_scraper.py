from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_processamento_viniferas(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_processamento_viniferas, 'viniferas', max_retries, retry_delay)

    def scrape_processamento_americanas_hibridas(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_americanas_hibridas, 'americanas_hibridas', max_retries, retry_delay)

    def scrape_processamento_uvas_de_mesa(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_uvas_de_mesa, 'uvas_de_mesa', max_retries, retry_delay)

    def scrape_processamento_sem_classificacao(self, max_retries=3, retry_delay=5):
        return self._scrape_tabela(self.url_sem_classificacao, 'sem_classificacao', max_retries, retry_delay)

    def _scrape_tabela(self, url, categoria, max_retries=3, retry_delay=5):
        for attempt in range(max_retries):
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

                tabela = soup.find("table", class_="tb_dados")

                if tabela:
                    dados = []
                    linhas = tabela.find_all("tr")[1:]  # Ignora a linha de cabeçalho
                    cabecalho_tabela = [th.get_text(strip=True) for th in tabela.find("tr").find_all(["th", "td"])]

                    for linha in linhas:
                        celulas = linha.find_all("td")
                        if len(celulas) == len(cabecalho_tabela):
                            item = {"ano": ano, "categoria": categoria}
                            has_data = False
                            for i, coluna in enumerate(cabecalho_tabela):
                                value = celulas[i].get_text(strip=True)
                                item[coluna.lower().replace(' ', '_').replace('(', '').replace(')', '')] = value
                                if value and value != '-':  # Considera valores não vazios ou traços como dados
                                    has_data = True
                            if has_data:
                                dados.append(item)

                    if not dados and categoria != 'sem_classificacao':
                        raise ScrapingError(f"A tabela com classe 'tb_dados' para a categoria '{categoria}' foi encontrada, mas não contém dados significativos. Possível erro de carregamento.")

                    return {"categoria": categoria, "dados": dados}
                else:
                    print(f"Tabela com classe 'tb_dados' não encontrada na URL {url} na tentativa {attempt + 1}.")
                    time.sleep(retry_delay)

            except Exception as e:
                print(f"Erro ao processar URL {url} na tentativa {attempt + 1}: {e}")
                time.sleep(retry_delay)
                raise

        raise ScrapingError(f"Falha ao encontrar a tabela com classe 'tb_dados' após {max_retries} tentativas na URL: {url}")

    def __del__(self):
        if self.driver:
            self.driver.quit()