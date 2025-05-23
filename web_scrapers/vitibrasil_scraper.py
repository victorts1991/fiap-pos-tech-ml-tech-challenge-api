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

    # Configuracao para os Mocks
    useMock = False
    url_base_for_mocks = "C:/FIAP/Tech Challenge/fiap-pos-tech-ml-tech-challenge-api/web_scrapers/mocks/"
    # url_base_for_mocks = "file:///Users/mac/Desktop/dev/fiap-pos-tech-ml-tech-challenge-api/web_scrapers/mocks/"

    CHROMEDRIVER_PATH_LOCAL = "/Users/mac/Downloads/chromedriver-mac-x64/chromedriver" 
    CHROME_BINARY_PATH_LOCAL = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" 

    # URLs
    url_producao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02'
    url_processamento_viniferas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03'
    url_americanas_hibridas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03'
    url_uvas_de_mesa = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03'
    url_sem_classificacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03'
    url_comercializacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'
    url_importacao_vinhos_de_mesa = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_05"
    url_importacao_espumantes = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_05"
    url_importacao_uvas_frescas = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_05"
    url_importacao_uvas_passas = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_05"
    url_importacao_suco_de_uva = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_05&opcao=opt_05"
    url_exportacao_vinhos_de_mesa = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_06"
    url_exportacao_espumantes = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_06"
    url_exportacao_uvas_frescas = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_06"
    url_exportacao_suco_de_uva = "http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_06"

    # URL's Mock
    url_producao_mock = f"{url_base_for_mocks}producao.html"
    url_processamento_viniferas_mock = f"{url_base_for_mocks}processamento_viniferas.html"
    url_americanas_hibridas_mock = f"{url_base_for_mocks}processamento_americanas_hibridas.html"
    url_uvas_de_mesa_mock = f"{url_base_for_mocks}processamento_uvas_de_mesa.html"
    url_sem_classificacao_mock = f"{url_base_for_mocks}processamento_sem_classificacao.html"
    url_comercializacao_mock = f"{url_base_for_mocks}comercializacao.html"
    url_importacao_vinhos_de_mesa_mock = f"{url_base_for_mocks}importacao_vinhos_de_mesa.html"
    url_importacao_espumantes_mock = f"{url_base_for_mocks}importacao_espumantes.html"
    url_importacao_uvas_frescas_mock = f"{url_base_for_mocks}importacao_uvas_frescas.html"
    url_importacao_uvas_passas_mock = f"{url_base_for_mocks}importacao_uvas_passas.html"
    url_importacao_suco_de_uva_mock = f"{url_base_for_mocks}importacao_suco_de_uva.html"
    url_exportacao_vinhos_de_mesa_mock = f"{url_base_for_mocks}exportacao_vinhos_de_mesa.html"
    url_exportacao_espumantes_mock = f"{url_base_for_mocks}exportacao_espumantes.html"
    url_exportacao_uvas_frescas_mock = f"{url_base_for_mocks}exportacao_uvas_frescas.html"
    url_exportacao_suco_de_uva_mock = f"{url_base_for_mocks}exportacao_suco_de_uva.html"


    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0')
        
        # Opcional: Adicionar log de console do navegador para depuração
        # chrome_options.add_argument('--enable-logging')
        # chrome_options.add_argument('--v=1') # Verbose logging

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
        if hasattr(self, 'driver') and self.driver: # Verifica se driver existe e não é None
            try:
                self.driver.quit()
            except WebDriverException as e:
                print(f"Aviso: Erro ao fechar o WebDriver: {e}")


    def scrape_producao(self, max_retries=3, retry_delay=5):
        url = self.url_producao_mock if self.useMock else self.url_producao
        return self._scrape_tabela(url, 'producao', max_retries, retry_delay)

    def scrape_processamento_viniferas(self, max_retries=3, retry_delay=5):
        url = self.url_processamento_viniferas_mock if self.useMock else self.url_processamento_viniferas
        return self._scrape_tabela(url, 'processamento_viniferas', max_retries, retry_delay)

    def scrape_processamento_americanas_hibridas(self, max_retries=3, retry_delay=5):
        url = self.url_americanas_hibridas_mock if self.useMock else self.url_americanas_hibridas
        return self._scrape_tabela(url, 'processamento_americanas_hibridas', max_retries, retry_delay)

    def scrape_processamento_uvas_de_mesa(self, max_retries=3, retry_delay=5):
        url = self.url_uvas_de_mesa_mock if self.useMock else self.url_uvas_de_mesa
        return self._scrape_tabela(url, 'processamento_uvas_de_mesa', max_retries, retry_delay)

    def scrape_processamento_sem_classificacao(self, max_retries=3, retry_delay=5):
        url = self.url_sem_classificacao_mock if self.useMock else self.url_sem_classificacao
        return self._scrape_tabela(url, 'processamento_sem_classificacao', max_retries, retry_delay)
    
    def scrape_comercializacao(self, max_retries=3, retry_delay=5):
        url = self.url_comercializacao_mock if self.useMock else self.url_comercializacao
        return self._scrape_tabela(url, 'comercializacao', max_retries, retry_delay)

    def scrape_importacao_vinhos_de_mesa(self, max_retries=3, retry_delay=5):
        url = self.url_importacao_vinhos_de_mesa_mock if self.useMock else self.url_importacao_vinhos_de_mesa
        return self._scrape_tabela_simples(url, 'importacao_vinhos_de_mesa', max_retries, retry_delay)
    
    def scrape_importacao_espumantes(self, max_retries=3, retry_delay=5):
        url = self.url_importacao_espumantes_mock if self.useMock else self.url_importacao_espumantes
        return self._scrape_tabela_simples(url, 'importacao_espumantes', max_retries, retry_delay)

    def scrape_importacao_uvas_frescas(self, max_retries=3, retry_delay=5):
        url = self.url_importacao_uvas_frescas_mock if self.useMock else self.url_importacao_uvas_frescas
        return self._scrape_tabela_simples(url, 'importacao_uvas_frescas', max_retries, retry_delay)

    def scrape_importacao_uvas_passas(self, max_retries=3, retry_delay=5):
        url = self.url_importacao_uvas_passas_mock if self.useMock else self.url_importacao_uvas_passas
        return self._scrape_tabela_simples(url, 'importacao_uvas_passas', max_retries, retry_delay)

    def scrape_importacao_suco_de_uva(self, max_retries=3, retry_delay=5):
        url = self.url_importacao_suco_de_uva_mock if self.useMock else self.url_importacao_suco_de_uva
        return self._scrape_tabela_simples(url, 'importacao_suco_de_uva', max_retries, retry_delay)

    def scrape_exportacao_vinhos_de_mesa(self, max_retries=3, retry_delay=5):
        url = self.url_exportacao_vinhos_de_mesa_mock if self.useMock else self.url_exportacao_vinhos_de_mesa
        return self._scrape_tabela_simples(url, 'exportacao_vinhos_de_mesa', max_retries, retry_delay)

    def scrape_exportacao_espumantes(self, max_retries=3, retry_delay=5):
        url = self.url_exportacao_espumantes_mock if self.useMock else self.url_exportacao_espumantes
        return self._scrape_tabela_simples(url, 'exportacao_espumantes', max_retries, retry_delay)

    def scrape_exportacao_uvas_frescas(self, max_retries=3, retry_delay=5):
        url = self.url_exportacao_uvas_frescas_mock if self.useMock else self.url_exportacao_uvas_frescas
        return self._scrape_tabela_simples(url, 'exportacao_uvas_frescas', max_retries, retry_delay)

    def scrape_exportacao_suco_de_uva(self, max_retries=3, retry_delay=5):
        url = self.url_exportacao_suco_de_uva_mock if self.useMock else self.url_exportacao_suco_de_uva
        return self._scrape_tabela_simples(url, 'exportacao_suco_de_uva', max_retries, retry_delay)


    def _scrape_tabela(self, url, categoria, max_retries=3, retry_delay=5, ano='2023'):
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1} de {max_retries} para URL: {url}")
                self.driver.get(url)
                
                # Espera explícita pela tabela com classe 'tb_dados'
                # Aumentei o tempo de espera máximo para 15 segundos
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tb_dados"))
                )
                time.sleep(1) # Pequena pausa extra para renderização final, se necessário

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
                        # Não levantar ScrapingError aqui se houver dados, mas o site pode ter retornado vazio
                        # Se realmente não houver dados, o retorno abaixo lidará com isso.
                    
                    return {"categoria": categoria, "dados": dados}
                else:
                    # Esta parte 'else' não deve ser alcançada se o WebDriverWait for bem-sucedido
                    # Se o WebDriverWait falhar, ele já levantará um TimeoutException
                    print(f"ERRO: Tabela com classe 'tb_dados' não encontrada na URL {url} na tentativa {attempt + 1} (após WebDriverWait).")
                    # Para depuração: levantar um erro para cair no except e capturar o HTML
                    raise ScrapingError(f"Tabela 'tb_dados' não encontrada após espera na URL: {url}") 
            
            except TimeoutException as e: 
                print(f"Tempo limite excedido ao esperar pela tabela em {url} na tentativa {attempt + 1}: {e}")
                # --- Bloco de depuração no erro ---
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do Timeout (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro de Timeout: {capture_e}")
                # --- Fim do bloco de depuração ---
                time.sleep(retry_delay)
                if attempt == max_retries - 1: # Se for a última tentativa, re-raise o erro para o chamador
                    raise ScrapingError(f"Tempo limite excedido após {max_retries} tentativas na URL: {url}") from e
            
            except Exception as e:
                print(f"Erro inesperado ao processar URL {url} na tentativa {attempt + 1}: {e}")
                # --- Bloco de depuração no erro ---
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do erro inesperado (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro inesperado: {capture_e}")
                # --- Fim do bloco de depuração ---
                time.sleep(retry_delay)
                if attempt == max_retries - 1: # Se for a última tentativa, re-raise o erro para o chamador
                    raise ScrapingError(f"Erro inesperado após {max_retries} tentativas na URL: {url}") from e

        # Este raise só será atingido se todas as tentativas falharem sem lançar uma exceção específica tratada acima
        raise ScrapingError(f"Falha ao encontrar a tabela com classe 'tb_dados' após {max_retries} tentativas na URL: {url} (verifique logs para mais detalhes).")


    def _scrape_tabela_simples(self, url, categoria, max_retries=3, retry_delay=5, ano='2023'):
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1} de {max_retries} para URL simples: {url}")
                self.driver.get(url)
                
                # Espera explícita pela tabela com classe 'tb_dados'
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
                # --- Bloco de depuração no erro ---
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do Timeout (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro de Timeout: {capture_e}")
                # --- Fim do bloco de depuração ---
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Tempo limite excedido após {max_retries} tentativas na URL simples: {url}") from e
            
            except Exception as e:
                print(f"[Tentativa {attempt + 1}] Erro inesperado: {e}")
                # --- Bloco de depuração no erro ---
                try:
                    page_html_on_error = self.driver.page_source
                    print(f"HTML da página no momento do erro inesperado (primeiras 1000 chars):\n{page_html_on_error[:1000]}...")
                except WebDriverException as capture_e:
                    print(f"Falha ao capturar HTML no erro inesperado: {capture_e}")
                # --- Fim do bloco de depuração ---
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Erro inesperado após {max_retries} tentativas na URL simples: {url}") from e

        raise ScrapingError(f"Falha ao processar tabela simples da categoria {categoria} após {max_retries} tentativas. (verifique logs para mais detalhes).")