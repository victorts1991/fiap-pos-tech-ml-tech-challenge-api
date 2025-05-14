from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class VitibrasilScraper:

    url_comercializacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'
    url_producao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02'

    url_processamento_viniferas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_01&opcao=opt_03'
    url_americanas_hibridas = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_02&opcao=opt_03'
    url_uvas_de_mesa = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_03&opcao=opt_03'
    url_sem_classificacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao=subopt_04&opcao=opt_03'

    def __init__(self):
        # Configura o Chrome em modo headless (sem abrir janela)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_comercializacao(self):
        return self._scrape_tabela_com_categorias(self.url_comercializacao)

    def scrape_producao(self):
        return self._scrape_tabela_com_categorias(self.url_producao)
    
    def scrape_processamento(self):
        viniferas = self._scrape_tabela_com_categorias(self.url_processamento_viniferas)
        americanas_hibridas = self._scrape_tabela_com_categorias(self.url_americanas_hibridas)
        uvas_de_mesa = self._scrape_tabela_com_categorias(self.url_uvas_de_mesa)
        sem_classificacao = self._scrape_tabela_com_categorias(self.url_sem_classificacao)

        return {
            "viniferas": viniferas,
            "americanas_hibridas": americanas_hibridas,
            "uvas_de_mesa": uvas_de_mesa,
            "sem_classificacao": sem_classificacao
        }

    def _scrape_tabela_com_categorias(self, url):
        try:
            self.driver.get(url)

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Encontrando a tabela certa
            table = soup.find('table', class_=lambda c: c and 'tb_base' in c and 'tb_dados' in c)
            if not table:
                print("Tabela com dados não encontrada.")
                return []

            rows = table.find_all('tr')
            data = []
            current_categoria = None

            for row in rows:
                cols = row.find_all('td')
                if not cols or len(cols) < 2:
                    continue

                nome = cols[0].text.strip()
                quantidade = cols[1].text.strip()
                classes = cols[0].get('class', [])

                if 'tb_item' in classes:
                    current_categoria = {
                        'categoria': nome,
                        'quantidade': quantidade,
                        'subcategorias': []
                    }
                    data.append(current_categoria)
                elif 'tb_subitem' in classes and current_categoria:
                    current_categoria['subcategorias'].append({
                        'subcategoria': nome,
                        'quantidade': quantidade
                    })

            return data

        except Exception as e:
            print(f"Erro durante scraping: {e}")
            return None

    def __del__(self):
        if self.driver:
            self.driver.quit()
