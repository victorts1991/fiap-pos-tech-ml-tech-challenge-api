import datetime
import json
from flask import Flask, jsonify, request
from flasgger import Swagger
import requests
from bs4 import BeautifulSoup
import jwt
from functools import wraps
from web_scrapers.vitibrasil_scraper import VitibrasilScraper, ScrapingError
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
    'title': 'Fiap Post Tech Machine Learning API Tech Challenge',
    'uiversion': 3
}

swagger = Swagger(app) 

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
                token = auth_header.split()[1]
            except IndexError:
                return jsonify({'error': 'Token de autorização inválido'}), 401

        if not token:
            return jsonify({'error': 'Token de autorização ausente'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
    return decorated

@app.route("/login", methods=["POST"])
def login():
    """
    Endpoint para login e geração de token JWT.
    ---
    tags:
      - Autenticação
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: admin
              password:
                type: string
                example: secret
    responses:
      200:
        description: Token JWT gerado com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
      401:
        description: Credenciais inválidas
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Credenciais inválidas
    """
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    if username == TEST_USERNAME and password == TEST_PASSWORD:
        token = create_token(username)
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401


@app.route('/producao/<ano>', methods=['GET'])
@token_required
def producao(ano):
    """
    Endpoint para obter dados de produção de uvas e derivados.
    ---
    tags:
      - Produção
    security:
      - Bearer: []
    responses:
      200:
        description: Dados de produção retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                categoria:
                  type: string
                  example: producao
                dados:
                  type: array
                  items:
                    type: object
      500:
        description: Erro ao obter os dados de produção
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
    """
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = scraper.scrape_producao(ano)

        if resultado_scraping and resultado_scraping.get("dados"):
            return jsonify(resultado_scraping)
        elif resultado_scraping:
            return jsonify({"categoria": "producao", "dados": []})
        else:
            return jsonify({"erro": "Não foi possível obter os dados de processamento para a categoria 'producao'"}), 500

    except ScrapingError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500


@app.route('/processamento/<categoria>/<ano>', methods=['GET'])
@token_required
def processamento(categoria, ano):
    """
    Endpoint para obter dados de processamento de uvas por categoria.
    ---
    tags:
      - Processamento
    parameters:
      - name: categoria
        in: path
        required: true
        schema:
          type: string
          enum: [viniferas, americanas_hibridas, uvas_de_mesa, sem_classificacao]
        description: Categoria de processamento a ser consultada.
    security:
      - Bearer: []
    responses:
      200:
        description: Dados de processamento retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                categoria:
                  type: string
                dados:
                  type: array
                  items:
                    type: object
      400:
        description: Categoria inválida
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Categoria inválida
      500:
        description: Erro inesperado ao processar os dados
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
    """
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = None

        if categoria == 'viniferas':
            resultado_scraping = scraper.scrape_processamento_viniferas(ano)
        elif categoria == 'americanas_hibridas':
            resultado_scraping = scraper.scrape_processamento_americanas_hibridas(ano)
        elif categoria == 'uvas_de_mesa':
            resultado_scraping = scraper.scrape_processamento_uvas_de_mesa(ano)
        elif categoria == 'sem_classificacao':
            resultado_scraping = scraper.scrape_processamento_sem_classificacao(ano)
        else:
            return jsonify({"error": "Categoria inválida"}), 400

        if resultado_scraping and resultado_scraping.get("dados"):
            return jsonify(resultado_scraping)
        elif resultado_scraping:
            return jsonify({"categoria": categoria, "dados": []})
        else:
            return jsonify({"erro": f"Não foi possível obter os dados de processamento para a categoria '{categoria}'"}), 500

    except ScrapingError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500


@app.route('/comercializacao/<ano>', methods=['GET'])
@token_required
def comercializacao(ano):
    """
    Endpoint para obter dados de comercialização de derivados de uva.
    ---
    tags:
      - Comercialização
    security:
      - Bearer: []
    responses:
      200:
        description: Dados de comercialização retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                categoria:
                  type: string
                  example: comercializacao
                dados:
                  type: array
                  items:
                    type: object
      500:
        description: Erro ao obter dados de comercialização
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
    """
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = scraper.scrape_comercializacao(ano)

        if resultado_scraping and resultado_scraping.get("dados"):
            return jsonify(resultado_scraping)
        elif resultado_scraping:
            return jsonify({"categoria": "producao", "dados": []})
        else:
            return jsonify({"erro": "Não foi possível obter os dados de processamento para a categoria 'comercializacao'"}), 500

    except ScrapingError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500

    
@app.route('/importacao/<categoria>/<ano>', methods=['GET'])
@token_required
def importacao(categoria, ano):
    """
    Endpoint para obter dados de importação por categoria.
    ---
    tags:
      - Importação
    parameters:
      - name: categoria
        in: path
        required: true
        schema:
          type: string
          enum: [vinhos_de_mesa, espumantes, uvas_frescas, uvas_passas, suco_de_uva]
        description: Categoria dos produtos importados
    security:
      - Bearer: []
    responses:
      200:
        description: Dados de importação retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                categoria:
                  type: string
                dados:
                  type: array
                  items:
                    type: object
      400:
        description: Categoria inválida
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
      500:
        description: Erro ao obter dados de importação
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
    """
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = None

        if categoria == 'vinhos_de_mesa':
            resultado_scraping = scraper.scrape_importacao_vinhos_de_mesa(ano)
        elif categoria == 'espumantes':
            resultado_scraping = scraper.scrape_importacao_espumantes(ano)
        elif categoria == 'uvas_frescas':
            resultado_scraping = scraper.scrape_importacao_uvas_frescas(ano)
        elif categoria == 'uvas_passas':
            resultado_scraping = scraper.scrape_importacao_uvas_passas(ano)
        elif categoria == 'suco_de_uva':
            resultado_scraping = scraper.scrape_importacao_suco_de_uva(ano)
        else:
            return jsonify({"error": "Categoria inválida"}), 400

        if resultado_scraping and resultado_scraping.get("dados"):
            return jsonify(resultado_scraping)
        elif resultado_scraping:
            return jsonify({"categoria": categoria, "dados": []})
        else:
            return jsonify({"erro": f"Não foi possível obter os dados de importação para a categoria '{categoria}'"}), 500

    except ScrapingError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500

    
@app.route('/exportacao/<categoria>/<ano>', methods=['GET'])
@token_required
def exportacao(categoria, ano):
    """
    Endpoint para obter dados de exportação por categoria.
    ---
    tags:
      - Exportação
    parameters:
      - name: categoria
        in: path
        required: true
        schema:
          type: string
          enum: [vinhos_de_mesa, espumantes, uvas_frescas, suco_de_uva]
        description: Categoria dos produtos exportados
    security:
      - Bearer: []
    responses:
      200:
        description: Dados de exportação retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                categoria:
                  type: string
                dados:
                  type: array
                  items:
                    type: object
      400:
        description: Categoria inválida
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
      500:
        description: Erro ao obter dados de exportação
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
    """
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = None

        if categoria == 'vinhos_de_mesa':
            resultado_scraping = scraper.scrape_exportacao_vinhos_de_mesa(ano)
        elif categoria == 'espumantes':
            resultado_scraping = scraper.scrape_exportacao_espumantes(ano)
        elif categoria == 'uvas_frescas':
            resultado_scraping = scraper.scrape_exportacao_uvas_frescas(ano)
        elif categoria == 'suco_de_uva':
            resultado_scraping = scraper.scrape_exportacao_suco_de_uva(ano)
        else:
            return jsonify({"error": "Categoria inválida"}), 400

        if resultado_scraping and resultado_scraping.get("dados"):
            return jsonify(resultado_scraping)
        elif resultado_scraping:
            return jsonify({"categoria": categoria, "dados": []})
        else:
            return jsonify({"erro": f"Não foi possível obter os dados de exportação para a categoria '{categoria}'"}), 500

    except ScrapingError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def hello_world():
    return 'OK'

@app.route('/')
def index():
    return 'API está funcionando!'


if __name__ == '__main__':
    app.run(debug=True)