
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep


nome_cidade = input("Cidade: ")  # solicita ao usuário que informe o nome da cidade
#data_ida = input("Digite a data de ida (ano-mês-dia):")
#data_volta = input("Digite a data de volta (ano-mês-dia):")
data_ida = "2023-06-05"
data_volta= "2023-06-10"
options= Options()  # instancia um objeto da classe Options
options.add_argument("window-size=950,800")  # define o tamanho da janela do navegador
#options.add_argument("--headless")  # opção para executar o navegador em modo headless

#Tive que colocar o caminho especifico do meu chrome web driver pois estava dando erro, (não é obrigatorio)
pat = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Python 3.11\chromedriver"  # define o caminho do webdriver do Chrome
navegador = webdriver.Chrome(executable_path=pat, options=options)  # instancia um objeto da classe webdriver.Chrome passando o caminho do webdriver e as opções definidas anteriormente

navegador.get("http://airbnb.com")  # navega para o site do Airbnb
sleep(5)  # espera por 2 segundos


Click = navegador.find_element(By.XPATH, '//*[@id="site-content"]/div/div/div/header/div/div[2]/div[1]/div/button[3]/div[2]').click()

sleep(1.5)  # espera por 3 segundos

pesquisar = navegador.find_element(By.XPATH, '//*[@id="bigsearch-query-location-input"]').click()  # encontra o campo de pesquisa e clica nele
procurar_cidade = navegador.find_element(By.NAME, "query")  # encontra o campo de pesquisa por nome
procurar_cidade.send_keys(nome_cidade)  # insere o nome da cidade no campo de pesquisa
procurar_cidade.submit()  # envia a pesquisa


sleep(4)
url_atual = navegador.current_url
nova_url = f"{url_atual}&date_picker_type=calendar&checkin={data_ida}&checkout={data_volta}"

navegador.get(nova_url)
sleep(10)

# obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
conteudo_pagina = navegador.page_source
site = BeautifulSoup(conteudo_pagina, "html.parser")

# encontra todos os elementos div com o atributo itemprop="itemListElement"
lista_hospedagem = site.find_all('div', attrs={'itemprop': "itemListElement"})
# obtém o primeiro elemento div da lista de hospedagem


#Criar meu dicionario para colocar as informações:
hospedagem = lista_hospedagem[0]

try:
    # obtém a URL da hospedagem
    hospedagem_url = hospedagem.find('meta', attrs={'itemprop': "url"})['content']
    # navega para a página da hospedagem
    navegador.get(f"http://{hospedagem_url}")

    # espera por 10 segundos
    sleep(10)

    # obtém o conteúdo da página atual do navegador e converte para um objeto BeautifulSoup
    conteudo_pagina = navegador.page_source
    site = BeautifulSoup(navegador.page_source, "html.parser")


    # encontra os dados
    hospedagem_infor =  site.find_all('h1', attrs={"elementtiming":"LCP-target"})[0].text
    
    hospedagem_local = site.find_all('div', attrs={'data-plugin-in-point-id':"TITLE_DEFAULT"})[0].find_all('button')[1].text
    #.find('section').find_all('div')[-1]
    #.find('div')
    #.find_all('span')[-1].text
   

    hospedagem_preco = site.find('div',attrs={'data-testid':"book-it-default"}).find_all("span")[2].text
    
    if hospedagem_preco[0] == "R":
        hospedagem_preco = hospedagem_preco[2:]
    else:
        hospedagem_preco = site.find('div',attrs={'data-testid':"book-it-default"}).find_all("span")[1].text
        hospedagem_preco = hospedagem_preco[2:]
        

    hospedagem_avaliacao = site.find_all('span', attrs={'aria-hidden':"true"})[0].text
    hospedagem_avaliacao = float(hospedagem_avaliacao.split(" ")[0].replace(',', "."))

    
    print(f"A url: {hospedagem_url}")
    print(f"A avaliação: {hospedagem_avaliacao}")
    print(f"A informação: {hospedagem_infor}")
    print(f"O local é {hospedagem_local}")
    print(f"O preço: {hospedagem_preco}")
    print('\n')
    input()


except ValueError:
    hospedagem_avaliacao = None
    print(f"A url: {hospedagem_url}")
    print(f"A avaliação: {hospedagem_avaliacao}")
    print(f"A informação: {hospedagem_infor}")
    print(f"O local é {hospedagem_local}")
    print(f"O preço: {hospedagem_preco}")
    print('\n')
    
except Exception as e:
    input(f"Algo deu errado, {e} //| {type(e).__name__}")
    
    


