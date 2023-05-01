# Importando as bibliotecas necessárias
import pandas as pd
from lxml import etree
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

dic_reviews = {
    "Limpeza:": [],
    "Exatidao do Anuncio" : [],
    "Comunicacao": [],
    "Localizacao": [],
    "Check-In": [],
    "Custo Beneficio" : []
}

# Loop pelos elementos da lista de hospedagem
for hospedagem in lista_hospedagem:
    try:
        # Obtém a URL da hospedagem
        hospedagem_url = hospedagem.find('meta', attrs={'itemprop': "url"})['content']
        
        # Navega para a página da hospedagem
        navegador.get(f"http://{hospedagem_url}")
    
        # Aguarda 10 segundos para a página ser carregada completamente
        sleep(15)

        # Obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
        conteudo_pagina = navegador.page_source
        site = BeautifulSoup(navegador.page_source, "html.parser")

        # Encontra as informações da hospedagem na página
        hospedagem_infor =  site.find_all('h1', attrs={"elementtiming":"LCP-target"})[0].text
        
        # Encontra a avaliação da hospedagem na página
        hospedagem_avaliacao = site.find_all('span', attrs={'aria-hidden':"true"})[0].text
        hospedagem_avaliacao = float(hospedagem_avaliacao.split(" ")[0].replace(',', "."))

        
        # Encontra a localização da hospedagem na página
        hospedagem_local = site.find_all('div', attrs={'data-plugin-in-point-id':"TITLE_DEFAULT"})[0].find_all('button')[1].text
        
        # Encontra o preço da hospedagem na página
        hospedagem_preco = site.find('div',attrs={'data-testid':"book-it-default"}).find_all("span")[2].text
        
        # Adiciona as informações ao dicionário de dados
        dic_dados["Url"].append(hospedagem_url)
        dic_dados["Informacao"].append(hospedagem_infor)
        dic_dados["Avaliacao"].append(hospedagem_avaliacao)
        dic_dados["Local"].append(hospedagem_local)
        dic_dados["Preco"].append(hospedagem_preco)

        #Entra os dados de reviews:
        dom = etree.HTML(str(site))

        review_limpeza = dom.xpath('//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[1]/div/div/div[2]/span')[0].text
        review_anuncio = dom.xpath('//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[2]/div/div/div[2]/span')[0].text
        review_comunicacao = dom.xpath('//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[3]/div/div/div[2]/span')[0].text
        review_localizacao = dom.xpath('//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[4]/div/div/div[2]/span')[0].text
        review_check_in = dom.xpath('//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[5]/div/div/div[2]/span')[0].text
        review_custo_beneficio = dom.xpath('//*[@id="site-content"]/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[6]/div/div/div[2]/span')[0].text

        # Adiciona as informações ao dicionário de reviews
        dic_reviews['Limpeza:'].append(review_limpeza)
        dic_reviews['Exatidao do Anuncio'].append(review_anuncio)
        dic_reviews["Comunicacao"].append(review_comunicacao)
        dic_reviews["Localizacao"].append(review_localizacao)
        dic_reviews["Check-In"].append(review_check_in)
        dic_reviews["Custo Beneficio"].append(review_custo_beneficio)

        if hospedagem_preco[0] == "R":
         hospedagem_preco = hospedagem_preco[2:]
        else:
            hospedagem_preco = site.find('div',attrs={'data-testid':"book-it-default"}).find_all("span")[1].text
            hospedagem_preco = hospedagem_preco[2:]
        

        hospedagem_avaliacao = site.find_all('span', attrs={'aria-hidden':"true"})[0].text
        hospedagem_avaliacao = float(hospedagem_avaliacao.split(" ")[0].replace(',', "."))
        
        print(f"A url: {hospedagem_url}")


    # Caso o quarto não possuir uma avaliação, vai dar um erro de valor e a hospedagem_avalição recebera nulo
    except ValueError:
     hospedagem_avaliacao = None 
     # Adiciona as informações ao dicionário de dados
     dic_dados["Url"].append(hospedagem_url)
     dic_dados["Informacao"].append(hospedagem_infor)
     dic_dados["Avaliacao"].append(hospedagem_avaliacao)
     dic_dados["Local"].append(hospedagem_local)
     dic_dados["Preco"].append(hospedagem_preco)
        
     # Adiciona as informações ao dicionário de reviews
     dic_reviews['Limpeza:'].append(review_limpeza)
     dic_reviews['Exatidao do Anuncio'].append(review_anuncio)
     dic_reviews["Comunicacao"].append(review_comunicacao)
     dic_reviews["Localizacao"].append(review_localizacao)
     dic_reviews["Check-In"].append(review_check_in)
     dic_reviews["Custo Beneficio"].append(review_custo_beneficio)

     continue


#Usa a blibioteca Pandas para salvar os dados com um dataframe        
df_listing = pd.DataFrame(dic_dados)
df_reviews = pd.DataFrame(dic_reviews)

#Salva o dataframe em um arquivo csv
df_listing.to_csv(f'{nome_cidade}_listing.csv', index=True)
df_reviews.to_csv(f"{nome_cidade}_reviews.csv", index=True)

print(df_listing, df_reviews)
input()