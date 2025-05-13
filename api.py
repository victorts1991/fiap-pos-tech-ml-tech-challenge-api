import datetime
import json
from flask import Flask, jsonify, request
from flasgger import Swagger
import requests
from bs4 import BeautifulSoup
import jwt
from functools import wraps
from web_scrapers.vitibrasil_scraper import VitibrasilScraper

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
                type: array
                items:
                  type: string
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
    url = 'https://www.embrapa.br/uva-e-vinho/producao'
    return extrair_tabela(url)

@app.route('/processamento', methods=['GET'])
def processamento():
    """
    Endpoint para extrair a tabela da página de processamento.
    ---
    responses:
      200:
        description: Dados da tabela de processamento.
        schema:
          type: object
          properties:
            tabela:
              type: array
              items:
                type: array
                items:
                  type: string
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
    url = 'https://www.embrapa.br/uva-e-vinho/processamento'
    return extrair_tabela(url)

@app.route('/exportacao', methods=['GET'])
def exportacao():
    """
    Endpoint para extrair a tabela da página de exportação.
    ---
    responses:
      200:
        description: Dados da tabela de exportação.
        schema:
          type: object
          properties:
            tabela:
              type: array
              items:
                type: array
                items:
                  type: string
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
    url = 'https://www.embrapa.br/uva-e-vinho/exportacao'
    return extrair_tabela(url)

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


@app.route('/comercializacao', methods=['GET'])
def comercializacao():
  # 
  try:
    scraper = VitibrasilScraper()
    dados_comercializacao = scraper.scrape_comercializacao()
    dados_json = json.dumps(dados_comercializacao, indent=4, ensure_ascii=False)
    return jsonify({
        "dados": dados_json
    })
  except Exception as e:
    return jsonify({ 
        "error": str(e)
    }), 500
    

#- /importacao

@app.route('/hello-world', methods=['GET'])
@token_required
def hello_world():
  return 'OK'

if __name__ == '__main__':
    app.run(debug=True)