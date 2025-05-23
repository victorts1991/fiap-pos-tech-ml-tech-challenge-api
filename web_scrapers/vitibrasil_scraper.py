from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException # Importar WebDriverException também para erros gerais do driver
from bs4 import BeautifulSoup
import re
import time
import os

class ScrapingError(Exception):
    """Exceção personalizada para erros de scraping."""
    pass

class VitibrasilScraper:

    useLocal = False

    CHROMEDRIVER_PATH_LOCAL = "/Users/mac/Downloads/chromedriver-mac-x64/chromedriver" 
    CHROME_BINARY_PATH_LOCAL = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" 

    urls = {
        # URLs originais
        "url_producao": 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02&ano=',
        "url_processamento_viniferas": 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03&ano=',
        "url_americanas_hibridas": 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03&ano=',
        "url_uvas_de_mesa": 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03&ano=',
        "url_sem_classificacao": 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03&ano=',
        "url_comercializacao": 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04&ano=',
        "url_importacao_vinhos_de_mesa": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_05&ano=",
        "url_importacao_espumantes": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_05&ano=",
        "url_importacao_uvas_frescas": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_05&ano=",
        "url_importacao_uvas_passas": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_05&ano=",
        "url_importacao_suco_de_uva": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_05&opcao=opt_05&ano=",
        "url_exportacao_vinhos_de_mesa": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_06&ano=",
        "url_exportacao_espumantes": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_06&ano=",
        "url_exportacao_uvas_frescas": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_06&ano=",
        "url_exportacao_suco_de_uva": "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_06&ano=",

        # URLs ScrapingBee
        "url_producao_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fopcao%3Dopt_02%26ano=",
        "url_processamento_viniferas_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_01%26opcao%3Dopt_03%26ano=",
        "url_americanas_hibridas_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_02%26opcao%3Dopt_03%26ano=",
        "url_uvas_de_mesa_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_03%26opcao%3Dopt_03%26ano=",
        "url_sem_classificacao_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_04%26opcao%3Dopt_03%26ano=",
        "url_comercializacao_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fopcao%3Dopt_04%26ano=",
        "url_importacao_vinhos_de_mesa_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_01%26opcao%3Dopt_05%26ano=",
        "url_importacao_espumantes_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_02%26opcao%3Dopt_05%26ano=",
        "url_importacao_uvas_frescas_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_03%26opcao%3Dopt_05%26ano=",
        "url_importacao_uvas_passas_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_04%26opcao%3Dopt_05%26ano=",
        "url_importacao_suco_de_uva_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_05%26opcao%3Dopt_05%26ano=",
        "url_exportacao_vinhos_de_mesa_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_01%26opcao%3Dopt_06%26ano=",
        "url_exportacao_espumantes_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_02%26opcao%3Dopt_06%26ano=",
        "url_exportacao_uvas_frescas_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_03%26opcao%3Dopt_06%26ano=",
        "url_exportacao_suco_de_uva_scrapingbee": f"https://app.scrapingbee.com/api/v1?api_key={os.environ.get('SCRAPINGBEE_API_KEY')}&render_js=false&url=http%3A%2F%2Fvitibrasil.cnpuv.embrapa.br%2Findex.php%3Fsubopcao%3Dsubopt_04%26opcao%3Dopt_06%26ano="
    }

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--verbose')
        chrome_options.add_argument('--log-path=/tmp/chromedriver.log')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')

        # --- Lógica para alternar entre ambiente local e Heroku ---
        is_heroku = os.environ.get('DYNO') is not None 

        if is_heroku:
            # **** CAMINHOS EXATOS ENCONTRADOS NO HEROKU ****
            CHROME_BINARY_PATH = "/app/.chrome-for-testing/chrome-linux64/chrome"
            CHROMEDRIVER_PATH = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"
            print("Rodando no Heroku: Usando caminhos de buildpack.")
        else:
            # **** CAMINHOS PARA AMBIENTE LOCAL ****
            
            CHROMEDRIVER_PATH = self.CHROMEDRIVER_PATH_LOCAL 
            CHROME_BINARY_PATH = self.CHROME_BINARY_PATH_LOCAL

            print(f"Rodando localmente: Usando chromedriver de {CHROMEDRIVER_PATH}")
            # Verifica se os binários existem e são acessíveis (para depuração local)
            if not os.path.exists(CHROME_BINARY_PATH):
                print(f"AVISO: Chrome binário não encontrado localmente em: {CHROME_BINARY_PATH}. Isso pode causar problemas se você não tiver o Chrome instalado ou o caminho estiver incorreto.")
            if not os.path.exists(CHROMEDRIVER_PATH):
                raise ScrapingError(f"ChromeDriver não encontrado localmente em: {CHROMEDRIVER_PATH}. Baixe a versão correta para o seu Chrome e coloque-o aqui.")

        # Define o caminho do binário do Chrome para as opções do Selenium
        chrome_options.binary_location = CHROME_BINARY_PATH

        if os.path.exists(CHROMEDRIVER_PATH) and not os.access(CHROMEDRIVER_PATH, os.X_OK):
             os.chmod(CHROMEDRIVER_PATH, 0o755)

        try:
            service = Service(executable_path=CHROMEDRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except WebDriverException as e:
            raise ScrapingError(f"Falha ao inicializar o WebDriver: {str(e)}. Verifique se o ChromeDriver e o Chrome estão instalados e compatíveis.")

    def __del__(self):
        # Garante que o driver seja fechado ao final para liberar recursos
        if hasattr(self, 'driver') and self.driver: 
            try:
                self.driver.quit()
            except WebDriverException as e:
                print(f"Aviso: Erro ao fechar o WebDriver: {e}")

    def get_url(self, base_url_name, ano='2023'):
        chosen_url = (
            self.urls[base_url_name] if self.useLocal
            else self.urls[f"{base_url_name}_scrapingbee"]
        )
        
        return f"{chosen_url}{ano}"

    def scrape_producao(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_producao", ano)
        return self._scrape_tabela(url, 'producao', max_retries, retry_delay, ano)

    def scrape_processamento_viniferas(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_processamento_viniferas", ano)
        return self._scrape_tabela(url, 'processamento_viniferas', max_retries, retry_delay, ano)

    def scrape_processamento_americanas_hibridas(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_americanas_hibridas", ano)
        return self._scrape_tabela(url, 'processamento_americanas_hibridas', max_retries, retry_delay, ano)

    def scrape_processamento_uvas_de_mesa(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_uvas_de_mesa", ano)
        return self._scrape_tabela(url, 'processamento_uvas_de_mesa', max_retries, retry_delay, ano)

    def scrape_processamento_sem_classificacao(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_sem_classificacao", ano)
        return self._scrape_tabela(url, 'processamento_sem_classificacao', max_retries, retry_delay, ano)

    def scrape_comercializacao(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_comercializacao", ano)
        return self._scrape_tabela(url, 'comercializacao', max_retries, retry_delay, ano)

    def scrape_importacao_vinhos_de_mesa(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_importacao_vinhos_de_mesa", ano)
        return self._scrape_tabela_simples(url, 'importacao_vinhos_de_mesa', max_retries, retry_delay, ano)

    def scrape_importacao_espumantes(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_importacao_espumantes", ano)
        return self._scrape_tabela_simples(url, 'importacao_espumantes', max_retries, retry_delay, ano)

    def scrape_importacao_uvas_frescas(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_importacao_uvas_frescas", ano)
        return self._scrape_tabela_simples(url, 'importacao_uvas_frescas', max_retries, retry_delay, ano)

    def scrape_importacao_uvas_passas(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_importacao_uvas_passas", ano)
        return self._scrape_tabela_simples(url, 'importacao_uvas_passas', max_retries, retry_delay, ano)

    def scrape_importacao_suco_de_uva(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_importacao_suco_de_uva", ano)
        return self._scrape_tabela_simples(url, 'importacao_suco_de_uva', max_retries, retry_delay, ano)

    def scrape_exportacao_vinhos_de_mesa(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_exportacao_vinhos_de_mesa", ano)
        return self._scrape_tabela_simples(url, 'exportacao_vinhos_de_mesa', max_retries, retry_delay, ano)

    def scrape_exportacao_espumantes(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_exportacao_espumantes", ano)
        return self._scrape_tabela_simples(url, 'exportacao_espumantes', max_retries, retry_delay, ano)

    def scrape_exportacao_uvas_frescas(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_exportacao_uvas_frescas", ano)
        return self._scrape_tabela_simples(url, 'exportacao_uvas_frescas', max_retries, retry_delay, ano)

    def scrape_exportacao_suco_de_uva(self, max_retries=3, retry_delay=5, ano="2023"):
        url = self.get_url("url_exportacao_suco_de_uva", ano)
        return self._scrape_tabela_simples(url, 'exportacao_suco_de_uva', max_retries, retry_delay, ano)

    def _scrape_tabela(self, url, categoria, max_retries=3, retry_delay=5, ano='2023'):
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1} de {max_retries} para URL: {url}")
                self.driver.get(url)
                
                # Espera pela tabela com classe 'tb_dados'
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tb_dados"))
                )
                time.sleep(1) 

                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

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
                                item_principal = {"ano": ano, "categoria": categoria}
                                for i, coluna in enumerate(cabecalho_tabela):
                                    item_principal[coluna.lower().replace(' ', '_').replace('(', '').replace(')', '')] = celulas[i].get_text(strip=True)
                                item_principal['subitem'] = []
                                dados.append(item_principal)

                            elif 'tb_subitem' in classes_primeira_celula and item_principal is not None:
                                subitem = {}
                                for i, coluna in enumerate(cabecalho_tabela):
                                    subitem[coluna.lower().replace(' ', '_').replace('(', '').replace(')', '')] = celulas[i].get_text(strip=True)
                                item_principal['subitem'].append(subitem)

                    if not dados and categoria != 'sem_classificacao':
                        print(f"A tabela com classe 'tb_dados' para a categoria '{categoria}' foi encontrada, mas não contém dados significativos.")                        
                    
                    return {"categoria": categoria, "dados": dados}
                else:
                    print(f"ERRO: Tabela com classe 'tb_dados' não encontrada na URL {url} na tentativa {attempt + 1} (após WebDriverWait).")
                    raise ScrapingError(f"Tabela 'tb_dados' não encontrada após espera na URL: {url}") 
            
            except TimeoutException as e: 

                print(f"Tempo limite excedido ao esperar pela tabela em {url} na tentativa {attempt + 1}: {e}")
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do Timeout (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro de Timeout: {capture_e}")

                time.sleep(retry_delay)
                if attempt == max_retries - 1: 
                    raise ScrapingError(f"Tempo limite excedido após {max_retries} tentativas na URL: {url}") from e
            
            except Exception as e:
                print(f"Erro inesperado ao processar URL {url} na tentativa {attempt + 1}: {e}")
                
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do erro inesperado (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro inesperado: {capture_e}")
                
                time.sleep(retry_delay)
                if attempt == max_retries - 1: 
                    raise ScrapingError(f"Erro inesperado após {max_retries} tentativas na URL: {url}") from e

        raise ScrapingError(f"Falha ao encontrar a tabela com classe 'tb_dados' após {max_retries} tentativas na URL: {url} (verifique logs para mais detalhes).")


    def _scrape_tabela_simples(self, url, categoria, max_retries=3, retry_delay=5, ano='2023'):
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1} de {max_retries} para URL simples: {url}")
                self.driver.get(url)
                
                # Espera pela tabela com classe 'tb_dados'
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tb_dados"))
                )
                time.sleep(1)

                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                tabela = soup.find("table", class_="tb_dados")
                if not tabela:
                    print(f"ERRO: Tabela com classe 'tb_dados' não encontrada na URL simples {url} na tentativa {attempt + 1} (após WebDriverWait).")
                    raise ScrapingError(f"Tabela 'tb_dados' não encontrada após espera na URL simples: {url}")

                linhas = tabela.find_all("tr")
                dados = []
                item_principal = {
                    "ano": ano,
                    "categoria": categoria,
                    "subitem": []
                }

                for linha in linhas[1:]:
                    colunas = linha.find_all("td")
                    if len(colunas) == 3:
                        pais = colunas[0].get_text(strip=True)
                        quantidade = colunas[1].get_text(strip=True)
                        valor = colunas[2].get_text(strip=True)

                        item_principal['subitem'].append({
                            "pais": pais,
                            "quantidade_kg": quantidade,
                            "valor_usd": valor
                        })

                if item_principal['subitem']:
                    dados.append(item_principal)

                return {"categoria": categoria, "dados": dados}

            except TimeoutException as e: 
                print(f"[Tentativa {attempt + 1}] Tempo limite excedido ao esperar pela tabela simples: {e}")
                
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do Timeout (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro de Timeout: {capture_e}")
                
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Tempo limite excedido após {max_retries} tentativas na URL simples: {url}") from e
            
            except Exception as e:
                print(f"[Tentativa {attempt + 1}] Erro inesperado: {e}")
                
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do erro inesperado (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro inesperado: {capture_e}")
                
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Erro inesperado após {max_retries} tentativas na URL simples: {url}") from e

        raise ScrapingError(f"Falha ao processar tabela simples da categoria {categoria} após {max_retries} tentativas. (verifique logs para mais detalhes).")