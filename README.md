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
    heroku config:set WEB_CONCURRENCY=1 -a pos-tech-ml-tech-challenge-api
    heroku config:set GUNICORN_TIMEOUT=60 -a pos-tech-ml-tech-challenge-api
    ```
6.  **Configure a Chave de API do ScrapingBee no Heroku:**
    Como o scraping no Heroku será feito via ScrapingBee, você precisa configurar sua chave de API como uma variável de ambiente.
    a. **Obtenha sua API Key do ScrapingBee:**
       * Acesse sua conta no [ScrapingBee](https://www.scrapingbee.com/).
       * Vá para o seu `Dashboard` ou `API Settings`. Sua chave de API estará visível lá. Copie-a.
    b. **Defina a variável de ambiente no Heroku:**
       No seu terminal, execute (substitua `SUA_API_KEY_SCRAPINGBEE` pela sua chave real):
       ```bash
       heroku config:set SCRAPINGBEE_API_KEY="SUA_API_KEY_SCRAPINGBEE" -a pos-tech-ml-tech-challenge-api
       ```
7.  **Gere sua Chave de API do Heroku (para GitHub Actions):**
    * Acesse seu [Dashboard do Heroku](https://dashboard.heroku.com/).
    * Clique na sua foto de perfil (canto superior direito) e vá em **Account settings** (Configurações da conta).
    * Role a página até a seção **API Key** (Chave de API).
    * Clique em **Reveal** (Revelar) e **copie** a chave gerada.
8.  **Configure os Secrets no GitHub Actions:**
    Você precisará configurar três Secrets no GitHub: um para a chave de API do Heroku, outro para o seu e-mail do Heroku e um terceiro para a chave de API do ScrapingBee.
    * No seu repositório do GitHub, vá em **Settings** (Configurações).
    * Clique em **Secrets and variables** > **Actions** (Segredos e variáveis > Ações).
    * Clique em **New repository secret** (Novo segredo do repositório) e crie os três secrets abaixo:
        * **Nome:** `HEROKU_API_KEY`
        * **Valor:** Cole a chave de API do Heroku que você copiou.
        * **Nome:** `HEROKU_EMAIL`
        * **Valor:** Digite o e-mail associado à sua conta Heroku.
        * **Nome:** `SCRAPINGBEE_API_KEY`
        * **Valor:** Cole a chave de API do ScrapingBee que você copiou.
    * Clique em **Add secret** para cada um.
9.  **Faça um push para a branch `develop`:**
    Após configurar os secrets e ter o seu workflow do GitHub Actions atualizado para o Heroku, qualquer commit na branch `develop` irá acionar o pipeline do GitHub Actions, que fará o deploy automático do projeto na plataforma Heroku.

---

## Deploy em Localhost

Para configurar e executar a API localmente, siga os passos abaixo:

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/victorts1991/fiap-pos-tech-ml-tech-challenge-api.git](https://github.com/victorts1991/fiap-pos-tech-ml-tech-challenge-api.git)
    cd fiap-pos-tech-ml-tech-challenge-api
    ```

2.  **Configurar Ambiente Python:**

    a. **Crie e ative um ambiente virtual:**

    ```bash
    python3 -m venv venv

    # Para Unix/macOS:
    source venv/bin/activate

    # Para Windows (CMD):
    # venv\Scripts\activate.bat

    # Para Windows (PowerShell):
    # venv\Scripts\Activate.ps1
    ```

    b. **Instale as dependências Python:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Chave de API do ScrapingBee (para Ambiente Local):**
    Para rodar a API localmente e testar o scraping, você precisará da chave de API do ScrapingBee configurada como uma variável de ambiente no seu sistema operacional.

    a. **Obtenha sua API Key do ScrapingBee:**
       * Acesse sua conta no [ScrapingBee](https://www.scrapingbee.com/).
       * Vá para o seu `Dashboard` ou `API Settings`. Sua chave de API estará visível lá. Copie-a.
    b. **Defina a variável de ambiente no seu sistema operacional:**

       **Para Unix/macOS (Terminal):**
       ```bash
       export SCRAPINGBEE_API_KEY="SUA_API_KEY_SCRAPINGBEE"
       # Para persistir entre sessões do terminal, adicione esta linha ao seu ~/.bashrc, ~/.zshrc ou ~/.profile
       ```

       **Para Windows (CMD):**
       ```cmd
       set SCRAPINGBEE_API_KEY="SUA_API_KEY_SCRAPINGBEE"
       # Para persistir entre sessões, você precisará configurá-la através das Propriedades do Sistema > Variáveis de Ambiente.
       ```
       (Substitua `SUA_API_KEY_SCRAPINGBEE` pela sua chave real).

4.  **Configurar ChromeDriver (para Web Scraping):**

    Esta API utiliza Selenium para web scraping local, que requer um navegador Chrome e seu respectivo ChromeDriver.

    a. **Verifique a versão do seu Google Chrome:**
       Abra o Google Chrome, vá em `Chrome` (no menu superior) > `Sobre o Google Chrome` e anote a versão exata (ex: `125.0.6422.141`).

    b. **Baixe o ChromeDriver compatível:**
       Acesse o site [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) e, na coluna `ChromeDriver`, baixe o `.zip` da versão que corresponde à do seu Chrome e à arquitetura do seu Mac (`mac-arm64` para Apple Silicon ou `mac-x64` para Intel).

    c. **Descompacte e coloque o ChromeDriver:**
       Após descompactar o arquivo `.zip` baixado, você encontrará o executável `chromedriver` dentro de uma pasta (ex: `chromedriver-mac-x64`). **Copie este executável `chromedriver`** para o local que você definiu na variável `CHROMEDRIVER_PATH_LOCAL` em `web_scrapers/vitibrasil_scraper.py`.

       **Com base no código atual, o caminho esperado é:** `/Users/mac/Downloads/chromedriver-mac-x64/`
       **Certifique-se de que o executável `chromedriver` esteja diretamente dentro dessa pasta.**

    d. **Conceda permissão de execução:**
       Abra o Terminal, navegue até a pasta onde você colocou o `chromedriver` e execute:

       ```bash
       chmod +x /Users/mac/Downloads/chromedriver-mac-x64/chromedriver
       ```
       (Ajuste o caminho se você decidir colocar o `chromedriver` em outro local no futuro).

    e. **Permissão de Segurança do macOS (se aplicável):**
       Na primeira vez que você tentar executar o scraper localmente, o macOS pode bloquear o `chromedriver`. Se isso acontecer, vá em `Ajustes do Sistema` (ou `Preferências do Sistema`) > `Privacidade e Segurança` e clique em `Abrir Mesmo Assim` ao lado da mensagem sobre o `chromedriver`.

5.  **Execute a API:**

    Com o ambiente virtual ativado, a chave do ScrapingBee e o ChromeDriver configurados, inicie a aplicação:

    ```bash
    python3 api.py
    ```

    A API estará disponível em `http://127.0.0.1:5000`. Você pode acessar a documentação Swagger em `http://127.0.0.1:5000/apidocs`.

---


## Como Usar a Coleção Postman

Para facilitar a interação com a API, fornecemos uma coleção do Postman que inclui todas as requisições e a configuração de autenticação.

1.  **Importe a Coleção Postman:**
    * Abra o Postman.
    * No canto superior esquerdo, clique em **"Import"** (Importar).
    * Selecione a opção **"Upload Files"** (Carregar Arquivos) e escolha o arquivo `Tech Challenge MLET API.postman_collection.json` que está na raiz do projeto.
    * Clique em **"Import"**. A coleção aparecerá na sua barra lateral esquerda em "Collections".

2.  **Configure a Variável de Ambiente `url_base`:**
    A coleção utiliza uma variável de ambiente chamada `url_base` para definir a URL base da API (seja local ou em produção).

    * No Postman, clique no ícone de **"olho"** (👁️) no canto superior direito, próximo ao dropdown de ambientes.
    * Clique em **"Add"** (Adicionar) para criar um novo ambiente, ou selecione um ambiente existente e clique no ícone de engrenagem para editá-lo.
    * Crie uma nova variável com o nome `url_base`.
    * No campo **`INITIAL VALUE`** e **`CURRENT VALUE`**, insira a URL base da sua API:
        * Para **Localhost**: `http://127.0.0.1:5000`
        * Para **Heroku**: `http://pos-tech-ml-tech-challenge-api-47e455659f67.herokuapp.com` (ou o nome do seu app Heroku)
    * Certifique-se de que este ambiente esteja **selecionado** no dropdown de ambientes do Postman.

3.  **Realize o Login para Obter o Bearer Token:**
    A requisição de login na coleção está configurada para automaticamente salvar o token JWT retornado em uma variável de ambiente chamada `bearer_token`.

    * Na coleção importada, expanda a pasta e selecione a requisição **"Login"**.
    * No corpo da requisição (`Body`), você verá um JSON com `username` e `password` (`admin` e `secret` por padrão).
    * Clique em **"Send"** (Enviar).
    * Após a resposta, o script na aba **"Post-response Script"** (Pós-resposta) será executado. Ele verificará se o login foi bem-sucedido e salvará o `token` retornado na variável de ambiente `bearer_token`. Você pode verificar isso clicando no ícone de "olho" (👁️) novamente e inspecionando o valor de `bearer_token`.

4.  **Execute as Requisições de Web Scraping:**
    Todas as outras requisições na coleção (Produção, Processamento, Importação, Exportação) estão configuradas para usar o `bearer_token` salvo.

    * Selecione qualquer uma das requisições de web scraping (ex: "Web Scraping: Produção").
    * Vá para a aba **"Authorization"** e você verá que o tipo **"Bearer Token"** está selecionado e o campo **"Token"** contém `{{bearer_token}}`.
    * Clique em **"Send"**. A requisição será enviada com o token de autenticação.

---

## Swagger

Documentação em Swagger:

```
# Localhost
http://127.0.0.1:5000/apidocs

# Exemplo de como ficaria no Heroku, precisa necessariamente ser http para que o web scraping funcione
http://pos-tech-ml-tech-challenge-api-47e455659f67.herokuapp.com/apidocs/
```
