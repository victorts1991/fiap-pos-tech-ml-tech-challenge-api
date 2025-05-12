from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
import requests
from bs4 import BeautifulSoup

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
        return jsonify({"error": "Item not found"}), 500

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

if __name__ == '__main__':
    app.run(debug=True)