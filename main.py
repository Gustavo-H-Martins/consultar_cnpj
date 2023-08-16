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
output_xlsx = os.path.join(current_dir, "DADOS_CONSULTA_CNPJ.xlsx")
log_file = os.path.join(current_dir, "consulta_cnpj.log")

logging.basicConfig(level=logging.DEBUG, filename=log_file,encoding="utf-8", format="%(asctime)s - %(levelname)s - %(message)s")

with open(input_csv) as f:
    # Lendo todo o arquivo na variável cnpjs
    cnpjs = f.readlines()[1:]
    # Removendo caracteres não numéricos
    cnpjs = [''.join(filter(str.isdigit, cnpj)) for cnpj in cnpjs]
    # Removendo duplicados
    cnpjs = list(set(cnpjs))


# Criando o dicionário JSON
base = {}

async def main():
    # Instanciando e executando o processo de coleta
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # iterando sobre os cnpjs
        for cnpj in cnpjs:
            
            # Adicionando o CNPJ ao dicionário com as listas vazias
            base[cnpj] = {"CABECALHO": [], "VALOR": [], "INFORMAÇÕES": []}

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
            # print(captcha_text)

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
            if len(lista_dados) == 1:
                print(f"{lista_dados[0]}: Captcha inválido!")
            elif len(lista_dados) == 0:
                botoes = soup.find_all("div", {"class": "botoes"})
                print(f"{botoes.text}: Erro interno!")
            # Se tiver dados para retornar
            else:
                campos = soup.find_all("font")
                # Iterando sobre cada campo
                for posicao in range(len(campos)):
                    if campos[posicao].text.strip() == "NÚMERO DE INSCRIÇÃO":
                        cabecalho_inscricao = campos[posicao].text.strip()
                        valor_inscricao = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_inscricao)
                        base[cnpj]["VALOR"].append(valor_inscricao)
                    elif campos[posicao].text.strip() == "DATA DE ABERTURA":
                        cabecalho_data_abertura = campos[posicao].text.strip()
                        valor_data_abertura = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_data_abertura)
                        base[cnpj]["VALOR"].append(valor_data_abertura)
                    elif campos[posicao].text.strip() == "NOME EMPRESARIAL":
                        cabecalho_nome_empresarial = campos[posicao].text.strip()
                        valor_nome_empresarial = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_nome_empresarial)
                        base[cnpj]["VALOR"].append(valor_nome_empresarial)
                    elif campos[posicao].text.strip() == "TÍTULO DO ESTABELECIMENTO (NOME DE FANTASIA)":
                        cabecalho_nome_fantasia = campos[posicao].text.strip()
                        valor_nome_fantasia = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_nome_fantasia)
                        base[cnpj]["VALOR"].append(valor_nome_fantasia)
                    elif campos[posicao].text.strip() == "PORTE":
                        cabecalho_porte = campos[posicao].text.strip()
                        valor_porte = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_porte)
                        base[cnpj]["VALOR"].append(valor_porte)
                    elif campos[posicao].text.strip() == "CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA PRINCIPAL":
                        cabecalho_cnae_principal = campos[posicao].text.strip()
                        valor_cnae_principal = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_cnae_principal)
                        base[cnpj]["VALOR"].append(valor_cnae_principal)
                    elif campos[posicao].text.strip() == "CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS":
                        cabecalho_cnae_secundario = campos[posicao].text.strip()
                        valor_cnae_secundario = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_cnae_secundario)
                        base[cnpj]["VALOR"].append(valor_cnae_secundario)
                    elif campos[posicao].text.strip() == "CÓDIGO E DESCRIÇÃO DA NATUREZA JURÍDICA":
                        cabecalho_natureza = campos[posicao].text.strip()
                        valor_natureza = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_natureza)
                        base[cnpj]["VALOR"].append(valor_natureza)
                    elif campos[posicao].text.strip() == "LOGRADOURO":
                        cabecalho_logradouro = campos[posicao].text.strip()
                        valor_logradouro = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_logradouro)
                        base[cnpj]["VALOR"].append(valor_logradouro)
                    elif campos[posicao].text.strip() == "NÚMERO":
                        cabecalho_numero = campos[posicao].text.strip()
                        valor_numero = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_numero)
                        base[cnpj]["VALOR"].append(valor_numero)
                    elif campos[posicao].text.strip() == "COMPLEMENTO":
                        cabecalho_complemento = campos[posicao].text.strip()
                        valor_nome_complemento = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_complemento)
                        base[cnpj]["VALOR"].append(valor_nome_complemento)
                    elif campos[posicao].text.strip() == "CEP":
                        cabecalho_cep = campos[posicao].text.strip()
                        valor_cep = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_cep)
                        base[cnpj]["VALOR"].append(valor_cep)
                    elif campos[posicao].text.strip() == "BAIRRO/DISTRITO":
                        cabecalho_bairro = campos[posicao].text.strip()
                        valor_bairro = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_bairro)
                        base[cnpj]["VALOR"].append(valor_bairro)
                    elif campos[posicao].text.strip() == "MUNICÍPIO":
                        cabecalho_municipio = campos[posicao].text.strip()
                        valor_municipio = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_municipio)
                        base[cnpj]["VALOR"].append(valor_municipio)
                    elif campos[posicao].text.strip() == "UF":
                        cabecalho_uf = campos[posicao].text.strip()
                        valor_uf = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_uf)
                        base[cnpj]["VALOR"].append(valor_uf)
                    elif campos[posicao].text.strip() == "ENDEREÇO ELETRÔNICO":
                        cabecalho_email = campos[posicao].text.strip()
                        valor_email = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_email)
                        base[cnpj]["VALOR"].append(valor_email)
                    elif campos[posicao].text.strip() == "TELEFONE":
                        cabecalho_telefone = campos[posicao].text.strip()
                        valor_telefone = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_telefone)
                        base[cnpj]["VALOR"].append(valor_telefone)
                    elif campos[posicao].text.strip() == "ENTE FEDERATIVO RESPONSÁVEL (EFR)":
                        cabecalho_efr = campos[posicao].text.strip()
                        valor_efr = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_efr)
                        base[cnpj]["VALOR"].append(valor_efr)
                    elif campos[posicao].text.strip() == "SITUAÇÃO CADASTRAL":
                        cabecalho_situacao_cadastral = campos[posicao].text.strip()
                        valor_situacao_cadastral = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_situacao_cadastral)
                        base[cnpj]["VALOR"].append(valor_situacao_cadastral)
                    elif campos[posicao].text.strip() == "DATA DA SITUAÇÃO CADASTRAL":
                        cabecalho_data_situacao_cadastral = campos[posicao].text.strip()
                        valor_data_situacao_cadastral = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_data_situacao_cadastral)
                        base[cnpj]["VALOR"].append(valor_data_situacao_cadastral)
                    elif campos[posicao].text.strip() == "MOTIVO DE SITUAÇÃO CADASTRAL":
                        cabecalho_motivo_situacao_cadastral = campos[posicao].text.strip()
                        valor_motivo_situacao_cadastral = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_motivo_situacao_cadastral)
                        base[cnpj]["VALOR"].append(valor_motivo_situacao_cadastral)
                    elif campos[posicao].text.strip() == "SITUAÇÃO ESPECIAL":
                        cabecalho_situacao_especial = campos[posicao].text.strip()
                        valor_situacao_especial = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_situacao_especial)
                        base[cnpj]["VALOR"].append(valor_situacao_especial)
                    elif campos[posicao].text.strip() == "DATA DA SITUAÇÃO ESPECIAL":
                        cabecalho_data_situacao_especial = campos[posicao].text.strip()
                        valor_data_situacao_especial = campos[posicao+1].text.strip()
                        base[cnpj]["CABECALHO"].append(cabecalho_data_situacao_especial)
                        base[cnpj]["VALOR"].append(valor_data_situacao_especial)
                    elif "A dispensa de alvarás e licenças é direito do empreendedor" in campos[posicao].text.strip():
                        paragrafo = campos[posicao].text.strip()
                        licenca = campos[posicao+1].text.strip()
                        data_emissao = campos[posicao+2].text.strip()
                        base[cnpj]["INFORMAÇÕES"].append(paragrafo)
                        base[cnpj]["INFORMAÇÕES"].append(licenca)
                        base[cnpj]["INFORMAÇÕES"].append(data_emissao)
            print(base)
            sleep(5)
            break
        # Criando um DataFrame a partir do dicionário base
        dataframe = pd.DataFrame.from_dict(base, orient="index")
        dataframe.to_excel(output_xlsx, sheet_name="DETALHES CNPJ", index=False)
        await context.close()
        await browser.close()

# Executa o loop assíncrono
asyncio.get_event_loop().run_until_complete(main())