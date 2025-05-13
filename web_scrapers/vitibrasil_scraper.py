from bs4 import BeautifulSoup
import requests
import json

class VitibrasilScraper:

    url_comercializacao = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'

    def __init__(self):
        pass  

    def scrape_comercializacao(self):
        """Faz o scraping da aba de Comercialização e extrai os dados da tabela."""
        try:
            response = requests.get(self.url_comercializacao)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find('table', class_='tb_base')
            if not table:
                print("Tabela 'tb_base' não encontrada na página.")
                return None

            headers = [th.text.strip() for th in table.thead.find_all('th')]
            data = []
            rows = table.tbody.find_all('tr')

            current_item = None
            for row in rows:
                cells = row.find_all('td', class_=['tb_item', 'tb_subitem'])
                if len(cells) == 2:
                    produto_cell = cells[0]
                    quantidade_cell = cells[1]

                    produto = produto_cell.text.strip()
                    quantidade = quantidade_cell.text.strip()

                    if 'tb_item' in produto_cell['class']:
                        current_item = {'Produto': produto, 'Quantidade (L.)': quantidade, 'subitens': []}
                        data.append(current_item)
                    elif current_item and 'tb_subitem' in produto_cell['class']:
                        current_item['subitens'].append({'Produto': produto, 'Quantidade (L.)': quantidade})

            return data

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {self.url_comercializacao}: {e}")
            return None
