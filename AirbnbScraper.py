# Importando as bibliotecas necessárias
import pandas as pd
import re
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

# Aguarda 15 segundos para a página ser carregada completamente
sleep(20)  

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

# Coletando todas as urls de todas as 15 paginas
lista_hospedagem = []

for i in range(1,15):
    # Obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
    conteudo_pagina = navegador.page_source
    site = BeautifulSoup(conteudo_pagina, "html.parser")

    # Encontra todos os elementos div com o atributo itemprop="itemListElement"
    lista_hospedagem += site.find_all('div', attrs={'itemprop': "itemListElement"})

 
    navegador.execute_script("window.scrollBy(0, 4600);")
    sleep(1.5)
    #Clica no proximo
    Click_Pro = navegador.find_element(By.CSS_SELECTOR, 'a[aria-label="Próximo"]').click()
    sleep(5)
    print(len(lista_hospedagem))
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

dic_coment = {
    "Id_Quarto" : [],
    "Nome" : [],
    "Comentario" : [],
    "Data" : [],
    "Id_Usuario": []
}




# Loop pelos elementos da lista de hospedagem
for index,hospedagem in enumerate(lista_hospedagem):
    try:
        # Obtém a URL da hospedagem
        hospedagem_url = hospedagem.find('meta', attrs={'itemprop': "url"})['content']
        
        # Navega para a página da hospedagem
        navegador.get(f"http://{hospedagem_url}")
    
        # Aguarda 8 segundos para a página ser carregada completamente
        sleep(8)

        #Rolar a pagina para baixo para garatir que todas as informações sejam carregadas:
        navegador.execute_script("window.scrollBy(0, 3600);")

        sleep(3)

        # Obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
        conteudo_pagina = navegador.page_source
        site = BeautifulSoup(navegador.page_source, "html.parser")
        
        
        # Encontra as informações da hospedagem na página
        hospedagem_infor =  site.find_all('h1', attrs={"elementtiming":"LCP-target"})[0].text
            
        # Encontra a localização da hospedagem na página
        hospedagem_local = site.find_all('div', attrs={'data-plugin-in-point-id':"TITLE_DEFAULT"})[0].find_all('button')[1].text
        
        # Encontra o preço da hospedagem na página
        hospedagem_preco = site.find('div',attrs={'data-testid':"book-it-default"}).find_all("span")[2].text
        
        if hospedagem_preco[0] == "R":
         hospedagem_preco = hospedagem_preco[2:]
        else:
            hospedagem_preco = site.find('div',attrs={'data-testid':"book-it-default"}).find_all("span")[1].text
            hospedagem_preco = hospedagem_preco[2:]
        
        
        # Encontra a avaliação da hospedagem na página
        hospedagem_avaliacao = site.find_all('span', attrs={'aria-hidden':"true"})[0].text
        hospedagem_avaliacao = float(hospedagem_avaliacao.split(" ")[0].replace(',', "."))


        #Comentarios
        lista_comentarios = site.find_all("div", attrs={'role':'listitem'})
        data_coment = site.find_all("li", attrs={"theme":"[object Object]"})
        nomes_comentarios = []
        comentarios = []

        for comentario in lista_comentarios:
            nomes_comentarios += [comentario.find("h3").text]
            comentarios += [comentario.find_all('span')[-1].text]

        # Encontrar todas as tags 'a' que contêm '/users/show/' no atributo 'href'
        id_user = site.find_all('a', href=lambda href: href and '/users/show/' in href)[-6:]


        # Iterar sobre as tags 'a' encontradas e imprimir o texto e o valor do atributo 'href'
        list_urlUser = []
        id_usuarios = []
        for id in id_user:
            list_urlUser.append(id['href'])
        for string in list_urlUser:
            numeros_string = re.findall(r'\d+', string)
            id_usuarios.extend(numeros_string)
        
            
        #Entra os dados de reviews:
        dom = etree.HTML(str(site))

        sleep(1.5)
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

        # Adiciona as informações ao dicionário de dados
        dic_dados["Url"].append(hospedagem_url)
        dic_dados["Informacao"].append(hospedagem_infor)
        dic_dados["Avaliacao"].append(hospedagem_avaliacao)
        dic_dados["Local"].append(hospedagem_local)
        dic_dados["Preco"].append(hospedagem_preco)

        for i in range(len(nomes_comentarios)):
            dic_coment["Id_Quarto"].append(index)
            dic_coment["Nome"].append(nomes_comentarios[i])
            dic_coment["Comentario"].append(comentarios[i])
            dic_coment["Data"].append(data_coment[i].text)
            dic_coment["Id_Usuario"].append(id_usuarios[i])

        print(f"Falta cerca de {len(lista_hospedagem) - index}")       

    
    except:
       print("Erro")
       sleep(1.5)
       continue

#Usa a blibioteca Pandas para salvar os dados com um dataframe        
df_listing = pd.DataFrame(dic_dados)
df_reviews = pd.DataFrame(dic_reviews)
df_coment = pd.DataFrame(dic_coment)

#Salva o dataframe em um arquivo csv
df_listing.to_csv(f'{nome_cidade}_listing.csv', index=True)
df_reviews.to_csv(f"{nome_cidade}_reviews.csv", index=True)
df_coment.to_csv(f"{nome_cidade}_comentarios.csv", index=True)


input()