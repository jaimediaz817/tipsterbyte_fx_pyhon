import os
from fastapi import FastAPI, Request
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import numbers
import requests
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# miembros propios


# >>>
# trabajo con fechas
from datetime import date, datetime, timedelta
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
# <<<

# importing module
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import platform

import sys
# import requests
# import aiohttp
# import asyncio
# from fastapi.responses import StreamingResponse

# IMPORTS SIN USO: (testear para eliminar)
# from datetime import timedelta
# import requests
# from array import array
# from database import database as connection
# from fastapi.responses import  RedirectResponse
# import pandas as pd



class TablaPosiciones():

    def transcribir_partidos_jugados(self, resultado):
        retorno_numerico = None
        
        if resultado == 'G' or resultado == 'W' or resultado == 'w':
            retorno_numerico = 1
        elif resultado == 'E' or resultado == 'D' or resultado == 'd':
            retorno_numerico = 0
        elif resultado == 'P' or resultado == 'L' or resultado == 'l':
            retorno_numerico = -1

        return retorno_numerico
    
    
class UtilitiesMontecarlo():
    
    acents: str
    witout_acents: str
    transform: str
    
    def __init__(self):
        self.acents, self.witout_acents = 'áéíóúüÁÉÍÓÚÜ', 'aeiouuAEIOUU'
        self.transform = str.maketrans(self.acents, self.witout_acents)
        
    def retornar_cadena_sin_acento(self, cadena_in: str):
        return cadena_in.translate(self.transform)    



# TODO: ejemplos para experimentar con variables globales
app = FastAPI(
    title='Web Scraping - TipsterByte',
    description='TipsterByte Scraping by league',
    version='1.0.1'
)

platforms = {
    "spotify": {
        "base_url":"https://spotifycharts.com/regional/"
    },
    "youtube": {
        "base_url":"https://charts.youtube.com/charts/TopSongs/"
    },
    "resultados-futbol": [
        {
            "url_liga_colombia": "https://www.resultados-futbol.com/apertura_colombia2023/grupo1/calendario",
            "bloque_jornada": ".boxhome.boxhome-2col",
            "bloque_tabla_matches_resultados": "table"
        }
    ]
}

# eventos
# @app.on_event('startup')
# def startup():
    # CONEXIÓN COMENTADA DE MOMENTO
    # if connection.is_closed():
    #     connection.connect()

# @app.on_event('shutdown')
# def shutdown():
    # DESCONEXIÓN COMENTADA DE MOMENTO
    # if not connection.is_closed():
    #     connection.close()

# TODO: ejemplo de respuesta exitosa a la raíz del sitio/API
@app.get('/')
def index():
    return {
        'success-last': True
    }
    
# NOTE: ejemplo para reutilización de métodos ASYNC en el mismo fichero o separados    
@app.get("/regions")
async def regions():
    spot_countries = await get_regions_spotify(platforms["spotify"]["base_url"])
    return {
        "spotify_countries": spot_countries
    }
    
 
def num_there(s):
    return any(i.isdigit() for i in s) 
     
async def get_regions_spotify(url):
    asession = AsyncHTMLSession()
    html = await asession.get(url)
    await html.html.arender(sleep=3)
    soup = BeautifulSoup(html.text, "html.parser")
    drop_down = soup.find_all("div",{"class": "responsive-select", "data-type":"country"})[2]
    countries = {}
    lists = drop_down.find_all("li")
    for l in lists:
        countries[l.text] = {
            "tag":l.attrs.get("data-value", None),
            "url":url + l.attrs.get("data-value", None)
        }

    return countries    

async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()


    

# NOTE: método funcional DEPRECADO! como parte del mecacnismo
@app.get('/ext-position-table-by-league')
async def extPositionTableByLeague__Deprecated(path_to_scrape: str = None):

    utilidades_global = UtilitiesMontecarlo()
    exception_content = ''
    status_code       = None
    sistema           = platform.system()
    os_name           = format(sistema)

    # URL SEMILLA
    url = "https://www.goal.com/es-co/primera-a/clasificaci%C3%B3n/2ty8ihceabty8yddmu31iuuej"
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')    
    options.add_argument('--disable-dev-shm-usage')    
    equipos_posicion = []
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:        
        # REQUERIMIENTO AL SERVIDOR
        driver.get(url)
        soup_posiciones  = BeautifulSoup(driver.page_source, 'lxml')
        lista_de_equipos = soup_posiciones.find_all('div', class_='wff_standings_table_row')
        
        for equipo in lista_de_equipos: # ITERAR ELEMENTO POR ELEMENTO    

            posicion_equipo = equipo.find(class_='wff_standings_position_marker').text.lstrip().rstrip()
            nombre_equipo   = equipo.find(class_='wff_participant_name').text.lstrip().rstrip()
            logo_equipo     = equipo.find(class_='wff_flag_logo_img').get('src')
            
            # Grupo de estadísticas
            estadisticas_equipo   = equipo.find_all(class_='wff_standings_stats_box')
            cantidad_estadisticas = len(estadisticas_equipo)        
            dict_estadisticas     = {}
            contador              = 0
            goles_a_favor         = ''
            goles_en_contra       = ''

            # recorriendo estadísticas
            while contador < cantidad_estadisticas:

                est          = estadisticas_equipo[contador]
                item_dynamic = est.select_one('div > div').text
                
                if contador == 4:
                    goles_favor_y_contra = item_dynamic.strip().replace(" ", "")
                    goles_favor_y_contra = goles_favor_y_contra.split('-')
                    
                    print("elemento #4: split ", goles_favor_y_contra)
                    
                    if len(goles_favor_y_contra) > 0:
                        goles_a_favor   = goles_favor_y_contra[0]
                        goles_en_contra = goles_favor_y_contra[1]
                    
                    dict_estadisticas[contador] = item_dynamic.strip().replace(" ", "")
                else:
                    dict_estadisticas[contador] = item_dynamic.strip()            
                
                contador+=1        
            
            # grupo de últimos partidos jugados
            ultimos_partidos_jugados_container = equipo.find(class_='wff_form')
            ultimos_jugados_items              = ultimos_partidos_jugados_container.find_all(class_='wff_form_ball')
            cantidad_ultimos_jugados           = len(ultimos_jugados_items)        
            contador                           = 0
            dict_ultimos_jugados               = {}
            
            if cantidad_ultimos_jugados > 0:
                operaciones_tabla = TablaPosiciones() 
            
            while contador < cantidad_ultimos_jugados:

                jugado       = ultimos_jugados_items[contador]            
                item_dynamic = jugado.select_one('div.wff_label_text').text
                item_dynamic = item_dynamic.strip()
                
                if item_dynamic != '?':                
                    res_numerico = operaciones_tabla.transcribir_partidos_jugados(
                        item_dynamic
                    )
                    dict_ultimos_jugados[contador] = res_numerico
                    
                contador+=1            
            
            equipos_posicion.append({
                'nombre_equipo_acronimo':       '',
                'nombre_equipo_full':           utilidades_global.retornar_cadena_sin_acento(nombre_equipo),
                'url_logo_equipo':              logo_equipo,
                'posicion':                     posicion_equipo,
                'partidos_jugados':             dict_estadisticas[0] if dict_estadisticas[0] is not None else '',
                'partidos_ganados':             dict_estadisticas[1] if len(dict_estadisticas) > 0 else '',
                'partidos_empatados':           dict_estadisticas[2] if len(dict_estadisticas) > 1 else '',
                'partidos_perdidos':            dict_estadisticas[3] if len(dict_estadisticas) > 2 else '',
                'goles_a_favor':                goles_a_favor,
                'goles_en_contra':              goles_en_contra,
                'goles_diferencia':             dict_estadisticas[5] if len(dict_estadisticas) > 4 else '',
                'puntos':                       dict_estadisticas[6] if len(dict_estadisticas) > 5 else '',
                'resultados_ultimos_5_jugados': dict_ultimos_jugados,
            })

        status_code = 200

    except Exception as ex:
        status_code = 500
        exception_content = ex

    return {
        'status_code': status_code,
        'tabla_posiciones': equipos_posicion,
        'path_to_scrape': path_to_scrape,
        'exception_content': exception_content
    }

@app.get('/ext-position-table-by-league-experimental')
async def extPositionTableByLeagueExperimental(path_to_scrape: str = None):

    utilidades_global = UtilitiesMontecarlo()
    exception_content = ''
    status_code       = None
    sistema           = platform.system()
    os_name           = format(sistema)

    # URL SEMILLA
    url = "https://www.goal.com/es-co/primera-a/clasificaci%C3%B3n/2ty8ihceabty8yddmu31iuuej"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')    
    options.add_argument('--disable-dev-shm-usage')    
    equipos_posicion = []
    
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    service = Service(ChromeDriverManager().install()) 
    driver  = webdriver.Chrome(service=service, options=options)        
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:        
        # REQUERIMIENTO AL SERVIDOR
        driver.get(url)
        soup_posiciones  = BeautifulSoup(driver.page_source, 'lxml')
        lista_de_equipos = soup_posiciones.find_all('div', class_='wff_standings_table_row')         
        
        for equipo in lista_de_equipos: # ITERAR ELEMENTO POR ELEMENTO    

            posicion_equipo = equipo.find(class_='wff_standings_position_marker').text.lstrip().rstrip()
            nombre_equipo   = equipo.find(class_='wff_participant_name').text.lstrip().rstrip()
            logo_equipo     = equipo.find(class_='wff_flag_logo_img').get('src')
            
            # Grupo de estadísticas
            estadisticas_equipo   = equipo.find_all(class_='wff_standings_stats_box')
            cantidad_estadisticas = len(estadisticas_equipo)        
            dict_estadisticas     = {}
            contador              = 0            
            goles_a_favor         = ''
            goles_en_contra       = ''

            # recorriendo estadísticas
            while contador < cantidad_estadisticas:

                est          = estadisticas_equipo[contador]
                item_dynamic = est.select_one('div > div').text
                # dict_estadisticas[contador] = item_dynamic.strip()
                
                if contador == 4:
                    goles_favor_y_contra = item_dynamic.strip().replace(" ", "")
                    goles_favor_y_contra = goles_favor_y_contra.split('-')                    
                    print("elemento #4: split ", goles_favor_y_contra)
                    
                    if len(goles_favor_y_contra) > 0:
                        goles_a_favor   = goles_favor_y_contra[0]
                        goles_en_contra = goles_favor_y_contra[1]
                    
                    dict_estadisticas[contador] = item_dynamic.strip().replace(" ", "")
                else:
                    dict_estadisticas[contador] = item_dynamic.strip()            
                
                contador+=1        
            
            # grupo de últimos partidos jugados
            ultimos_partidos_jugados_container = equipo.find(class_='wff_form')
            ultimos_jugados_items              = ultimos_partidos_jugados_container.find_all(class_='wff_form_ball')
            cantidad_ultimos_jugados           = len(ultimos_jugados_items)        
            contador                           = 0
            dict_ultimos_jugados               = {}
            
            if cantidad_ultimos_jugados > 0:
                operaciones_tabla = TablaPosiciones() 
            
            while contador < cantidad_ultimos_jugados:
                jugado       = ultimos_jugados_items[contador]            
                item_dynamic = jugado.select_one('div.wff_label_text').text
                item_dynamic = item_dynamic.strip()
                
                if item_dynamic != '?':                
                    res_numerico = operaciones_tabla.transcribir_partidos_jugados(
                        item_dynamic
                    )
                    dict_ultimos_jugados[contador] = res_numerico
                    
                contador+=1            
            
            equipos_posicion.append({
                'nombre_equipo_acronimo':       '',
                'nombre_equipo_full':           utilidades_global.retornar_cadena_sin_acento(nombre_equipo),
                'url_logo_equipo':              logo_equipo,
                'posicion':                     posicion_equipo,
                'partidos_jugados':             dict_estadisticas[0] if dict_estadisticas[0] is not None else '',
                'partidos_ganados':             dict_estadisticas[1] if len(dict_estadisticas) > 0 else '',
                'partidos_empatados':           dict_estadisticas[2] if len(dict_estadisticas) > 1 else '',
                'partidos_perdidos':            dict_estadisticas[3] if len(dict_estadisticas) > 2 else '',
                'goles_a_favor':                goles_a_favor,
                'goles_en_contra':              goles_en_contra,
                'goles_diferencia':             dict_estadisticas[5] if len(dict_estadisticas) > 4 else '',
                'puntos':                       dict_estadisticas[6] if len(dict_estadisticas) > 5 else '',
                'resultados_ultimos_5_jugados': dict_ultimos_jugados,
            })
        
        status_code = 200
    
    except Exception as ex:    
        status_code = 500
        exception_content = ex
        
    return {
        'status_code': status_code,
        'tabla_posiciones': equipos_posicion,
        'path_to_scrape': path_to_scrape,
        'exception_content': exception_content
    }

# TODO: este método vuela una vez que se testee perfectamente los métodos activos como parte del modelo
@app.get('/scanear2')
async def scrapper2(matches_league_path: str = None, position_table_league_path: str = None):    
    
    # TODO: Creación de instancias/utilidades
    utilidades_global = UtilitiesMontecarlo()
    fecha_actual = datetime.now()
    
    url_liga_betplay_jornadas = platforms["resultados-futbol"][0]
    # json.loads
    print("arr liga bet play jornadas:; ", url_liga_betplay_jornadas)
    print("json.dumps ::::::::::::::::::::::::::", url_liga_betplay_jornadas["url_liga_colombia"])
    
    url0_finalizacion = "https://www.resultados-futbol.com/apertura_colombia2024/grupo1/calendario"
    page0 = urlopen(url0_finalizacion).read()
    soup0 = BeautifulSoup(page0)
    
    # adding 2 seconds time delay
    time.sleep(2)
    tabla0 = soup0.select(".boxhome-2col")
    arr_aplazados = []
    arr_contenido_partidos = []
    arr_jornadas_content = []
    
    # Recorriendo todos los partidos por jornadas de una temporada (semestre)
    for table in tabla0:
         
        jornada = table.find_all("span", class_="titlebox") 
        jornada = jornada[0].text
        rows = table.select('table tr')
         
        for row in rows:
            
            # ANCHOR - Obteniendo los nombres de los equipos
            equipos = row.find_all("img")
            
            if len(equipos) > 0:
                equipo_1 = equipos[0]
                equipo_1 = equipo_1.get("alt")        
                equipo_2 = equipos[1]
                equipo_2 = equipo_2.get("alt")
        
            # validar partido aplazado
            posible_partido_aplazado = row.select("td.rstd")
            
            # posible marcador/fecha partido
            contenido_partido = row.select("td.rstd :not(span)")
            
            # fecha del partido
            fecha_corta_partido = row.select("td.fecha")
            # fecha & hora
            fecha_hora_partido = row.select("td.rstd span.dtstart")
                        
            
            if len(fecha_hora_partido) > 0:
                fecha_hora_partido = fecha_hora_partido[0].text
                
                if fecha_hora_partido is not None:
                    particion_fecha_partido = fecha_hora_partido.split("T")
                    
                    if len(particion_fecha_partido) > 0:
                        fecha_hora_partido = particion_fecha_partido[0].strip() + " " + particion_fecha_partido[1].strip()                    
                            
                        fecha_p = datetime.strptime(fecha_hora_partido, '%Y-%m-%d %H:%M:%S')
                        fecha_p2 = datetime.strftime(fecha_actual, '%Y-%m-%d %H:%M:%S')
                        print("ttttttttttttttttttttttttttttttttttt ", type(fecha_p))
                        print("ddddddddddddddddddddddddddddd ", " ahora: ",type(fecha_actual))
                        print("reswtassssssssssssssssssss ", (fecha_p - fecha_actual))

            
            if len(fecha_corta_partido) > 0:
                print(fecha_corta_partido)
                fecha_corta_partido = fecha_corta_partido[0].text
                
            

            # ANCHOR Validación del contenido del partido            
            # print("contenido partido:::: ", len(contenido_partido))
            
            if len(contenido_partido) > 0:
                # print("CONTENIDO PARTIDO <<<<<<<<<<<<<<<<<<<<<< ///////////////////  ", contenido_partido[0])


                # ANCHOR Validación de partidos aplazados
                if len(posible_partido_aplazado) > 0:
                    
                    cadena_texto_val_partido = posible_partido_aplazado[0].text.strip('\n')
                    cadena_texto_val_partido = cadena_texto_val_partido.strip('\t')                

                    arr_aplazados.append({
                        'aplazado': cadena_texto_val_partido,
                        'coincidencia': 'Apl' in cadena_texto_val_partido
                    })
                    # if posible_partido_aplazado[0].text == 'Apl':

                
                # ANCHOR - Validar que el partido ya haya pasado
                contenido_a_evaluar = contenido_partido[0].text
                contenido_a_evaluar = contenido_a_evaluar.strip()
                
                goles_equipo_1 = ''
                goles_equipo_2 = ''
                
                if "-" or ":" in contenido_a_evaluar:
                    # test
                    if "-" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split("-")
                        goles_equipo_1 = contenido_a_evaluar[0].strip()
                        goles_equipo_2 = contenido_a_evaluar[1].strip()
                        
                    elif ":" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split(":")
                        goles_equipo_1 = "x"
                        goles_equipo_2 = "x"
                        
                    detalle_partido_jornada = {
                        'jornada'              : jornada,
                        'fecha_corta_partido'  : fecha_corta_partido,
                        'fecha_hora_partido'   : fecha_hora_partido,
                        'equipo1'              : utilidades_global.retornar_cadena_sin_acento(equipo_1),
                        'equipo2'              : utilidades_global.retornar_cadena_sin_acento(equipo_2),
                        'contenido_partido'    : contenido_partido[0].text,
                        'goles_equipo1'        : goles_equipo_1,
                        'goles_equipo2'        : goles_equipo_2,
                        'partido_aplazado_flag': cadena_texto_val_partido,
                    }
                    
                    arr_contenido_partidos.append(detalle_partido_jornada)


                
            # if len(resultado_goles_partido) > 0:
            #     print("goles partido ¿? ????????????????????? ", resultado_goles_partido[0].text)
            
            # link_path_detalles = link_detalles_partido.get('href')
            
            # fpartido = row.select("td.fecha") 
            
            # print("jornada: ", jornada, "fecha partido: ", type(fpartido), " ::: ", fpartido[0].text)
            # print("Resumen partido >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> :::::::::::::: ", link_detalles_partido)
    
            # ******************** https://www.resultados-futbol.com/
            
            # url_details  = "https://www.resultados-futbol.com" + link_detalles_partido
            # page_details = urlopen(url_details).read()
            # soup_details = BeautifulSoup(page_details)            

            # print(" &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& ", soup_details)
            

        # solo partidos jugados
        if len(arr_contenido_partidos) > 0:
            arr_jornadas_content.append(arr_contenido_partidos)

        arr_contenido_partidos = []        



    # ----------------------------------------------------------------------------------------------
    position_table_league_for_date = []
    matches_league_for_date = []
    
    # utilidades = Scrapper()
    
    #      https://apuestas.wplay.co/es/t/19311/Colombia-Primera-A
    url = "https://apuestas.wplay.co/es/t/19311/Colombia-Primera-A"
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    page2 = urlopen(req).read().decode('utf8')
    #page2 = urlopen(req, timeout=10).read()
    
    soup = BeautifulSoup(page2)
    
    
    # TODO: descomentar esto
    tabla = soup.find("table")
    rows = tabla.find_all('tr')
        
    for row in rows:
        # print("row::: ")
        # if (row.find('th', {"scope":"row"}) != None):
        time_hour = row.find_all("span", class_="time")
        time_date = row.find_all("span", class_="date")
        
        # print("hour: ", time_hour[0].text)
        # print("tome: ", time_date[0].text)
        
        partido1 = row.find_all("td", class_="seln")
        
        equipo1 = row.select("td div > button > span > span.seln-label > span > span")
        cuota_equipo = row.select("td div > button > span .price.dec")
        # print("equipo:::::: ", equipo1[0].text, "  cuota: ", cuota_equipo[0].text, " empate.:: ", cuota_equipo[1].text)        
        # print("equipo2:::::: ", equipo1[2].text, " cupta equipo 2: ", cuota_equipo[2].text)
        
        # CREANDO POR CADA PARTIDO EL OBJECTO CON LA INFO CORRESPONDIENTE
        match_date = {
            'time_match': time_hour[0].text,
            'date_match': time_date[0].text,
            'team_local': equipo1[0].text,
            'quota_team_local': cuota_equipo[0].text,
            'quota_tie': cuota_equipo[1].text,
            'team_visiting': equipo1[2].text,
            'quota_team_visiting': cuota_equipo[2].text
        }

        matches_league_for_date.append(match_date)    
 
    # ----------------------------------------------------------------------------------------------           
    return {
        'success': True,
        'matches_league_path': matches_league_path,
        'position_table_league_path': position_table_league_path,
        'matches_wplay': matches_league_for_date,
        'aplazados': arr_aplazados,
        'partidos_por_jornada': arr_jornadas_content
    } 

@app.get('/scrape-zoho-crm')
async def scrape_zoho_crm():
    url = "https://accounts.zoho.com/signin"
    # request_url             = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    # exception_content       = None
    
    
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    }

    # REQUERIMIENTO AL SERVIDOR - PARSEO DEL ARBOL CON BEAUTIFUL SOUP
    request_url = Request(url, headers=headers)
    page_url_open = urlopen(request_url).read().decode('utf8')    
    soup = BeautifulSoup(page_url_open, 'html.parser')
        
    
    try:
        # page_url_open = urlopen(request_url).read().decode('utf8')    
        # soup          = BeautifulSoup(page_url_open)    
        
        
        # login_data = {
        #     'login_id': 'crmtecniedcore@gmail.com',
        #     'password': 'Tecnidecore2024*'
        # }
        
        
        # TODO: descomentar esto
        email = soup.find("form input#login_id")
        email['value'] = 'crmtecniedcore@gmail.com'
        
        login_button = soup.find("form button#nextbtn")
        login_button.click()
        
        password = soup.find("form input#password")
        password['value'] = 'Tecnidecore2024*'
        
        login_button = soup.find("form button#nextbtn")
        login_button.click()
        
        time.sleep(13)
        
        # Navigate to the settings page after login
        settings_url = "https://crm.zoho.com/crm/org870195146/settings/functions/myFunctions"
        request_url = Request(settings_url, headers={'User-Agent': 'XYZ/3.0'})
        page_url_open = urlopen(request_url).read().decode('utf8')
        soup = BeautifulSoup(page_url_open)

        print ("test >>> ", settings_url)


        # Check if the settings page loaded successfully
        if "functions" in settings_url:
            return {"success": True, "message": "Settings page loaded successfully"}
        else:
            return {"success": False, "message": "Failed to load settings page"}
              
    except Exception as ex:
        return {"success": False, "message": str(ex)}


@app.get('/scrape-google')
async def scrape_google(query: str = None):
    # options = webdriver.ChromeOptions()
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    
    
    driver = Service(executable_path='C:/drivers_chrome_scraper/chrome-win64/chrome.exe')  # Specify the path to the ChromeDriver
    # Usar ChromeDriverManager para gestionar la versión correcta de ChromeDriver
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)
    
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # driver.get("https://accounts.zoho.com/signin")
    # REQUERIMIENTO AL SERVIDOR
    # driver.get(url)
    

    try:
        soup_posiciones = BeautifulSoup(driver.page_source, 'lxml')    
        
        time.sleep(10)
        # driver.get("https://accounts.zoho.com/signin")
        
        
        
        # Set email
        email_field = soup_posiciones.find_element_by_id("login_id")
        email_field.send_keys("crmtecniedcore@gmail.com")

        # # Click on next button
        next_button = soup_posiciones.find_element_by_id("nextbtn")
        next_button.click()

        # # Wait for the password field to be present
        time.sleep(2)

        # # Set password
        password_field = soup_posiciones.find_element_by_id("password")
        password_field.send_keys("Tecnidecore2024*")

        # # Click on login button
        login_button = soup_posiciones.find_element_by_id("nextbtn")
        login_button.click()
        
        # Wait for the page to load
        time.sleep(5)

        # Check if login was successful by looking for an element that only appears after login
        try:
            driver.find_element_by_id("some_element_id_after_login")
            return {"success": True, "message": "Login successful"}
        except:
            return {"success": False, "message": "Login failed"}

    
    except Exception as ex:
        return {"success": False, "message": str(ex)}
    
    # finally:
    #     driver.quit()


@app.get('/scrape-tecnidecor-facturas')
async def scrape_tecnidecor_facturas(query: str = None):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Intenta ejecutar sin la opción headless para depuración
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    login_usuario = "cartera@tecnidecor.co"
    login_contrasena = "4dm1nTD*"
    function_id = "function_1328761000000103007"
    
    try:
        print("Navegando a la página de inicio de sesión...")
        driver.get("https://accounts.zoho.com/signin")
        time.sleep(5)
        
        print("Estableciendo el correo electrónico...")
        email_field = driver.find_element(By.ID, "login_id")
        email_field.send_keys(login_usuario)

        print("Haciendo clic en el botón siguiente...")
        next_button = driver.find_element(By.ID, "nextbtn")
        next_button.click()

        print("Esperando el campo de contraseña...")
        time.sleep(2)

        print("Estableciendo la contraseña...")
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(login_contrasena)

        print("Haciendo clic en el botón de inicio de sesión...")
        print("Esperando a que la página se cargue...")
        time.sleep(4)
        
        print("Haciendo clic en el botón de inicio de sesión...")
        login_button = driver.find_element(By.ID, "nextbtn")
        login_button.click()
        
        print("Esperando que la página se cargue...")
        time.sleep(5)
        
        print("Navegando a la página de funciones...")
        driver.get("https://crm.zoho.com/crm/org870195146/settings/functions/myFunctions")
        time.sleep(12)
        
        print("Haciendo clic en el elemento con ID function_1328761000000103007")

        element = driver.find_element(By.ID, function_id)
        print(">>> click para abrie el modal: ", element)
        element.click()
        print("Elemento clickeado exitosamente")
        time.sleep(5)

        print("Buscando el segundo span dentro del elemento lyte con la clase especificada...")
        span_element = driver.find_element(By.CSS_SELECTOR, "span[data-zcqa='cf_editFunction']")
        print(" >>>> ", span_element)
        span_element.click()        
        
        time.sleep(15)
        print("Browser will remain open for further operations.")
            
        print("Buscando el elemento con data-zcqa='delgv2execPlay'...")
        element = driver.find_element(By.CSS_SELECTOR, "span[data-zcqa='delgv2execPlay']")
        # TODO: descomentar
        
        print("Elemento clickeado exitosamente")        
        time.sleep(2)
        
        while True:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>> PRESIONANDO EL CLICK PARA EJECUTAR EL PROCESO >>>>>>>>>>>>>>>")
            element = driver.find_element(By.CSS_SELECTOR, "span[data-zcqa='delgv2execPlay']")
            element.click()
            print("iniciando while externo, fn ppal")

            if (wait_for_condition(driver) == "Continue"):
                print("se mantiene el while externo")
                print(">> -- reiniciando el ciclo nuevamente...")
                element = None                  
                continue
            elif (wait_for_condition(driver) == "Exit"):
                print("se rompe el while externo")
                break
        
        print(">>>>>>>>>>>>>>>>>>>>>>>>>> SE TERMINA EL PROCESO >>>>>>>>>>>>>>>")
        
        return{
            "success": True,
            "message": "Proceso de ejecución de función exitoso."            
        }

    except Exception as ex:
        print(f"Error: {str(ex)}")
        return {"success": False, "message": str(ex)}

    finally:
        # Keep the browser open for further operations
        print("Browser will remain open for further operations.")


def get_unique_download_path(base_path: str, username: str) -> str:
    """
    Genera una carpeta única para el usuario o sesión.

    Args:
        base_path (str): Ruta base donde se almacenarán los archivos.
        username (str): Nombre del usuario o identificador de la sesión.

    Returns:
        str: Ruta completa de la carpeta de descargas.
    """
    # Crear una carpeta específica para el usuario
    user_folder = os.path.join(base_path, username)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def getDateToday():

    dateTodayValue = date.today()
    formatDate = dateTodayValue.strftime("%d/%m/%Y")
    day, month, year = formatDate.split('/')
    finalDate = f"{day}/{month}/{year}" # Reconstruir la fecha formateada sin el cero en el mes

    return finalDate

def periodRecaudoDate():

    todayDate = date.today()
    # Formatear la fecha
    yesterdayDate = todayDate - timedelta(days=1)
    
    finalDate = yesterdayDate.strftime("%d/%m/%Y")
    # Separar el día, mes y año
    day, mouth, year = finalDate.split('/')
    # Quitar el cero a la izquierda si está presente
    day = day.lstrip('0')
    mouth = mouth.lstrip('0')
    # Reconstruir la fecha formateada sin el cero en el mouth
    finalDateRecaudo = f"{day}/{mouth}/{year}"

    #Calcula la fecha Inicial Restando x dias
    fechaInicial = yesterdayDate - timedelta(days=2)
    finalDate = fechaInicial.strftime("%d/%m/%Y")
    # Separar el día, mes y año
    day, mouth, year = finalDate.split('/')
    # Quitar el cero a la izquierda si está presente
    day = day.lstrip('0')
    mouth = mouth.lstrip('0')
    # Reconstruir la fecha formateada sin el cero en el mouth
    startDateRecaudo = f"{day}/{mouth}/{year}"
    
    return startDateRecaudo ,finalDateRecaudo

def validateCarteraFileIsDownload(driver):
    
    isDownload = False

    try:
        rows = WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr"))
        )
        
        # Imprimir la estructura de la tabla
        for i, row in enumerate(rows):
            columns = row.find_elements(By.XPATH, ".//td")
            print(f"Fila {i}: {[col.text for col in columns]}")
        
        todayDate = getDateToday()

        for row in rows:
            try:
                columns = row.find_elements(By.XPATH, ".//td")
                
                # Imprimir el contenido de las columnas para depuración
                print(f"Columnas en la fila actual: {[col.text for col in columns]}")
                
                if len(columns) < 4:
                    continue
                
                # Buscar el texto en la segunda columna (Tipo)
                valueType = columns[1]  # Index 1 porque es la segunda columna
                getValueType = valueType.text.strip()
                requestDateValue = columns[3]
                getValueDate = requestDateValue.text.strip()
                print(f"Fecha desde la tabla {getValueDate}")
                

                if getValueType.lower() == 'cartera' and getValueDate == todayDate:  # Comparación insensible a mayúsculas/minúsculas
                    isDownload = True
                    try:
                        # Espera explícita para el botón de descarga
                        download_button = WebDriverWait(row, 10).until(
                            EC.element_to_be_clickable((By.XPATH, ".//td[last()]//button"))
                        )
                        download_button.click()
                        break  # Sale del bucle después de hacer clic en el botón
                    
                    except Exception as e:
                        header = "Error"
                        popUpMessage = f"Error al hacer clic en el botón: {e}"
                        # message.notifyError(header, popUpMessage)
                        print(f"Error ", header, popUpMessage)
                    
            except NoSuchElementException:
                header = "Error"
                popUpMessage = "Ocurrio un error al encontrar la fila de Cartera. Por favor cierre el programa y ejecutelo nuevamente."
                # message.notifyError(header, popUpMessage)
                print(f"Error ", header, popUpMessage)
            
                
    except TimeoutException:
        header = "Error"
        popUpMessage = "Ocurrio un error al encontrar el boton. Por favor cierre el programa y ejecutelo nuevamente."
        # message.notifyError(header, popUpMessage)
        print(f"Error ", header, popUpMessage)

    time.sleep(2)

    return isDownload

def get_driver(downloadPath: str):
    options = webdriver.ChromeOptions()
    
    prefs = {
        "download.default_directory": downloadPath,  # Carpeta de descargas
        "download.prompt_for_download": False,  # No preguntar dónde guardar cada descarga
        "download.directory_upgrade": True,  # Cambiar automáticamente la carpeta de descarga si es necesario
        "safebrowsing.enabled": True  # Deshabilitar la protección de navegación segura
    }
    options.add_experimental_option("prefs", prefs)    
    
    # Disable sharing memory across the instances
    options.add_argument('--disable-dev-shm-usage')
    # Initialize a remote WebDriver
    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4444/wd/hub",
        options=options
    )
    return driver


@app.get('/rpa-sura-headless')
async def scrape_sura_headless(query: str = None):
    """ 
    Scrape Sura headless para descargar el informe de cartera.

    Args:
        query (str, optional): _description_. Defaults to None.
    """

    global detener_proceso
    
    username = "10101212"  # Cambia esto por el nombre de usuario deseado

    if getattr(sys, 'frozen', False):
        currentPath = os.path.dirname(sys.executable)
    else:
        currentPath = os.getcwd()

    # filePath = r"filesScrap"
    # downloadFilePath = os.path.join(currentPath, filePath)    
    # print("path download files: ", downloadFilePath)
    
    # Generar una carpeta única para el usuario
    base_download_path = os.path.join(currentPath, "filesScrap")
    downloadFilePath = get_unique_download_path(base_download_path, username)

    print("Ruta de descarga para el usuario:", downloadFilePath)
    driver = get_driver(downloadFilePath)
    driver.maximize_window()

    print("Navegando a la página de inicio de sesión...  /https://asesores.segurossura.com.co/ :::::::::::: ")
    
    try:
        # TODO: a partir de aquí comienza la automatización
        # Navegar a la página de inicio de sesión
        driver.get('https://asesores.segurossura.com.co/')
        
        #Selecciona la opcion NIT
        selectLogin = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentMain_suraType"))
        )
        selectLogin.click()
        
        valueSelectLogin = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//option[@value = 'A']"))
        )
        valueSelectLogin.click()
        
        #Ingresa el valor del nit en el campo Numero de Identificacion
        idNumberField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "suraName"))
        )
        idNumberField.send_keys("8001384245")
        
        # Ingresa la contraseña directamente evitando el captcha
        driver.execute_script("document.getElementsByName('suraPassword')[0].value = '2424'")
        
        loginButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'session-internet'))
        )
        loginButton.click()
        
        print("Esperando a que la página se cargue... se ha presionado click <<<<<<<<<<<<<<<<<<<<<<<<<<<< ")
        ## ------------------------------------------------------------------------------------------------------>
        
        #Se dirije a la pagina de informes de sura
        driver.get("https://asistentevirtualasesores.sura.com/inicio")
        
        time.sleep(10)
        
        openMenuToCartera = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-bars arrow']"))
        )
        openMenuToCartera.click()
        
        asistenciaButton = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Asistente Cartera']"))
        )
        asistenciaButton.click()
        
        goToCarteraButton = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Asistente servicios financieros']"))
        )
        goToCarteraButton.click()

        time.sleep(10)

        # Obtener los identificadores de todas las pestañas
        all_windows = driver.window_handles

        # Cambiar el foco a la nueva pestaña (que es la última en la lista)
        driver.switch_to.window(all_windows[-1])
        
        
        
        consultarCarteraButton = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Consultar']"))
        )
        consultarCarteraButton.click()
        
        aceptarCarteraButton = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Aceptar']"))
        )
        aceptarCarteraButton.click()    
        
        generarInformeButton = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Generar informe de cartera']"))
        )
        generarInformeButton.click()
        
        time.sleep(2)
        
        aceptarCarteraButton2 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Aceptar']"))
        )
        aceptarCarteraButton2.click() 
        
        verInformesCarteraButton = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Ver informes']"))
        )
        verInformesCarteraButton.click()
        
        time.sleep(2)        
        
        
        carteraFileIsDownload = validateCarteraFileIsDownload(driver)
        
        if carteraFileIsDownload == False:
            try:

                #Delay de 5 minutos para que sura tenga tiempo de generar el informe para descargar
                time.sleep(300)

                refreshButton = WebDriverWait(driver, 40).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@nztooltiptitle='Refrescar']"))
                )
                refreshButton.click()
                
                time.sleep(3)

                carteraFileIsDownload = validateCarteraFileIsDownload(driver)

                if carteraFileIsDownload == False:
                    header = "Error"
                    popUpMessage = f"Error al descargar el archivo sura: No se pudo generar."
                    # message.notifyError(header, popUpMessage)
                    print(f"Error ", header, popUpMessage)
            
            except Exception as e:
                header = "Error"
                popUpMessage = f"Error al descargar el archivo sura: Se agotó el tiempo de espera."
                # message.notifyError(header, popUpMessage)
                print(f"Error ", header, popUpMessage)
        # ------------------------------------------------------------------------------------------------------>
                
        #Se dirije a la seccion de Recaudos
        goToRecaudoButton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Medios de recaudo usados por mis clientes']"))
        )
        goToRecaudoButton.click()
        
        fechaInicioInput = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Fecha inicial']"))
        )
        fechaInicioInput.click()
        
        fechaInicial, fechaFinal = periodRecaudoDate()
        
        xpathInicial = f"//td[@title='{fechaInicial}']"      
        # Espera hasta que el calendario esté visible y la fecha específica sea seleccionable
        fecha_elemento = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, xpathInicial))
        )        
        
        # Haz clic en la fecha específica para seleccionarla
        fecha_elemento.click()
        
        xpathFinal = f"//td[@title='{fechaFinal}']"    
        # Espera hasta que el calendario esté visible y la fecha específica sea seleccionable
        fecha_elementoFinal = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, xpathFinal))
        )

        # Haz clic en la fecha específica para seleccionarla
        fecha_elementoFinal.click()
        
        try:
            consultarRecaudoButton = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Consultar']"))
            )
            
            consultarRecaudoButton.click()
            
            time.sleep(30)
        
        except WebDriverException as e:
            driver.refresh()
            fechaInicioInput = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Fecha inicial']"))
            )
            fechaInicioInput.click()
            
            fechaInicial, fechaFinal = periodRecaudoDate()
            
            xpathInicial = f"//td[@title='{fechaInicial}']"      
            # Espera hasta que el calendario esté visible y la fecha específica sea seleccionable
            fecha_elemento = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, xpathInicial))
            )

            # Haz clic en la fecha específica para seleccionarla
            fecha_elemento.click()
            
            xpathFinal = f"//td[@title='{fechaFinal}']"    
            # Espera hasta que el calendario esté visible y la fecha específica sea seleccionable
            fecha_elementoFinal = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, xpathFinal))
            )

            # Haz clic en la fecha específica para seleccionarla
            fecha_elementoFinal.click()
            
            consultarRecaudoButton = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Consultar']"))
            )
            
            consultarRecaudoButton.click()
            
            time.sleep(30)
            
        totalRecaudoButton = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Total']"))
        )
        totalRecaudoButton.click()
        
        time.sleep(3)
                    
        #Descarga el archivo de Recaudo
        downloadFileRecaudoButton = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@nztooltiptitle='Exportar']"))
        )
        downloadFileRecaudoButton.click()
        
        time.sleep(3)                

    except TimeoutException:
        header = "Error"
        popUpMessage = "Ocurrio un error al encontrar el boton. Por favor cierre el programa y ejecutelo nuevamente."
        # message.notifyError(header, popUpMessage) 
        print(f"Error ", header, popUpMessage)


@app.get('/scrape-tecnidecor-facturas-update')
async def scrape_tecnidecor_facturas_update(query: str = None):
    login_usuario = "cartera@tecnidecor.co"
    login_contrasena = "4dm1nTD*"
    function_id = "function_1328761000000103007"
    funcion_facturas_tipo_FE_id = "function_1328761000000016001"
        
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Intenta ejecutar sin la opción headless para depuración
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("Navegando a la página de inicio de sesión...")
        driver.get("https://accounts.zoho.com/signin")
        time.sleep(5)
        
        print("Estableciendo el correo electrónico...")
        email_field = driver.find_element(By.ID, "login_id")
        # email_field.send_keys("crmtecniedcore@gmail.com")
        email_field.send_keys(login_usuario)

        print("Haciendo clic en el botón siguiente...")
        next_button = driver.find_element(By.ID, "nextbtn")
        next_button.click()

        print("Esperando el campo de contraseña...")
        time.sleep(2)

        print("Estableciendo la contraseña...")
        password_field = driver.find_element(By.ID, "password")
        # password_field.send_keys("Tecnidecore2024*")
        password_field.send_keys(login_contrasena)

        print("Haciendo clic en el botón de inicio de sesión...")
        print("Esperando a que la página se cargue...")
        time.sleep(4)
        
        print("Haciendo clic en el botón de inicio de sesión...")
        login_button = driver.find_element(By.ID, "nextbtn")
        login_button.click()
        
        print("Esperando que la página se cargue...")
        time.sleep(5)
        
        print("Navegando a la página de funciones...")
        driver.get("https://crm.zoho.com/crm/org870195146/settings/functions/myFunctions")
        time.sleep(12)

        print(f"Haciendo clic en el elemento con ID {function_id}...")

        element = driver.find_element(By.ID, "function_1328761000000103007")
        print(">>> click para abrie el modal: ", element)
        element.click()
        print("Elemento clickeado exitosamente")
        time.sleep(5)

        print("Buscando el segundo span dentro del elemento lyte con la clase especificada...")
        span_element = driver.find_element(By.CSS_SELECTOR, "span[data-zcqa='cf_editFunction']")
        print(" >>>> ", span_element)
        span_element.click()        
        
        time.sleep(15)
        print("Browser will remain open for further operations.")
            
        print("Buscando el elemento con data-zcqa='delgv2execPlay'...")
        element = driver.find_element(By.CSS_SELECTOR, "span[data-zcqa='delgv2execPlay']")
        # TODO: descomentar
        
        print("Elemento clickeado exitosamente")        
        time.sleep(2)
        
        while True:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>> PRESIONANDO EL CLICK PARA EJECUTAR EL PROCESO >>>>>>>>>>>>>>>")
            element = driver.find_element(By.CSS_SELECTOR, "span[data-zcqa='delgv2execPlay']")
            element.click()
            print("iniciando while externo, fn ppal")

            if (wait_for_condition(driver) == "Exit"):
                print("se rompe el while externo")
                break
            elif (wait_for_condition(driver) == "Continue"):
                print("se mantiene el while externo")
                print(">> -- reiniciando el ciclo nuevamente...")
                element = None                  
                continue    
        
        print(">>>>>>>>>>>>>>>>>>>>>>>>>> SE TERMINA EL PROCESO >>>>>>>>>>>>>>>")
        
        return{
            "success": True,
            "message": "Proceso de ejecución de función exitoso."            
        }

    except Exception as ex:
        print(f"Error: {str(ex)}")
        return {"success": False, "message": str(ex)}

    finally:
        # Keep the browser open for further operations
        print("Browser will remain open for further operations.")



def wait_for_condition(driver):    
    STATUS_CONDITION_EXIT="Exit"
    STATUS_CONDITION_CONTINUE="Continue"
    CHECK_STATUS_TRUE="True"
    CHECK_STATUS_FALSE="False"
    CHECK_STATUS_NONE="None"
    status_condition_response = ""

    while True:

        if check_status(driver) == CHECK_STATUS_FALSE:
            status_condition_response = STATUS_CONDITION_CONTINUE
            print("se mantiene el while de wait_for_condition pero salta al primer while <<<<< | ")
            # break
            return status_condition_response
        elif check_status(driver) == CHECK_STATUS_TRUE:
            print("se rompe el while de wait_for_condition")
            status_condition_response = STATUS_CONDITION_EXIT
            # break
            return status_condition_response        
        else:
            print("se mantiene el while de wait_for_condition y NO salta al primer while >>>>>  | ")
            status_condition_response = CHECK_STATUS_NONE
            continue

def check_status(driver):
    CHECKED_RETURN_TRUE = "STATUS_WHILE_RETURN_PROCESS=TRUE".strip('"')
    CHECKED_RETURN_FALSE = "STATUS_WHILE_RETURN_PROCESS=FALSE".strip('"')
    CHECK_STATUS_TRUE="True"
    CHECK_STATUS_FALSE="False"
    CHECK_STATUS_NONE="None"
    DELAY_TIME_VALUE = 10                                                                                                                                                                                                                                                                                                          

    # Verificar si el contenido de la contraseña corresponde con el texto: "STATUS_WHILE_RETURN_PROCESS=TRUE"
    print("Verificando contenedor de la consola ... dentro de check status")
    
    time.sleep(DELAY_TIME_VALUE)

    element = driver.find_element(By.CSS_SELECTOR, ".delg_console_container")
    
    if element:
        list_items = element.find_elements(By.CLASS_NAME, "delg_console_list_view_item")
        texto_salida_consola = ""
        
        if list_items:
            last_item = list_items[-1]
            span_element = last_item.find_element(By.CSS_SELECTOR, "div.dB span")
            texto_salida_consola = span_element.text
            print("Texto de la consola:", texto_salida_consola)
        else:
            print("No se encontraron elementos en la lista")
    
    print("Texto de la consola:RESULT ", texto_salida_consola.strip())

    status_text = texto_salida_consola.strip().strip('"')
    
    if status_text == CHECKED_RETURN_TRUE.strip():
        print("!!!!!!!!!!!!!!!!! STATUS_WHILE_RETURN_PROCESS=TRUE")
        return CHECK_STATUS_TRUE
    elif status_text == CHECKED_RETURN_FALSE.strip():
        print("¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡ STATUS_WHILE_RETURN_PROCESS=FALSE >>", status_text)
        return CHECK_STATUS_FALSE
    else:
        print("# se mantiene FALSE")
        return CHECK_STATUS_NONE


# TODO: clase de ejemplo NO funcional 
class CalendarioLiga():    
    
    def __init__(self, semestre):
        self.semestre = semestre
        

# TODO: clase de ejemplo NO funcional
class Scrapper():
    
    def scrapedata(self, tag):
        url = f'https://quotes/toscrape/tag/{tag}'
        # s = HTMLSession()
        # r = s.get(url)
        # print(r.status_code)
        
    def getTest (self):
        return '817'
    
    # Python3 code to remove whitespace
    def remove(self, string):
        return string.replace(" ", "")
    
    
    
    

async def get_calendar_data_details(url_details: str, count_fechas_partido):
    # details
    print(">>>>> MATCH DETAILLS::: ", url_details, " $$$$ contador $$$$ ", count_fechas_partido)
    
    detalles_estadisticas = {}
    
    page_details = urlopen(url_details).read()
    soup_details = BeautifulSoup(page_details)                        
    table_main = soup_details.select('.boxhome.boxnormal table')
    
    if len(table_main) > 0:
        # print(">>>>> MATCH DETAILLS::: ttablel  ", table_main)
        table_main = table_main[0]
        posesion_balon      = table_main.select('.barstyle.bar4:nth-child(1) td')
        goles               = table_main.select('.barstyle.bar4:nth-child(2) td')
        tiros_a_puerta      = table_main.select('.barstyle.bar4:nth-child(3) td')
        tiros_fuera         = table_main.select('.barstyle.bar4:nth-child(4) td')
        total_tiros         = table_main.select('.barstyle.bar4:nth-child(5) td')
        paradas_del_portero = table_main.select('.barstyle.bar4:nth-child(6) td')
        saques_de_esquina   = table_main.select('.barstyle.bar4:nth-child(7) td')
        fueras_de_juego     = table_main.select('.barstyle.bar4:nth-child(8) td')
        tarjetas_rojas      = table_main.select('.barstyle.bar4:nth-child(9) td')
        asistencias         = table_main.select('.barstyle.bar4:nth-child(10) td')
        sustituciones       = table_main.select('.barstyle.bar4:nth-child(11) td')
        faltas              = table_main.select('.barstyle.bar4:nth-child(12) td')
        # print(">>>>> POSESION MATCH DETAILS::: ----> ----> ----> tablel posesion ", " ttabla main:: ", table_main)
        
        if (len(posesion_balon) > 1):
            
            detalles_estadisticas['equipo_a'] = {
                'posesion'           : posesion_balon[0].text       if len(posesion_balon) > 0 else None,
                'goles'              : goles[0].text                if len(goles) > 0 else None,
                'tiros_a_puerta'     : tiros_a_puerta[0].text       if len(tiros_a_puerta) > 0 else None,
                'tiros_fuera'        : tiros_fuera[0].text          if len(tiros_fuera) > 0 else None,
                'total_tiros'        : total_tiros[0].text          if len(total_tiros) > 0 else None,
                'paradas_del_portero': paradas_del_portero[0].text  if len(paradas_del_portero) > 0 else None,
                'saques_de_esquina'  : saques_de_esquina[0].text    if len(saques_de_esquina) > 0 else None,
                'fueras_de_juego'    : fueras_de_juego[0].text      if len(fueras_de_juego) > 0 else None,
                'tarjetas_rojas'     : tarjetas_rojas[0].text       if len(tarjetas_rojas) > 0 else None,
                'asistencias'        : asistencias[0].text          if len(asistencias) > 0 else None,
                'sustituciones'      : sustituciones[0].text        if len(sustituciones) > 0 else None,
                'faltas'             : faltas[0].text               if len(faltas) > 0 else None
            }
            detalles_estadisticas['equipo_b'] = {
                'posesion'           : posesion_balon[2].text       if len(posesion_balon) > 1 else None,
                'goles'              : goles[2].text                if len(goles) > 1 else None,
                'tiros_a_puerta'     : tiros_a_puerta[2].text       if len(tiros_a_puerta) > 1 else None,
                'tiros_fuera'        : tiros_fuera[2].text          if len(tiros_fuera) > 1 else None,
                'total_tiros'        : total_tiros[2].text          if len(total_tiros) > 1 else None,
                'paradas_del_portero': paradas_del_portero[2].text  if len(paradas_del_portero) > 1 else None,
                'saques_de_esquina'  : saques_de_esquina[2].text    if len(saques_de_esquina) > 1 else None,
                'fueras_de_juego'    : fueras_de_juego[2].text      if len(fueras_de_juego) > 1 else None,
                'tarjetas_rojas'     : tarjetas_rojas[2].text       if len(tarjetas_rojas) > 1 else None,
                'asistencias'        : asistencias[2].text          if len(asistencias) > 1 else None,
                'sustituciones'      : sustituciones[2].text        if len(sustituciones) > 1 else None,
                'faltas'             : faltas[2].text               if len(faltas) > 1 else None
            }
        
    table_main = None
    soup_details = None
    page_details = None
    
    return detalles_estadisticas


#TODO: TENER EN CUENTA ESTE METODO COMO SCRAPER!
# NOTE: método funcional activo como parte del mecacnismo
# NOTE: METODO ACTIVO FUNCIONAL "extCalendarLeagueByLeague
# TODO: quiero ver ra´pido este metodo despues 
@app.get('/ext-calendar-league-by-league')
async def extCalendarLeagueByLeague(path_to_scrape: str = None, get_details_status: bool = False):

    sys.setrecursionlimit(999000) # 10000 es un ejemplo puedes variar el numero incrementando o decrementando
    utilidades_global = UtilitiesMontecarlo()
    # fecha_actual = datetime.now()
    exception_content = None
    url_base_page = "https://www.resultados-futbol.com"
    
    # url = "https://www.resultados-futbol.com/premier2024/grupo1/calendario" #"https://www.resultados-futbol.com/apertura_colombia2024/grupo1/calendario"
    # url = "https://www.resultados-futbol.com/usa2024/grupo1/calendario"
    url = path_to_scrape if path_to_scrape is not None else "https://www.resultados-futbol.com/competicion/primera/2026/grupo1/calendario" 
    #"https://www.resultados-futbol.com/brasil2024/grupo1/calendario"
    
    page0 = urlopen(url).read()
    soup0 = BeautifulSoup(page0)
    
    # adding 2 seconds time delay
    time.sleep(1)
    tabla0 = soup0.select(".col-calendar-content .boxhome.boxhome-2col")
    
    if tabla0 is not None and len(tabla0) > 0:
        print("SI EXISTEN REGISTROS ACTIVOS - calendario")
        # tabla contains some value or records
        # continue with your code here
    else:
        print("NO EXISTEN REGISTROS ACTIVOS - calendario")
        # tabla is empty or None
        # handle the case accordingly    
    
    arr_aplazados = []
    arr_contenido_partidos = []
    arr_jornadas_content = []
    
    # Contadores
    count_fechas_partido = 0
    count_fechas_calendar = 0
    
    # Recorriendo todos los partidos por jornadas de una temporada (semestre)
    for table in tabla0:
         
        jornada = table.find_all("span", class_="titlebox") 
        jornada = jornada[0].text
        rows = table.select('table tr')                
         
        for row in rows:
            
            # ANCHOR - Obteniendo los nombres de los equipos
            equipos = row.find_all("img")
            
            if len(equipos) > 0:
                equipo_1 = equipos[0]
                equipo_1 = equipo_1.get("alt")
                equipo_2 = equipos[1]
                equipo_2 = equipo_2.get("alt")
            
            # validar partido aplazado
            posible_partido_aplazado = row.select("td.rstd")
            
            # posible marcador/fecha partido
            contenido_partido = row.select("td.rstd :not(span)")
            
            # detalles partido, alternativas
            link_detalles_partido = row.find("a", {"class": "url"}).get("href")
            link_detalles_partido = row.find("a", {"class": "link"})
            
            # fecha del partido
            fecha_corta_partido = row.select("td.fecha")
            # fecha & hora
            fecha_hora_partido = row.select("td.rstd span.dtstart")
                                    
            if len(fecha_hora_partido) > 0:

                fecha_hora_partido = fecha_hora_partido[0].text
                
                # if fecha_hora_partido is not None:
                #     particion_fecha_partido = fecha_hora_partido.split("T")
            
            if len(fecha_corta_partido) > 0:
                print(fecha_corta_partido)
                fecha_corta_partido = fecha_corta_partido[0].text

            # ANCHOR Validación del contenido del partido            
            if len(contenido_partido) > 0:

                # ANCHOR Validación de partidos aplazados
                if len(posible_partido_aplazado) > 0:
                    
                    cadena_texto_val_partido = posible_partido_aplazado[0].text.strip('\n')
                    cadena_texto_val_partido = cadena_texto_val_partido.strip('\t')                

                    arr_aplazados.append({
                        'aplazado': cadena_texto_val_partido,
                        'coincidencia': 'Apl' in cadena_texto_val_partido
                    })

                # ANCHOR - Validar que el partido ya haya pasado
                contenido_a_evaluar = contenido_partido[0].text
                contenido_a_evaluar = contenido_a_evaluar.strip()
                
                goles_equipo_1 = ''
                goles_equipo_2 = ''
                flag_partido_jugado = False
                link_full_estadisticas_detalles_content = ''
                
                if "-" or ":" in contenido_a_evaluar:
                    estadisticas_jornada_local = {}
                                        
                    if "-" in contenido_a_evaluar:  

                        contenido_a_evaluar = contenido_a_evaluar.split("-")
                        goles_equipo_1 = contenido_a_evaluar[0].strip()
                        goles_equipo_2 = contenido_a_evaluar[1].strip()
                        
                        if num_there(goles_equipo_1) and num_there(goles_equipo_2) and isinstance(int(goles_equipo_1), numbers.Number) and isinstance(int(goles_equipo_2), numbers.Number):
                                          
                            flag_partido_jugado = True                                
                            
                            # >>>
                            # solo si el partido se jugó se consultas los detalles:
                            # detalles partido, alternativas
                            if bool(get_details_status):
                                print('>>> partido jugado: ', equipo_1, ' vs ', equipo_2, ' - ', goles_equipo_1, ' - ', goles_equipo_2)
                                link_detalles_partido = row.find("a", {"class": "url"}).get("href")
                                link_full_estadisticas_detalles_content =  url_base_page + link_detalles_partido                        

                        else:
                            goles_equipo_1 = "x"
                            goles_equipo_2 = "x"
                            link_full_estadisticas_detalles_content = ""                                                                            

                    # NOTE: Sin fecha asignada, es partido NO jugado: partido pendiente por jugar
                    elif ":" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split(":")
                        goles_equipo_1 = "x"
                        goles_equipo_2 = "x"
                        link_full_estadisticas_detalles_content = ""
                         
                    detalle_partido_jornada = {
                        'jornada'              : jornada,
                        'partiddo_jugado'      : flag_partido_jugado,
                        'fecha_corta_partido'  : fecha_corta_partido,
                        'fecha_hora_partido'   : fecha_hora_partido,
                        'equipo1'              : utilidades_global.retornar_cadena_sin_acento(equipo_1),
                        'equipo2'              : utilidades_global.retornar_cadena_sin_acento(equipo_2),
                        'contenido_partido'    : contenido_partido[0].text,
                        'goles_equipo1'        : goles_equipo_1,
                        'goles_equipo2'        : goles_equipo_2,
                        'partido_aplazado_flag': cadena_texto_val_partido,
                        'url_estadisticas_detalles': link_full_estadisticas_detalles_content,
                        'estadisticas_detalles': estadisticas_jornada_local,
                        'partido_procesado_status': False
                    }
                    
                    arr_contenido_partidos.append(detalle_partido_jornada)

        # solo partidos jugados
        if len(arr_contenido_partidos) > 0:
            arr_jornadas_content.append(arr_contenido_partidos)

        arr_contenido_partidos = []
        count_fechas_calendar = count_fechas_calendar + 1
    
    # TODO: pendiente probar!
    # get_details_status = False
    
    # REVIEW: evaluar después y aprobar.
    evaluar_detalles_calendario = bool(get_details_status)
    
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('evaluar_detalles_calendario: ', evaluar_detalles_calendario)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    

    # NOTE: Si se solicitan detalles de estadísticas, se procesan y asignan:
    # NOTE: así estaba antes: if bool(get_details_status) == True:
    if evaluar_detalles_calendario:
            
            count_fechas_calendar = 0
            count_sin_detalles = 0            
            contador_calendarios = len(arr_jornadas_content)
                        
            for calendario in arr_jornadas_content:
                
                count_fechas_partido = 0
                count_sin_detalles = 0
                
                # print("TEMPORAL >>> ", calendario)
                
                for fecha in calendario:                
                    
                    # count_fechas_partido = count_fechas_partido + 1
                    count_fechas_partido += 1
                    
                    if  fecha['partido_procesado_status'] is False:

                        # NOTE: comentado temporalmente
                        # if fecha['url_estadisticas_detalles'] != "":
                        #     url = fecha['url_estadisticas_detalles']                            
                        #     arr_temp = await get_calendar_data_details(str(url), count_fechas_partido)
                        #     fecha['estadisticas_detalles'] = arr_temp
                        #     fecha['partido_procesado_status'] = True
                        #     arr_temp = {}
                        # else: 
                        #     count_sin_detalles = count_sin_detalles + 1
                        #     print("sin detalles, fecha partido: ", count_fechas_partido)
                        if not fecha['partido_procesado_status']:
                            if fecha['url_estadisticas_detalles'] != "":
                                # url = fecha['url_estadisticas_detalles']                            
                                arr_temp = await get_calendar_data_details(str(fecha['url_estadisticas_detalles']), count_fechas_partido)
                                fecha['estadisticas_detalles'] = arr_temp
                                fecha['partido_procesado_status'] = True
                            else: 
                                count_sin_detalles += 1
                                print(f"sin detalles, fecha partido: {count_fechas_partido}")
                        
                #count_fechas_calendar = count_fechas_calendar + 1
                count_fechas_calendar += 1
                
                if contador_calendarios == count_fechas_calendar:
                    break

    return {
        'success': True,
        'partidos_por_jornada': arr_jornadas_content
    }    
    
#TODO: TENER EN CUENTA ESTE METODO COMO SCRAPER!    
# TODO: pendiente agregar bloques try except 
# NOTE: REFACTORIZAR MÉTODO
# NOTE: método funcional ACTIVO como parte del mecacnismo que permite extraer tabla de posiciones con la nueva fuente deportiva
@app.get('/ext-position-table-by-league-stable')
async def extPositionTableByLeagueStable(path_to_scrape: str = None):
    # extPositionTableByLeagueStable("https://www.fctables.com/brazil/serie-a/")

    utilidades_global = UtilitiesMontecarlo()
    exception_content = ''
    status_code = None
    sistema = platform.system()
    # TODO: saber si estamos en windows o Linux
    os_name = format(sistema)
    #equipos 
    equipos_posicion = []

    # URL SEMILLA
    url = path_to_scrape if path_to_scrape != None else "https://www.fctables.com/spain/liga-adelante/"
    # NOTE: Habilitar
    # "https://www.fctables.com/brazil/serie-a/"
    
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    }

    # REQUERIMIENTO AL SERVIDOR - PARSEO DEL ARBOL CON BEAUTIFUL SOUP
    request_url = Request(url, headers=headers)
    page_url_open = urlopen(request_url).read().decode('utf8')    
    soup = BeautifulSoup(page_url_open, 'html.parser')
    
    # TODO: Validar
    contenedor_equipos = soup.select('div.template_table div.table-responsive table.stage-table')
    
    
    # VALIDAR EXISTENCIA
    if len(contenedor_equipos) > 0:
        print("SI EXISTEN REGISTROS ACTIVOS - tabla de posiciones")
        # Code to be executed if contenedor_equipos contains records
        # ...
        ## refactrorizar ´para el caso en que todo esté bien, dejar el código desde: 681 - 790
        # Tomar la última tabla
        ultima_tabla = contenedor_equipos[-1]
        contenedor_equipos = ultima_tabla.select('tbody tr')
    
        # Selecciona las filas de la última tabla
        # filas_ultima_tabla = ultima_tabla.select('tbody tr')
    else:
        print("NO EXISTEN REGISTROS ACTIVOS - tabla de posiciones")
        status_code = 404
        return False
        # Code to be executed if contenedor_equipos is empty
        # ...    
    
    # VALIDAR EXISTENCIA
    if len(contenedor_equipos) > 0:
        
        for equipo in contenedor_equipos:

            dict_ultimos_jugados      = {}
            logo_equipo               = None
            posicion_equipo           = None
            puntos_equipo             = 0
            partidos_ganados          = 0
            partidos_empatados        = 0
            partidos_perdidos         = 0
            cantidad_partidos_jugados = 0
            nombre_equipo             = 0
            goles_a_favor             = 0
            goles_en_contra           = 0
            diferencia_goles          = 0
            estadisticas_equipos_td   = equipo.find_all('td')
            cantidad_tds              = len(estadisticas_equipos_td)
            contador_tds              = 0
            
            while contador_tds < cantidad_tds:                

                # NOTE: Posición
                if contador_tds == 0:
                    posicion_equipo = estadisticas_equipos_td[0].text if estadisticas_equipos_td[0] is not None else ''                                

                # NOTE: Nombre y logo equipo 
                if contador_tds == 1:
                    # TODO: partido en vivo (marcador online) Table_live_game
                    logo_equipo = estadisticas_equipos_td[1].find('img') if len(estadisticas_equipos_td) > 0 else None
                    nombre_equipo = estadisticas_equipos_td[1].find('a') if len(estadisticas_equipos_td) > 0 else None
                    
                    if logo_equipo is not None:
                        logo_equipo = logo_equipo.get('src')
                    if nombre_equipo is not None:
                        nombre_equipo = nombre_equipo.text

                # NOTE: Cantidad de partidos jugados en el torneo
                if contador_tds == 2:
                    cantidad_partidos_jugados = estadisticas_equipos_td[2].text if len(estadisticas_equipos_td) > 1 else None
                    
                # NOTE: Puntos
                if contador_tds == 3:
                    puntos_equipo = estadisticas_equipos_td[3].text if len(estadisticas_equipos_td) > 2 else None
                    
                # NOTE: Partidos ganados
                if contador_tds == 4:
                    partidos_ganados = estadisticas_equipos_td[4].text if len(estadisticas_equipos_td) > 3 else None
                    
                # NOTE: Partidos empatados
                if contador_tds == 5:
                    partidos_empatados = estadisticas_equipos_td[5].text if len(estadisticas_equipos_td) > 4 else None
                    
                # NOTE: Partidos perdidos
                if contador_tds == 6:
                    partidos_perdidos = estadisticas_equipos_td[6].text if len(estadisticas_equipos_td) > 5 else None
                    
                # NOTE: Goles a favor
                if contador_tds == 7:
                    goles_a_favor = estadisticas_equipos_td[7].text if len(estadisticas_equipos_td) > 6 else None
                    
                # NOTE: Goles en contra
                if contador_tds == 8:
                    goles_en_contra = estadisticas_equipos_td[8].text if len(estadisticas_equipos_td) > 7 else None
                                    
                if contador_tds == 9:
                    diferencia_goles = estadisticas_equipos_td[9].text if len(estadisticas_equipos_td) > 8 else None

                # NOTE: Resultados últimos 5 jugaddos
                if contador_tds == 10:
                    
                    resultados_ultimos_jugados = estadisticas_equipos_td[10].select('td.forms div')
                    cantidad_resultados = len(resultados_ultimos_jugados)
                    
                    if cantidad_resultados > 0:

                        contador_resultados = 0
                        operaciones_tabla = TablaPosiciones() 
                        
                        while contador_resultados < cantidad_resultados:
                                                        
                            res_texto = resultados_ultimos_jugados[contador_resultados].text
                            res_texto = res_texto.strip()
                            res_numerico = operaciones_tabla.transcribir_partidos_jugados(
                                res_texto
                            )
                            dict_ultimos_jugados[contador_resultados] = res_numerico                            
                            contador_resultados +=1
                
                contador_tds+= 1    
            cantidad_tds = 0
            
            equipos_posicion.append({
                'nombre_equipo_full':           utilidades_global.retornar_cadena_sin_acento(nombre_equipo),
                'url_logo_equipo':              logo_equipo,
                'posicion':                     posicion_equipo,
                'partidos_jugados':             cantidad_partidos_jugados,
                'partidos_ganados':             partidos_ganados,
                'partidos_empatados':           partidos_empatados,
                'partidos_perdidos':            partidos_perdidos,
                'goles_a_favor':                goles_a_favor,
                'goles_en_contra':              goles_en_contra,
                'goles_diferencia':             diferencia_goles,
                'puntos':                       puntos_equipo,
                'resultados_ultimos_10_jugados': dict_ultimos_jugados,
            })
            
            print('nombre equipo: ', nombre_equipo, ' - ', 'posicion: ', posicion_equipo, ' - ', 'partidos jugados: ', cantidad_partidos_jugados, ' - ', 'puntos: ', puntos_equipo, ' - ', 'partidos ganados: ', partidos_ganados, ' - ', 'partidos empatados: ', partidos_empatados, ' - ', 'partidos perdidos: ', partidos_perdidos, ' - ', 'goles a favor: ', goles_a_favor, ' - ', 'goles en contra: ', goles_en_contra, ' - ', 'diferencia goles: ', diferencia_goles, ' - ', 'resultados últimos 5 jugados: ', dict_ultimos_jugados)
        
        status_code = 200

    return {
        'status_code':       status_code,
        'tabla_posiciones':  equipos_posicion,
        'path_to_scrape':    path_to_scrape,
        'exception_content': exception_content
    }
    
#TODO: TENER EN CUENTA ESTE METODO COMO SCRAPER!    
# NOTE: método funcional activo como parte del mecacnismo
@app.get('/ext-next-matches-wplay-by-league')
async def extNextMatchesWplayByLeague(path_to_scrape: str = None):
    
    matches_league_for_date = []    
    url                     = "https://apuestas.wplay.co/es/t/19160/La-Liga" # "https://apuestas.wplay.co/es/t/19297/Brasil-Serie-A"
    request_url             = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    exception_content       = None
    
    try:
        page_url_open = urlopen(request_url).read().decode('utf8')    
        soup          = BeautifulSoup(page_url_open)    
        
        # TODO: descomentar esto
        tabla = soup.find("table")
        
        if tabla is not None and len(tabla) > 0:
            print("SI EXISTEN REGISTROS ACTIVOS")
            # tabla contains some value or records
            # continue with your code here
        else:
            print("NO EXISTEN REGISTROS ACTIVOS")
            # tabla is empty or None
            # handle the case accordingly
        
        
        
        rows = tabla.find_all('tr')
            
        for row in rows:

            time_hour    = row.find_all("span", class_="time")
            time_date    = row.find_all("span", class_="date")
            equipo1      = row.select("td div > button > span > span.seln-label > span > span")
            cuota_equipo = row.select("td div > button > span .price.dec")
            # print("equipo:::::: ", equipo1[0].text, "  cuota: ", cuota_equipo[0].text, " empate.:: ", cuota_equipo[1].text)        
            # print("equipo2:::::: ", equipo1[2].text, " cupta equipo 2: ", cuota_equipo[2].text)
            
            # CREANDO POR CADA PARTIDO EL OBJECTO CON LA INFO CORRESPONDIENTE
            # TODO: pendiente validar que existan estos indices, en el mejor de los casos existen [1], [2], pero puede ser que no hayan elementos en los arraays: cuota_equipo, equipo1, etc
            match_date = {
                'time_match'         : time_hour[0].text,
                'date_match'         : time_date[0].text,
                'team_local'         : equipo1[0].text,
                'quota_team_local'   : cuota_equipo[0].text,
                'quota_tie'          : cuota_equipo[1].text,
                'team_visiting'      : equipo1[2].text,
                'quota_team_visiting': cuota_equipo[2].text
            }

            matches_league_for_date.append(match_date)

        status_code = 200
      
    except Exception as ex:    
        status_code = 500
        exception_content = ex

    return {
        'success': status_code,
        'matches_wplay': matches_league_for_date,
        'param': path_to_scrape,
        'exception': exception_content
    }
    
    