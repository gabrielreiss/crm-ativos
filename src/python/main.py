# Função para extrair dados de uma página
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd

def extract_data(pagina, driver):
    # Espera a página carregar os resultados
    time.sleep(5)  # Aguarde alguns segundos para garantir que a página tenha carregado

    # Extrai os dados dos médicos
    #doctors = driver.find_elements(By.XPATH, '//div[@class="busca-resultado"]')

    doctors = driver.find_elements(By.XPATH, './/div[contains(@class, "resultado-item")]')
    print(len(doctors))
    print(doctors)

    for doctor in doctors:
        try:            
            #temp = doctor.find_element(By.XPATH, '//div[@class="col-md-4"]')
            #crm = temp.find_element(By.XPATH,"//div[.//b[contains(text(), 'CRM:')]]").text
            crm = doctor.find_element(By.XPATH,".//div[@class='col-md-4']").text
            print(crm)
        except:
            crm = ''

        try:
            situacao = doctor.find_element(By.XPATH,".//div[@class='col-md']").text
            #situacao = doctor.find_elements(By.CLASS_NAME, "col-md").text
            #situacao = situacao.find_element(By.TAG_NAME, "b").text
            print(situacao)
        except:
            situacao = ''

        try:
            inscricao = doctor.find_element(By.XPATH,".//div[@class='col-md-6']").text
            #inscricao = doctor.find_elements(By.CLASS_NAME, "col-md-6").text
            #inscricao = inscricao.find_element(By.TAG_NAME, "b").text
            print(inscricao)
        except:
            inscricao = ''

        try:
            temp = doctor.find_element(By.XPATH,".//div[@class='col-md-12']")
            especialidade = temp.find_element(By.XPATH, ".//span").text
            #especialidade = doctor.find_elements(By.CLASS_NAME, "col-md-12").text
            #especialidade = especialidade.find_element(By.TAG_NAME, "b").text
            print(especialidade)
        except:
            especialidade = ''
        
        print(f"{crm} {situacao} {inscricao} {especialidade}")

        #try:
        #    temp = doctor.find_elements(".//*")
        #    tudo = ''
        #    for i in range(0,len(temp)):
        #        tudo = tudo + '|' + str(temp[i].text)
        #except:
        #    tudo = ''

        # Adiciona os dados à lista
        data = []
        data.append({'CRM': crm, 
                    'Situação': situacao, 
                    'Inscricao': inscricao, 
                    'Especialidade': especialidade,
                    'Pagina': pagina})
    return data

def rouba_dados_CFM():
    # Caminho para o ChromeDriver
    chrome_driver_path = 'C:\\Users\\gabriel.castro\\Desktop\\2024\\chromedriver.exe'  # Altere para o caminho do seu ChromeDriver

    #%%
    # Configuração do navegador
    #service =Service(ChromeDriverManager(driver_version="114.0.5735.90").install())
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executa o navegador em modo headless (sem interface gráfica)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Inicia o navegador
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Acessa o site do CFM
        driver.get('https://portal.cfm.org.br/busca-medicos')

        # Seleciona a UF "RS" no dropdown
        time.sleep(2)
        uf_dropdown = driver.find_element(By.ID, 'uf')
        uf_dropdown.send_keys('RS')

        time.sleep(2)
        situacao_dropdown = driver.find_element(By.ID, 'tipoSituacao')
        situacao_dropdown.send_keys('A')

        # Clica no botão de busca
        #search_button = driver.find_element(By.XPATH, '//button[contains(text(), "Buscar")]')
        #search_button = driver.find_element(by=By.css("[type='submit']"))
        #search_button = driver.find_element(by=By.CLASS_NAME("w-100 btn-buscar btnPesquisar "))
        search_button = driver.find_element(By.XPATH, '//button[@class="w-100 btn-buscar btnPesquisar "]')
        #find_element_by_css_selector('button[alt="Buscar"]').click()

    # Tenta clicar no botão de busca usando JavaScript se o click normal falhar
        try:
            search_button.click()
        except Exception as e:
            print(f"Erro ao clicar no botão: {e}. Tentando com JavaScript...")
            driver.execute_script("arguments[0].click();", search_button)

        # Navega pelas páginas seguintes
        while True:
            # Encontra o botão de próxima página e clica nele
            #precisa fazer algo que pule as paginas
            pagina = 1
            
            try:
                df = pd.read_csv('dados_medicos_rs.csv')
                if 'Pagina' not in df.columns:
                    data = extract_data(1, driver)
                    df = pd.DataFrame(data)
                    df.to_csv('dados_medicos_rs.csv', index=False, mode = 'a')
                    print(f"Dados da pagina {pagina} exportados para 'dados_medicos_rs.csv'")
                else:
                    if pagina not in df["Pagina"]:
                        # Extrai dados da nova página
                        data = extract_data(pagina, driver)
                        df = pd.DataFrame(data)
                        df.to_csv('dados_medicos_rs.csv', index=False, mode = 'a')
                        print(f"Dados da pagina {pagina} exportados para 'dados_medicos_rs.csv'")
                    else:
                        print(f"Página {pagina} já lida...")
                pagina += 1
                next_button = driver.find_element(By.XPATH, f"//a[contains(@href, {pagina})]")
                # Tenta clicar no botão de busca usando JavaScript se o click normal falhar
                try:
                    next_button.click()
                except Exception as e:
                    print(f"Erro ao clicar no botão: {e}. Tentando com JavaScript...")
                    driver.execute_script("arguments[0].click();", next_button)

            except NoSuchElementException:
                # Se não houver mais o botão de próxima página, encerra o loop
                print("Todas as páginas foram processadas.")
                break

    finally:
        # Fecha o navegador
        driver.quit()

#%%
#40220 médicos no RS

while True:
    try:
        df = pd.read_csv('dados_medicos_rs.csv')
        paginas = df["Pagina"].unique()
        if not list(range(1,4023)) in paginas:
            rouba_dados_CFM()
    except Exception as e:
        print(e)
    