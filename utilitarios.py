# libs
import ctypes
from PIL import Image, ImageTk
from tkinter import Tk, Button, Label, Entry

# Pegando a resolução da tela
user32 = ctypes.windll.user32
resolucao = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def input_ok(path_imagem:str="captcha.png"):
    
    # Criando a janela principal do Tkinter
    root = Tk()
    # Configurando a largura e a altura da janela
    window_width = int(resolucao[0]/4)
    window_height = int(resolucao[1]/4)

    # Obtendo a largura e a altura da tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculando a posição x e y para centralizar a janela
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Definindo a geometria da janela
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Carregando a imagem do captcha
    img_captcha = Image.open(path_imagem)
    img_captcha = ImageTk.PhotoImage(img_captcha)

    # Criando um widget Label para exibir a imagem
    label = Label(root, image=img_captcha)
    label.pack()

    # Adicionando uma label para informar que quero que insira o captcha
    captcha_label = Label(root, text="Digite o captcha acima!")
    captcha_label.pack()
    
    
    # Criando um widget Entry para pegar o input do usuário
    entry = Entry(root)
    
    # Definindo o foco no widget Entry
    entry.focus_set()
    entry.pack()

    # Associando a função on_button_click ao evento <Return> do widget Entry
    entry.bind("<Return>", lambda event: on_button_click())

    # Função para continuar a execução do script quando o botão for clicado
    def on_button_click():
        global captcha_text
        # Obtendo o texto digitado pelo usuário
        captcha_text = entry.get()
        # Fechando a janela do Tkinter
        root.destroy()


    # Adicionando um botão para permitir que o usuário continue a execução do script
    button = Button(root, text="Continuar", command=on_button_click)
    button.configure(font={'size': 20})
    
    # Posicionando o botão abaixo do campo de entrada
    button.pack(side='bottom')

    # Exibindo a janela do Tkinter
    root.mainloop()
    
    return captcha_text