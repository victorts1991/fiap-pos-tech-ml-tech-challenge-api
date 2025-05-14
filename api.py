import datetime
import json
from flask import Flask, jsonify, request
from flasgger import Swagger
import requests
from bs4 import BeautifulSoup
import jwt
from functools import wraps
from web_scrapers.vitibrasil_scraper import VitibrasilScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re  

JWT_SECRET = "MEUSEGREDOAQUI"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600
 
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'My Flask API',
    'uiversion': 3
}

swagger = Swagger(app) 

#Função genérica para extrair tabela HTML
def extrair_tabela(url):
    try:
        response = requests.get(url)
        response.raise_for_status()   # Isso lança erro se status não for 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": e}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    tabelas = soup.find_all('table')

    if not tabelas:
        return jsonify({"error": "Item not found"}), 404

    dados = []
    if tabelas:
        linhas = tabelas[0].find_all('tr')
        for linha in linhas:
            colunas = linha.find_all(['td','th'])
            dados.append([col.text.strip() for col in colunas])

    return jsonify({'tabela': dados})

TEST_USERNAME = "admin"
TEST_PASSWORD = "secret"

def create_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split()[1] # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token de autorização inválido'}), 401

        if not token:
            return jsonify({'error': 'Token de autorização ausente'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # Você pode adicionar lógica aqui para verificar se o usuário existe, etc.
            # Se quiser passar o username para a função de rota:
            # return f(current_user=data['username'], *args, **kwargs)
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    if username == TEST_USERNAME and password == TEST_PASSWORD:
        token = create_token(username)
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401
    
@app.route('/producao', methods=['GET'])
def producao():
    """
    Endpoint para extrair a tabela da página de produção.
    ---
    responses:
      200:
        description: Dados da tabela de produção.
        schema:
          type: object
          properties:
            tabela:
              type: array
              items:
                type: object
      404:
        description: Nenhuma tabela encontrada na página.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Nenhuma tabela encontrada"
      500:
        description: Erro ao acessar a URL.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Erro ao acessar a URL: ..."
    """
    scraper = VitibrasilScraper()
    dados = scraper.scrape_producao()

    if dados is None:
        return jsonify({'erro': 'Nenhuma tabela encontrada ou erro de acesso'}), 404

    return jsonify({'tabela': dados}), 200

@app.route('/processamento', methods=['GET'])
def processamento():
    """
    Endpoint para extrair e formatar os dados das tabelas de processamento de uvas:
    viníferas, americanas/híbridas, uvas de mesa e sem classificação.
    """
    try:
        scraper = VitibrasilScraper()
        dados_processamento = scraper.scrape_processamento()

        return jsonify({
            "processamento": dados_processamento
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/comercializacao', methods=['GET'])
def comercializacao():
  # 
  try:
    scraper = VitibrasilScraper()
    dados_comercializacao = scraper.scrape_comercializacao()
    return jsonify({
        "dados": dados_comercializacao
    })
  except Exception as e:
    return jsonify({ 
        "error": str(e)
    }), 500
    
@app.route('/importacao', methods=['GET'])
def importacao():
    """
    Endpoint para extrair e formatar os dados da tabela de importação de derivados de uva.
    """
    url = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        tabelas = soup.find_all("table")
        for tabela in tabelas:
            linhas = tabela.find_all("tr")
            if not linhas:
                continue

            cabecalho = [col.get_text(strip=True) for col in linhas[0].find_all(["th", "td"])]
            if "Países" in cabecalho and "Quantidade (Kg)" in cabecalho and "Valor (US$)" in cabecalho:
                dados = []
                for linha in linhas[1:]:
                    colunas_linha = linha.find_all("td")
                    if len(colunas_linha) == 3:
                        pais = colunas_linha[0].get_text(strip=True)
                        quantidade = colunas_linha[1].get_text(strip=True)
                        valor = colunas_linha[2].get_text(strip=True)
                        dados.append({
                            "pais": pais,
                            "quantidade_kg": quantidade,
                            "valor_usd": valor
                        })

                return jsonify({"importacoes": dados})

        return jsonify({"erro": "Tabela não encontrada"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    finally:
        driver.quit()

@app.route('/exportacao', methods=['GET'])
def exportacao():
    """
    Endpoint para extrair e formatar os dados da tabela de exportação de derivados de uva.
    """
    url = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extrai o ano do título (ex: [2024])
        titulo = soup.find("p", string=lambda x: x and "[" in x and "]" in x)
        ano = None
        if titulo:
            match = re.search(r"\[(\d{4})\]", titulo.get_text())
            if match:
                ano = match.group(1)

        tabelas = soup.find_all("table")
        tabela_dados = None

        for tabela in tabelas:
            linhas = tabela.find_all("tr")
            if not linhas:
                continue

            cabecalho = [col.get_text(strip=True) for col in linhas[0].find_all(["td", "th"])]
            if set(["Países", "Quantidade (Kg)", "Valor (US$)"]).issubset(set(cabecalho)):
                tabela_dados = tabela
                break

        if not tabela_dados:
            return jsonify({"erro": "Tabela de exportação não encontrada"}), 404

        dados = []

        for linha in tabela_dados.find_all("tr")[1:]:  # ignora cabeçalho
            colunas = linha.find_all("td")
            if len(colunas) != 3:
                continue

            pais = colunas[0].get_text(strip=True)
            quantidade = colunas[1].get_text(strip=True)
            valor = colunas[2].get_text(strip=True)

            # 🔍 Filtro para ignorar linhas com dados vazios ou decorativos
            if not pais or (quantidade == "-" and valor == "-"):
                continue

            dados.append({
                "ano": ano,
                "pais": pais,
                "quantidade_kg": quantidade,
                "valor_usd": valor
            })

        return jsonify({"exportacao": dados})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    finally:
        driver.quit()

@app.route('/hello-world', methods=['GET'])
@token_required
def hello_world():
  return 'OK'


@app.route('/')
def home():
    """
    Endpoint de boas-vindas da API.
    ---
    responses:
      200:
        description: Mensagem de boas-vindas e lista de endpoints.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "API Embrapa Vitivinicultura"
            endpoints:
              type: array
              items:
                type: string
                example: "/producao"
    """
    return jsonify({
        "mensagem": "API Embrapa Vitivinicultura",
        "endpoints": ["/producao", "/processamento", "/exportacao"]
    })




if __name__ == '__main__':
    app.run(debug=True)