# fiap-pos-tech-ml-tech-challenge-api

### Tech Challenge 1:
### Passos para a homologação dos professores da Fiap

## Deploy na plataforma Vercel

1. Crie uma conta no Vercel;
2. Vá no menu de configurações da sua conta e após isso no menu Tokens;
3. Crie um token com o nome "GitHub Actions Deploy" e selecione o scopo do seu projeto;
4. Copie o token gerado e voltando ao seu repositório do Github, acesse o menu Settings->Secrets and Variables->Actions;
5. Crie um "Repository secrets" com o nome "VERCEL_TOKEN" e cole o valor do token gerado na plataforma Vercel;
6. Após isso, qualquer commit na branch main irá acionar o pipeline do Github Actions e será feito o deploy do projeto na plataforma Vercel;

## Deploy em Localhost

1. Após executar o git clone execute os comandos abaixo na raiz do projeto:

```
python3 -m venv venv

source venv/bin/activate  # Unix/macOS
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt

python3 api.py
```

## Swagger
Documentação em Swagger:

```
# Localhost
http://127.0.0.1:5000/apidocs

# Exemplo de como ficaria no Vercel
https://fiap-pos-tech-ml-tech-challenge-api.vercel.app/apidocs/
```
```
