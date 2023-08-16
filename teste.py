# libs
import ctypes

import logging
import os
from time import sleep
from tkinter import Tk, Button
from dotenv import load_dotenv

load_dotenv(".env")

# Pegando a resolução da tela
user32 = ctypes.windll.user32
resolucao = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

current_dir = os.path.dirname(os.path.abspath(__file__))
caminho_tesseract = os.path.join(os.environ.get("caminho_tesseract"), "tesseract.exe")
input_csv = os.path.join(current_dir,"input.csv")
log_file = os.path.join(current_dir, "consulta_cnpj.log")
with open(input_csv) as f:
    # Lendo todo o arquivo na variável cnpjs
    cnpjs = f.readlines()[1:]
    # Removendo caracteres não numéricos
    cnpjs = [''.join(filter(str.isdigit, cnpj)) for cnpj in cnpjs]
    # Removendo duplicados
    cnpjs = list(set(cnpjs))

def input_ok ():
    # Criando a janela principal do Tkinter
    root = Tk()
    # Configurando a largura e a altura da janela
    window_width = resolucao[0]
    window_height = resolucao[1]

    # Obtendo a largura e a altura da tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculando a posição x e y para centralizar a janela
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Definindo a geometria da janela
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    # Função para continuar a execução do script quando o botão for clicado
    def on_button_click():
        # Fechando a janela do Tkinter
        root.destroy()

    # Adicionando um botão para permitir que o usuário continue a execução do script
    button = Button(root, text="Continuar", command=on_button_click)
    button.configure(font={'size': 20})
    button.pack(padx=100, pady=200)

    # Exibindo a janela do Tkinter
    root.mainloop()

import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import pytesseract
from io import BytesIO

# instanciando o pytesseract
pytesseract.pytesseract.tesseract_cmd = caminho_tesseract
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        page = await context.new_page()

        for cnpj in cnpjs:
            if os.path.exists('./captcha.png'):
                os.system("del captcha.png")
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
            
            # Use o pytesseract para reconhecer o texto na imagem do captcha
            captcha_text = pytesseract.image_to_string('captcha.png')
            print(captcha_text)
            # Preencha o campo de texto com a resposta do captcha
            await page.fill('input[name="txtTexto_captcha_serpro_gov_br"]', captcha_text)

            # Clique no botão consultar
            await page.click('button:has-text("Consultar")')
            
            sleep(30)
            break

        await context.close()
        await browser.close()

# Executa o loop assíncrono
asyncio.get_event_loop().run_until_complete(main())