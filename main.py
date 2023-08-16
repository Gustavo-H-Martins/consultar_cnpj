# libs
import asyncio
from playwright.async_api import async_playwright
from PIL import Image
from io import BytesIO
import logging
import os
from time import sleep
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd
from utilitarios import input_ok
load_dotenv(".env")


# Define o diretório e nomeia os arquivos
current_dir = os.path.dirname(os.path.abspath(__file__))
input_csv = os.path.join(current_dir,"input.csv")
output_csv = os.path.join(current_dir, "output.csv")
log_file = os.path.join(current_dir, "consulta_cnpj.log")

logging.basicConfig(level=logging.DEBUG, filename=log_file,encoding="utf-8", format="%(asctime)s - %(levelname)s - %(message)s")

with open(input_csv) as f:
    # Lendo todo o arquivo na variável cnpjs
    cnpjs = f.readlines()[1:]
    # Removendo caracteres não numéricos
    cnpjs = [''.join(filter(str.isdigit, cnpj)) for cnpj in cnpjs]
    # Removendo duplicados
    cnpjs = list(set(cnpjs))

async def main():
    # Instanciando e executando o processo de coleta
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # iterando sobre os cnpjs
        for cnpj in cnpjs:
            # Criando o dicionário JSON
            base = {
                "INDICE_CNPJ": [],
                "NÚMERO DE INSCRIÇÃO": [], 
                "DATA DE ABERTURA": [], 
                "NOME EMPRESARIAL": [],
                "TÍTULO DO ESTABELECIMENTO (NOME DE FANTASIA)" : [],
                "PORTE": [],
                "CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA PRINCIPAL": [],
                "CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS": [],
                "CÓDIGO E DESCRIÇÃO DA NATUREZA JURÍDICA": [],
                "LOGRADOURO": [],
                "NÚMERO": [],
                "COMPLEMENTO":[],
                "CEP":[],
                "BAIRRO/DISTRITO":[],
                "MUNICÍPIO":[],
                "UF":[],
                "ENDEREÇO ELETRÔNICO":[],
                "TELEFONE":[],
                "ENTE FEDERATIVO RESPONSÁVEL (EFR)":[],
                "SITUAÇÃO CADASTRAL":[],
                "DATA DA SITUAÇÃO CADASTRAL":[],
                "MOTIVO DE SITUAÇÃO CADASTRAL":[],
                "SITUAÇÃO ESPECIAL":[],
                "DATA DA SITUAÇÃO ESPECIAL":[]
            }
            # Verifica se a imagem do captcha existe, se sim deleta.
            if os.path.exists('./captcha.png'):
                os.system("del captcha.png")
            # Rodando a automação no browser
            await page.goto("https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao_CS.asp")
            await page.wait_for_selector('input[name="cnpj"]')
            await page.fill('input[name="cnpj"]', cnpj)

            # Tenta resolver o captcha
            
            await page.wait_for_selector('//*[@id="imgCaptcha"]')

            # Captura a imagem do captcha
            captcha = await page.query_selector('//*[@id="imgCaptcha"]')
            captcha_screenshot = await captcha.screenshot()

            # Converte os bytes em uma imagem Pillow
            captcha_image = Image.open(BytesIO(captcha_screenshot))

            # Salva a imagem capturada
            captcha_image.save("captcha.png")
            
            # Exibindo o captcha automaticamente
            captcha_text = input_ok("captcha.png")
            logging.info(f"Captcha para o cnpj:{cnpj} : {captcha_text}")

            # Preencha o campo de texto com a resposta do captcha
            await page.fill('input[name="txtTexto_captcha_serpro_gov_br"]', captcha_text)

            # Clicando no botão "Consultar" usando um seletor CSS
            await page.click('.btn.btn-primary[type="submit"]')

            # Retirando os dados da consulta
            # Aguardando a página atualizar
            await page.wait_for_load_state()

            # Obtendo o HTML da página atualizada
            html = await page.content()

            # Fazendo o parse do html
            soup = BeautifulSoup(html, "html.parser")
            
            # Localizando todos os elementos com a tag td
            dados = soup.find_all("b")
            
            # Verificando se esses elementros refletem o erro de coleta.
            lista_dados = []
            for dado in dados:
                lista_dados.append(dado.text)
            if len(lista_dados) == 0:
                logging.info(f"Erro ao consultar o cnpj: {cnpj}")
            elif len(lista_dados) == 0:
                logging.info(f"{lista_dados[0]}: Captcha inválido!")
            # Se tiver dados para retornar
            else:
                # Adicionando o CNPJ ao dicionário
                base["INDICE_CNPJ"].append(cnpj)
                campos = soup.find_all("font")
                # Iterando sobre cada campo
                for posicao in range(len(campos)):
                    if campos[posicao].text.strip() == "NÚMERO DE INSCRIÇÃO":
                        valor_inscricao = campos[posicao+1].text.strip()
                        valor_inscricao = valor_inscricao.replace("\n", " ")
                        base["NÚMERO DE INSCRIÇÃO"].append(valor_inscricao)
                    elif campos[posicao].text.strip() == "DATA DE ABERTURA":
                        valor_data_abertura = campos[posicao+1].text.strip()
                        base["DATA DE ABERTURA"].append(valor_data_abertura)
                    elif campos[posicao].text.strip() == "NOME EMPRESARIAL":
                        valor_nome_empresarial = campos[posicao+1].text.strip()
                        base["NOME EMPRESARIAL"].append(valor_nome_empresarial)
                    elif campos[posicao].text.strip() == "TÍTULO DO ESTABELECIMENTO (NOME DE FANTASIA)":
                        valor_nome_fantasia = campos[posicao+1].text.strip()
                        base["TÍTULO DO ESTABELECIMENTO (NOME DE FANTASIA)"].append(valor_nome_fantasia)
                    elif campos[posicao].text.strip() == "PORTE":
                        valor_porte = campos[posicao+1].text.strip()
                        base["PORTE"].append(valor_porte)
                    elif campos[posicao].text.strip() == "CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA PRINCIPAL":
                        valor_cnae_principal = campos[posicao+1].text.strip()
                        base["CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA PRINCIPAL"].append(valor_cnae_principal)
                    elif campos[posicao].text.strip() == "CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS":
                        valor_cnae_secundario = campos[posicao+1].text.strip()
                        base["CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS"].append(valor_cnae_secundario)
                    elif campos[posicao].text.strip() == "CÓDIGO E DESCRIÇÃO DA NATUREZA JURÍDICA":
                        valor_natureza = campos[posicao+1].text.strip()
                        base["CÓDIGO E DESCRIÇÃO DA NATUREZA JURÍDICA"].append(valor_natureza)
                    elif campos[posicao].text.strip() == "LOGRADOURO":
                        valor_logradouro = campos[posicao+1].text.strip()
                        base["LOGRADOURO"].append(valor_logradouro)
                    elif campos[posicao].text.strip() == "NÚMERO":
                        valor_numero = campos[posicao+1].text.strip()
                        base["NÚMERO"].append(valor_numero)
                    elif campos[posicao].text.strip() == "COMPLEMENTO":
                        valor_nome_complemento = campos[posicao+1].text.strip()
                        base["COMPLEMENTO"].append(valor_nome_complemento)
                    elif campos[posicao].text.strip() == "CEP":
                        valor_cep = campos[posicao+1].text.strip()
                        base["CEP"].append(valor_cep)
                    elif campos[posicao].text.strip() == "BAIRRO/DISTRITO":
                        valor_bairro = campos[posicao+1].text.strip()
                        base["BAIRRO/DISTRITO"].append(valor_bairro)
                    elif campos[posicao].text.strip() == "MUNICÍPIO":
                        valor_municipio = campos[posicao+1].text.strip()
                        base["MUNICÍPIO"].append(valor_municipio)
                    elif campos[posicao].text.strip() == "UF":
                        valor_uf = campos[posicao+1].text.strip()
                        base["UF"].append(valor_uf)
                    elif campos[posicao].text.strip() == "ENDEREÇO ELETRÔNICO":
                        valor_email = campos[posicao+1].text.strip()
                        base["ENDEREÇO ELETRÔNICO"].append(valor_email)
                    elif campos[posicao].text.strip() == "TELEFONE":
                        valor_telefone = campos[posicao+1].text.strip()
                        base["TELEFONE"].append(valor_telefone)
                    elif campos[posicao].text.strip() == "ENTE FEDERATIVO RESPONSÁVEL (EFR)":
                        valor_efr = campos[posicao+1].text.strip()
                        base["ENTE FEDERATIVO RESPONSÁVEL (EFR)"].append(valor_efr)
                    elif campos[posicao].text.strip() == "SITUAÇÃO CADASTRAL":
                        valor_situacao_cadastral = campos[posicao+1].text.strip()
                        base["SITUAÇÃO CADASTRAL"].append(valor_situacao_cadastral)
                    elif campos[posicao].text.strip() == "DATA DA SITUAÇÃO CADASTRAL":
                        valor_data_situacao_cadastral = campos[posicao+1].text.strip()
                        base["DATA DA SITUAÇÃO CADASTRAL"].append(valor_data_situacao_cadastral)
                    elif campos[posicao].text.strip() == "MOTIVO DE SITUAÇÃO CADASTRAL":
                        valor_motivo_situacao_cadastral = campos[posicao+1].text.strip()
                        base["MOTIVO DE SITUAÇÃO CADASTRAL"].append(valor_motivo_situacao_cadastral)
                    elif campos[posicao].text.strip() == "SITUAÇÃO ESPECIAL":
                        valor_situacao_especial = campos[posicao+1].text.strip()
                        base["SITUAÇÃO ESPECIAL"].append(valor_situacao_especial)
                    elif campos[posicao].text.strip() == "DATA DA SITUAÇÃO ESPECIAL":
                        valor_data_situacao_especial = campos[posicao+1].text.strip()
                        base["DATA DA SITUAÇÃO ESPECIAL"].append(valor_data_situacao_especial)
                
                # Criando um DataFrame a partir do dicionário base
                dataframe = pd.DataFrame.from_dict(base, orient='columns')
                dataframe.to_csv(output_csv,sep=";", encoding='utf-8', index=False, mode='a', header=False)

        await context.close()
        await browser.close()

# Executa o loop assíncrono
asyncio.get_event_loop().run_until_complete(main())