# fiap-pos-tech-ml-tech-challenge-api

### Tech Challenge 1:
### Passos para a homologação dos professores da Fiap

---

## Deploy na plataforma Heroku

1.  **Crie uma conta no Heroku** em [heroku.com](https://www.heroku.com/).
2.  **Instale o Heroku CLI** (Command Line Interface) seguindo as instruções em [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli).
3.  **Faça login no Heroku CLI** no seu terminal:
    ```bash
    heroku login
    ```
4.  **Crie um novo aplicativo no Heroku** para o seu projeto (certifique-se de estar na raiz do seu projeto):
    ```bash
    heroku create pos-tech-ml-tech-challenge-api
    ```
    **Observação:** O Heroku exige nomes de aplicativos únicos globalmente. Se este nome já estiver em uso, o Heroku retornará um erro e você precisará escolher outro.
5.  **Configure os Buildpacks do Heroku:**
    Estes buildpacks são essenciais para instalar o Python, o Google Chrome e o ChromeDriver no ambiente do Heroku.
    ```bash
    heroku buildpacks:set heroku/python -a pos-tech-ml-tech-challenge-api
    heroku buildpacks:add [https://github.com/heroku/heroku-buildpack-chrome-for-testing](https://github.com/heroku/heroku-buildpack-chrome-for-testing) -a pos-tech-ml-tech-challenge-api
    ```
6.  **Gere sua Chave de API do Heroku:**
    * Acesse seu [Dashboard do Heroku](https://dashboard.heroku.com/).
    * Clique na sua foto de perfil (canto superior direito) e vá em **Account settings** (Configurações da conta).
    * Role a página até a seção **API Key** (Chave de API).
    * Clique em **Reveal** (Revelar) e **copie** a chave gerada.
7.  **Configure o Secret no GitHub Actions:**
    * No seu repositório do GitHub, vá em **Settings** (Configurações).
    * Clique em **Secrets and variables** > **Actions** (Segredos e variáveis > Ações).
    * Clique em **New repository secret** (Novo segredo do repositório).
    * **Nome:** `HEROKU_API_KEY`
    * **Valor:** Cole a chave de API do Heroku que você copiou.
    * Clique em **Add secret**.
8.  **Faça um push para a branch `main`:**
    Após configurar o secret e ter o seu workflow do GitHub Actions atualizado para o Heroku, qualquer commit na branch `main` irá acionar o pipeline do GitHub Actions, que fará o deploy automático do projeto na plataforma Heroku.

---

## Deploy em Localhost

1.  Após executar o `git clone`, execute os comandos abaixo na raiz do projeto:

    ```bash
    python3 -m venv venv

    source venv/bin/activate  # Unix/macOS
    # ou
    venv\Scripts\activate  # Windows

    pip install -r requirements.txt

    python3 api.py
    ```

---

## Swagger

Documentação em Swagger:

```
# Localhost
http://127.0.0.1:5000/apidocs

# Exemplo de como ficaria no Heroku
https://pos-tech-ml-tech-challenge-api-47e455659f67.herokuapp.com/apidocs/
```
