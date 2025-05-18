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
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    if username == TEST_USERNAME and password == TEST_PASSWORD:
        token = create_token(username)
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401

@app.route('/producao', methods=['GET'])
@token_required
def producao():
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = scraper.scrape_producao()

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

@app.route('/processamento/<categoria>', methods=['GET'])
@token_required
def processamento(categoria):
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = None

        if categoria == 'viniferas':
            resultado_scraping = scraper.scrape_processamento_viniferas()
        elif categoria == 'americanas_hibridas':
            resultado_scraping = scraper.scrape_processamento_americanas_hibridas()
        elif categoria == 'uvas_de_mesa':
            resultado_scraping = scraper.scrape_processamento_uvas_de_mesa()
        elif categoria == 'sem_classificacao':
            resultado_scraping = scraper.scrape_processamento_sem_classificacao()
       
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

@app.route('/comercializacao', methods=['GET'])
@token_required
def comercializacao():
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = scraper.scrape_comercializacao()

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
    
@app.route('/importacao/<categoria>', methods=['GET'])
@token_required
def importacao(categoria):
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = None

        if categoria == 'vinhos_de_mesa':
            resultado_scraping = scraper.scrape_importacao_vinhos_de_mesa()
        elif categoria == 'espumantes':
            resultado_scraping = scraper.scrape_importacao_espumantes()
        elif categoria == 'uvas_frescas':
            resultado_scraping = scraper.scrape_importacao_uvas_frescas()
        elif categoria == 'uvas_passas':
            resultado_scraping = scraper.scrape_importacao_uvas_passas()
        elif categoria == 'suco_de_uva':
            resultado_scraping = scraper.scrape_importacao_suco_de_uva()
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
    
@app.route('/exportacao/<categoria>', methods=['GET'])
@token_required
def exportacao(categoria):
    try:
        scraper = VitibrasilScraper()
        resultado_scraping = None

        if categoria == 'vinhos_de_mesa':
            resultado_scraping = scraper.scrape_exportacao_vinhos_de_mesa()
        elif categoria == 'espumantes':
            resultado_scraping = scraper.scrape_exportacao_espumantes()
        elif categoria == 'uvas_frescas':
            resultado_scraping = scraper.scrape_exportacao_uvas_frescas()
        elif categoria == 'suco_de_uva':
            resultado_scraping = scraper.scrape_exportacao_suco_de_uva()
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

@app.route('/health', methods=['GET'])
@token_required
def hello_world():
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)