# Importando as bibliotecas necessárias
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

# Recebe como entrada do usuário o nome da cidade, a data de ida e a data de volta
nome_cidade = input("Cidade: ")
data_ida = input("Digite a data de ida (ano-mês-dia):")
data_volta = input("Digite a data de volta (ano-mês-dia):")

# Define as opções do navegador
options= Options()  
options.add_argument("window-size=950,800") 
#options.add_argument("--headless")  # opção para executar o navegador em modo headless

# Define o caminho do webdriver do Chrome (não é obrigatório)
pat = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Python 3.11\chromedriver"  # define o caminho do webdriver do Chrome
navegador = webdriver.Chrome(executable_path=pat, options=options) 

# Navega para o site do Airbnb
navegador.get("http://airbnb.com")  

# Aguarda 2 segundos para a página ser carregada completamente
sleep(2)  

# Clica no botão "Datas" para abrir a caixa de seleção de datas
Click = navegador.find_element(By.XPATH, '//*[@id="site-content"]/div/div/div/header/div/div[2]/div[1]/div/button[3]/div[2]').click()

# Aguarda 1,5 segundos para a página ser carregada completamente
sleep(1.5) 

# Insere o nome da cidade na barra de pesquisa e clica no botão de pesquisa
pesquisar = navegador.find_element(By.XPATH, '//*[@id="bigsearch-query-location-input"]').click()
procurar_cidade = navegador.find_element(By.NAME, "query") 
procurar_cidade.send_keys(nome_cidade)  
procurar_cidade.submit() 

# Aguarda 4 segundos para a página ser carregada completamente
sleep(4)

# Obtém a URL atual
url_atual = navegador.current_url

# Define uma nova URL incluindo as datas de ida e volta
nova_url = f"{url_atual}&date_picker_type=calendar&checkin={data_ida}&checkout={data_volta}"

# Navega para a nova URL
navegador.get(nova_url)

# Aguarda 10 segundos para a página ser carregada completamente
sleep(10)

# Obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
conteudo_pagina = navegador.page_source
site = BeautifulSoup(conteudo_pagina, "html.parser")

# Encontra todos os elementos div com o atributo itemprop="itemListElement"
lista_hospedagem = site.find_all('div', attrs={'itemprop': "itemListElement"})

# Cria um dicionário para armazenar as informações coletadas
dic_dados = {
    "Url": [],
    "Informacao": [],
    "Avaliacao" : [],
    "Local": [],
    "Preco" : []
}

# Loop pelos elementos da lista de hospedagem
for hospedagem in lista_hospedagem:
    try:
        # Obtém a URL da hospedagem
        hospedagem_url = hospedagem.find('meta', attrs={'itemprop': "url"})['content']
        
        # Navega para a página da hospedagem
        navegador.get(f"http://{hospedagem_url}")
    
        # Aguarda 10 segundos para a página ser carregada completamente
        sleep(10)

        # Obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
        conteudo_pagina = navegador.page_source
        site = BeautifulSoup(navegador.page_source, "html.parser")

        # Encontra as informações da hospedagem na página
        hospedagem_infor =  site.find_all('h1', attrs={"elementtiming":"LCP"} )
        
        # Encontra a avaliação da hospedagem na página
        hospedagem_avaliacao = site.find_all('span', attrs={"class":"_1ne5r4rt"})[0].text
        
        # Encontra a localização da hospedagem na página
        hospedagem_local = site.find_all('span', attrs={"class":"_16shi2n"})[0].text
        
        # Encontra o preço da hospedagem na página
        hospedagem_preco = site.find_all('span', attrs={'class': '_olc9rf0'})[0].text
        
        # Adiciona as informações ao dicionário de dados
        dic_dados["Url"].append(hospedagem_url)
        dic_dados["Informacao"].append(hospedagem_infor)
        dic_dados["Avaliacao"].append(hospedagem_avaliacao)
        dic_dados["Local"].append(hospedagem_local)
        dic_dados["Preco"].append(hospedagem_preco)
        
    except:
        continue

#Usa a blibioteca Pandas para salvar os dados com um dataframe        
df = pd.DataFrame(dic_dados)

#Salva o dataframe em um arquivo csv
df.to_csv('dados.csv', index=False)

