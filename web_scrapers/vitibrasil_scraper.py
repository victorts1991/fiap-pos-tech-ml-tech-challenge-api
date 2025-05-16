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

    # Configuracao para os Mocks
    useMock = True
    url_base_for_mocks = 'file:///Users/mac/Desktop/dev/fiap-pos-tech-ml-tech-challenge-api/web_scrapers/mocks/'

    # URLs
    url_comercializacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'
    url_producao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02'
    url_processamento_viniferas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03'
    url_americanas_hibridas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03'
    url_uvas_de_mesa = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03'
    url_sem_classificacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03'

    # URL's Mock
    url_producao_mock = f"{url_base_for_mocks}producao.html"
    url_processamento_viniferas_mock = f"{url_base_for_mocks}processamento_viniferas.html"
    url_americanas_hibridas_mock = f"{url_base_for_mocks}processamento_americanas_hibridas.html"
    url_uvas_de_mesa_mock = f"{url_base_for_mocks}processamento_uvas_de_mesa.html"
    url_sem_classificacao_mock = f"{url_base_for_mocks}processamento_sem_classificacao.html"

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_producao(self, max_retries=3, retry_delay=5):
        url = self.url_producao
        if self.useMock: 
            url = self.url_producao_mock

        return self._scrape_tabela(url, 'producao', max_retries, retry_delay)
    
    def scrape_processamento_viniferas(self, max_retries=3, retry_delay=5):
        url = self.url_processamento_viniferas
        if self.useMock: 
            url = self.url_processamento_viniferas_mock
        return self._scrape_tabela(url, 'viniferas', max_retries, retry_delay)

    def scrape_processamento_americanas_hibridas(self, max_retries=3, retry_delay=5):
        url = self.url_americanas_hibridas
        if self.useMock: 
            url = self.url_americanas_hibridas_mock
        return self._scrape_tabela(url, 'americanas_hibridas', max_retries, retry_delay)

    def scrape_processamento_uvas_de_mesa(self, max_retries=3, retry_delay=5):
        url = self.url_uvas_de_mesa
        if self.useMock: 
            url = self.url_uvas_de_mesa_mock
        return self._scrape_tabela(url, 'uvas_de_mesa', max_retries, retry_delay)

    def scrape_processamento_sem_classificacao(self, max_retries=3, retry_delay=5):
        url = self.url_sem_classificacao
        if self.useMock: 
            url = self.url_sem_classificacao_mock
        return self._scrape_tabela(url, 'sem_classificacao', max_retries, retry_delay)

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
                    thead = tabela.find("thead")
                    tbody = tabela.find("tbody")
                    cabecalho_tabela = [th.get_text(strip=True) for th in thead.find_all("th")] if thead else []
                    linhas = tbody.find_all("tr") if tbody else []
                    item_principal = None

                    for linha in linhas:
                        celulas = linha.find_all("td")
                        if len(celulas) == len(cabecalho_tabela):
                            primeira_celula = celulas[0]
                            classes_primeira_celula = primeira_celula.get('class', [])

                            if 'tb_item' in classes_primeira_celula:
                                # Nova linha de item principal
                                item_principal = {"ano": ano, "categoria": categoria}
                                for i, coluna in enumerate(cabecalho_tabela):
                                    item_principal[coluna.lower().replace(' ', '_').replace('(', '').replace(')', '')] = celulas[i].get_text(strip=True)
                                item_principal['subitem'] = []
                                dados.append(item_principal)

                            elif 'tb_subitem' in classes_primeira_celula and item_principal is not None:
                                # Linha de subitem para o item principal anterior
                                subitem = {}
                                for i, coluna in enumerate(cabecalho_tabela):
                                    subitem[coluna.lower().replace(' ', '_').replace('(', '').replace(')', '')] = celulas[i].get_text(strip=True)
                                item_principal['subitem'].append(subitem)

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