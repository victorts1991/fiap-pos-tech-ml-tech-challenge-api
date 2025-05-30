import requests
from bs4 import BeautifulSoup
import re
import time
import os

class ScrapingError(Exception):
    """Exceção personalizada para erros de scraping."""
    pass

class VitibrasilScraper:

    useLocal = False

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
        # Nenhuma inicialização de WebDriver necessária para requests
        pass

    def __del__(self):
        # Nenhuma ação de fechamento de driver necessária
        pass

    def get_url(self, base_url_name, ano='2023'):
        chosen_url = (
            self.urls[base_url_name] if self.useLocal
            else self.urls[f"{base_url_name}_scrapingbee"]
        )
        
        return f"{chosen_url}{ano}"

    def _fetch_page_content(self, url, max_retries, retry_delay):
        """Fetches the HTML content of a given URL using requests."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1} de {max_retries} para URL: {url}")
                response = requests.get(url, headers=headers, timeout=15) # Increased timeout
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                return response.content
            except requests.exceptions.Timeout as e:
                print(f"Tempo limite excedido ao requisitar {url} na tentativa {attempt + 1}: {e}")
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Tempo limite excedido após {max_retries} tentativas na URL: {url}") from e
            except requests.exceptions.RequestException as e:
                print(f"Erro ao requisitar {url} na tentativa {attempt + 1}: {e}")
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Erro de requisição após {max_retries} tentativas na URL: {url}") from e
        return None # Should not be reached if an exception is always raised on last attempt

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
        html = self._fetch_page_content(url, max_retries, retry_delay)
        if not html:
            raise ScrapingError(f"Não foi possível obter o conteúdo da página para {url}")

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
            raise ScrapingError(f"Tabela com classe 'tb_dados' não encontrada na URL: {url}") 

    def _scrape_tabela_simples(self, url, categoria, max_retries=3, retry_delay=5, ano='2023'):
        html = self._fetch_page_content(url, max_retries, retry_delay)
        if not html:
            raise ScrapingError(f"Não foi possível obter o conteúdo da página para {url}")

        soup = BeautifulSoup(html, 'html.parser')

        tabela = soup.find("table", class_="tb_dados")
        if not tabela:
            raise ScrapingError(f"Tabela com classe 'tb_dados' não encontrada na URL simples: {url}")

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