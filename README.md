
# Consultar CNPJ - Automação de Consulta na Receita Federal

Este é um projeto de automação de consulta de informações de CNPJ na Receita Federal utilizando a biblioteca Playwright em Python. O projeto realiza consultas em lote, coletando informações relevantes de empresas a partir de uma lista de CNPJs fornecida em um arquivo CSV.

## Pré-requisitos

Certifique-se de que você tenha os seguintes requisitos instalados em sua máquina:

- Python (versão 3.9 ou superior)
- Bibliotecas Python listadas em `requirements.txt`
- Google Chrome ou Chromium instalado (necessário para a execução do Playwright)

## Como Baixar e Rodar

1. Clone este repositório em sua máquina:

```bash
git clone https://github.com/Gustavo-H-Martins/consultar_cnpj
```

2. Instale as bibliotecas Python necessárias usando o seguinte comando:

```bash
pip install -r requirements.txt
```

3. Edite o arquivo `.env` para definir as variáveis de ambiente necessárias, como `log_file`, `input_csv` e `output_csv` caso queira.

4. Execute o script principal para iniciar o processo de consulta:

```bash
python main.py
```

## Funcionalidades

- O programa lê uma lista de CNPJs a partir de um arquivo CSV.
- Para cada CNPJ, o programa realiza os seguintes passos:
  1. Acessa a página da Receita Federal para consulta.
  2. Resolve o captcha manualmente (é exibida uma imagem do captcha para o usuário).
  3. Preenche o captcha e envia o formulário de consulta.
  4. Coleta informações relevantes da página de resultado da Receita Federal.
- Os resultados são armazenados em um CSV contendo informações detalhadas de cada CNPJ consultado.

## Observações

- Certifique-se de ter o Google Chrome ou Chromium instalado em sua máquina.
- A resolução manual do captcha é necessária para a conclusão da consulta.
- Os resultados da consulta são armazenados em um dicionário JSON.
- O projeto pode ser facilmente personalizado para atender às suas necessidades específicas.