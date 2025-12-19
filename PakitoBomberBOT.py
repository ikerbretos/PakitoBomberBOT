from consolemenu import *
from consolemenu.items import *
import signal
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import time
import os
import argparse
from unidecode import unidecode
import re
from os import system
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from colorama import Fore, Style, init

init()

version = '2.3 BETA'
global debug

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help="Habilitar el modo debug")
parser.add_argument('--headless', action='store_true', help="Ejecutar en modo headless")
parser.add_argument('--start', nargs=4, metavar=('nombre', 'apellido', 'telefono', 'email'),
                    help="Iniciar el programa con datos: nombre apellido telefono email")
# Leer los argumentos
args = parser.parse_args()
debug = int(args.debug)
headless = int(args.headless)

if os.name == 'nt':
    system("title " 'PakitoBomberBOT v'+version)
else:
    system("echo -e '\033]2;PakitoBomberBOT v"+version+"\007'")

global pakito_header
pakito_header = Fore.GREEN + Style.BRIGHT + r"""
  ___  _   _  _ ___ _____ ___
 | _ \/_\ | |/ |_ _|_   _/ _ \
 |  _/ _ \| ' < | |  | || (_) |
 |_|/_/ \_\_|\_\___| |_| \___/
  ___  ___  __  __ ___ ___ ___
 | _ )/ _ \|  \/  | _ ) __| _ \
 | _ \ (_) | |\/| | _ \ _||   /
 |___/\___/|_|  |_|___/___|_|_\

             B O T
""" + Style.RESET_ALL

def check_version():
    return ""

def setup_browser():
    global binary, profile, PATH_TO_DEV_NULL
    global browser

    if os.name == 'nt':  # Windows
        firefox_binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        PATH_TO_DEV_NULL = 'nul'
    elif os.uname().sysname == 'Darwin':  # macOS
        firefox_binary = '/Applications/Firefox.app/Contents/MacOS/firefox'
        PATH_TO_DEV_NULL = '/dev/null'
    else:
        firefox_binary = '/usr/bin/firefox'
        PATH_TO_DEV_NULL = '/dev/null'

    # Comprobar si Firefox está instalado
    if os.path.exists(firefox_binary):
        PATH_TO_DEV_NULL = 'nul' if os.name == 'nt' else '/dev/null'
        profile = webdriver.FirefoxProfile()
        profile.set_preference("media.autoplay.default", 0)
        profile.accept_untrusted_certs = True
        profile.set_preference("media.volume_scale", "0.0")
        profile.set_preference("dom.webnotifications.enabled", False)

        # Use webdriver_manager to get geckodriver
        try:
            geckodriver_path = GeckoDriverManager().install()
        except Exception as e:
            print(f"Error installing geckodriver: {e}")
            geckodriver_path = './geckodriver' # Fallback

        firefox_service = FirefoxService(geckodriver_path)

        if headless:
            options = webdriver.FirefoxOptions()
            options.headless = True
            browser = webdriver.Firefox(firefox_binary=firefox_binary, service=firefox_service, firefox_profile=profile, service_log_path=PATH_TO_DEV_NULL, options=options)
        else:
            browser = webdriver.Firefox(firefox_binary=firefox_binary, service=firefox_service, firefox_profile=profile, service_log_path=PATH_TO_DEV_NULL)
    
    # Configurar para Chrome si Firefox no está disponible
    else: 
        print("Firefox no está instalado, usando Chrome...")
        chrome_service = ChromeService(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--silent')
        browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

#Limpiar Consola
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

#Formulario Datos
def pregunta_estilizada(prompt, datos_previos='', email='', validacion=None):
    clear_console()
    print(pakito_header)
    # Imprimir los datos previos antes de hacer la nueva pregunta
    if datos_previos:
        print(datos_previos)
    
    while True:
        try:
            respuesta = input(Fore.GREEN + Style.BRIGHT + prompt + Style.RESET_ALL)
            # Si se proporciona una función de validación y la respuesta es válida, romper el bucle
            if not validacion or validacion(respuesta):
                break
            else:
                print(Fore.RED + "Entrada inválida, por favor intente de nuevo." + Style.RESET_ALL)
        except EOFError:
            clear_console()
            exit(0)
    
    # Agregar el correo electrónico a datos_previos si se proporciona
    if email:
        datos_previos += Fore.WHITE + Style.BRIGHT + f"Correo: {email}\n" + Style.RESET_ALL
    
    return respuesta

def validacion_no_vacia(input_str):
    return input_str.strip() != ''

#Formulario
def formulario():
    global email 
    prefijos = ('6', '7', '9')
    if debug == 1:
        print(pakito_header)
        print('MODO DEBUG ACTIVADO')
        global number, name, surname, email
        number, name, surname, email = '666666666', 'NombrePrueba', 'ApellidoPrueba', 'CorreoPrueba@gmail.com'
    else:
        def normalizar_cadena(cadena):
            # Quitar tildes y caracteres especiales
            cadena = unidecode(cadena)
            # Eliminar cualquier carácter que no sea alfanumérico
            cadena = re.sub(r'[^a-zA-Z0-9]', '', cadena)
            return cadena

        datos_persona = ''
        number = pregunta_estilizada('[+] TELÉFONO OBJETIVO: ')
        while len(number) != 9 or not number.isdigit() or number[0] not in prefijos:
            number = pregunta_estilizada('[!] NÚMERO INVÁLIDO. REINTENTE TELÉFONO: ')
        datos_persona += Fore.WHITE + Style.BRIGHT + f"Nº de Teléfono: {number}\n" + Style.RESET_ALL

        name = pregunta_estilizada('[+] NOMBRE OBJETIVO: ', datos_previos=datos_persona, validacion=validacion_no_vacia)
        surname = pregunta_estilizada('[+] APELLIDOS OBJETIVO: ', datos_previos=datos_persona, validacion=validacion_no_vacia)
        nombre_completo = Fore.WHITE + Style.BRIGHT + f"Nombre: {name} {surname}\n" + Style.RESET_ALL
        datos_persona += nombre_completo

        # Normalizar el nombre y apellido
        name = normalizar_cadena(name.lower())
        surname = normalizar_cadena(surname.lower())

        email = pregunta_estilizada('[+] EMAIL OBJETIVO (Dejar en blanco para auto-generar): ', datos_persona)
        if not email:
            email = f'{name}.{surname}@gmail.com'
        datos_persona += Fore.WHITE + Style.BRIGHT + f"Correo: {email}\n" + Style.RESET_ALL

    # Después de recopilar toda la información, puedes mostrar datos_persona
    clear_console()
    print(pakito_header)
    if debug == 0:
        print(datos_persona)
    else:
        print('MODO DEBUG ACTIVADO')

interrupted = False

def handle_interrupt(browser):
    global interrupted
    interrupted = True
    browser.quit()
    print("Navegador cerrado. Volviendo al menú principal...")

def main():
    #Limite hora
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    start = '10:40:00'
    end = '22:00:00'

    if args.start or debug:
        repeat = 0
    else:
        repeat = input('Modo repetición [S/N]: ').lower()
        if repeat in ('y', 'yes', 's', 'si'):
            repeat = 1
        
    global interrupted
    while not interrupted:
        setup_browser()
        #SECURITAS DIRECT
        try:
            browser.get('https://www.securitasdirect.es/')
            time.sleep(5) #Cookies
            try:
                browser.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()
                time.sleep(1)
            except:
                pass
            browser.find_element(By.XPATH, '//*[@id="edit-telefono1"]').send_keys(number)
            browser.find_element(By.XPATH, '//*[@id="edit-submit"]').click()
            time.sleep(1)
            if(browser.current_url == 'https://www.securitasdirect.es/error-envio'):
                print('Securitas Direct: Skipeado (Limite Excedido)')
            else:
                print('Securitas Direct: OK')
        except Exception as e:
            print(f'Securitas Direct: Skipeado (ERROR: {e})')

        #euroinnova
        try:
            browser.get('https://www.euroinnova.com/')
            time.sleep(3)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="accept-cookies"]').click()
                time.sleep(2)
            except:
                pass
            
            try:
                # Click "Solicitar información" button to open modal
                browser.find_element(By.XPATH, "//button[contains(text(),'Solicitar información')]").click()
                time.sleep(2)
            except:
                pass

            browser.find_element(By.ID, 'name').send_keys(name)
            browser.find_element(By.ID, 'mail').send_keys(email)
            browser.find_element(By.ID, 'tel').send_keys(number)
            
            # JS Click for privacy and submit
            browser.execute_script("document.getElementById('privacidad').click();")
            time.sleep(1)
            browser.execute_script("document.getElementById('btn_enviar').click();")
            
            time.sleep(3)
            print('Euroinnova: OK')
        except Exception as e:
            print(f'Euroinnova: Skipeado (ERROR: {e})')

        #GENESIS
        try:
            if current_time > start and current_time < end:
                browser.get('https://www.genesis.es/modal/c2c')
                time.sleep(3)
                try: #Cookies

                    browser.execute_script("document.querySelector('#onetrust-accept-btn-handler').click();")
                except:
                    pass
                time.sleep(1)
                
                # Use JS to select option and interact with inputs to avoid interception
                try:
                    select = browser.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div/div/article/div/div/div/div/div/form/section/div/div[2]/div/select/option[2]')
                    browser.execute_script("arguments[0].selected = true; arguments[0].click();", select)
                except:
                    pass

                name_input = browser.find_element(By.XPATH, '//*[@id="edit-por-quien-preguntamos-"]')
                browser.execute_script("arguments[0].value = arguments[1];", name_input, name)
                
                phone_input = browser.find_element(By.XPATH, '//*[@id="edit-phone"]')
                browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
                
                phone_conf = browser.find_element(By.XPATH, '//*[@id="edit-phone-confirmation"]')
                browser.execute_script("arguments[0].value = arguments[1];", phone_conf, number)

                submit_btn = browser.find_element(By.XPATH, '//*[@id="edit-actions-submit"]')
                browser.execute_script("arguments[0].click();", submit_btn)
                time.sleep(3)
                print('Genesis: OK')
            else:
                print('Genesis: Skipeado (Fuera de Horario)')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Genesis: Skipeado (ERROR: {e})')

        #RACCTEL+
        try:
            browser.get('https://www.racctelplus.cat/es')
            time.sleep(3)
            try: #Cookies
                cookie_btn = browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                browser.execute_script("arguments[0].click();", cookie_btn)
                time.sleep(1)
            except:
                pass
            time.sleep(2)
            
            phone_input = browser.find_element(By.XPATH, "//input[@id='phone']")
            browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
            
            submit_btn = browser.find_element(By.XPATH, "//button[@id='c2c-submit']")
            browser.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)
            print('Racctel+ OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Racctel+ Skipeado: (ERROR: {e})')





        #spamovil
        try:
            browser.get('https://spamovil.es/te-llamamos-gratis/')
            time.sleep(1)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()
                time.sleep(2)
            except:
                pass
            browser.find_element(By.XPATH, '/html/body/div[1]/div/div/article/div/div/div/div[2]/div[2]/div/form/p[1]/label/span/input').send_keys(name)
            browser.find_element(By.XPATH, '/html/body/div[1]/div/div/article/div/div/div/div[2]/div[2]/div/form/p[2]/label/span/input').send_keys(number)
            browser.find_element(By.XPATH, '/html/body/div[1]/div/div/article/div/div/div/div[2]/div[2]/div/form/p[3]/label/span/span/span/input').click()
            browser.find_element(By.XPATH, '/html/body/div[1]/div/div/article/div/div/div/div[2]/div[2]/div/form/p[4]/input').click()
            time.sleep(5)
            print('spamovil: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'spamovil: Skipeado (ERROR: {e})')

        #Vodafone
        try:
            browser.get('https://www.vodafone.es/c/empresas/es/marketing-online/')
            time.sleep(3)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(2)
            except:
                pass
            
            # Click "Autónomos (1-4 empleados)" link to reveal form
            try:
                browser.find_element(By.XPATH, "//a[contains(text(),'Autónomos (1-4 empleados)')]").click()
                time.sleep(2)
            except:
                pass

            phone_input = browser.find_element(By.XPATH, "//input[@id='phone']")
            browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
            
            checkbox_gdpr = browser.find_element(By.XPATH, "//input[@id='cmb-gdpr']")
            browser.execute_script("arguments[0].click();", checkbox_gdpr)
            
            checkbox_commercial = browser.find_element(By.XPATH, "//input[@id='cmb-check']")
            browser.execute_script("arguments[0].click();", checkbox_commercial)
            
            time.sleep(1)
            time.sleep(1)
            submit_btn = browser.find_element(By.XPATH, "//input[@data-vfms-js='cmb-submit']")
            browser.execute_script("arguments[0].click();", submit_btn)
            time.sleep(4)
            print('Vodafone: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Vodafone: Skipeado (ERROR: {e})')

        #Euskaltel
        try:
            browser.get('https://www.euskaltel.com/?idioma=esp')
            time.sleep(3)
            try: #Cookies
                cookie_btn = browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                browser.execute_script("arguments[0].click();", cookie_btn)
                time.sleep(1)
            except:
                pass
            time.sleep(2)
            
            phone_input = browser.find_element(By.XPATH, "//input[@id='phone']")
            browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
            
            submit_btn = browser.find_element(By.XPATH, "//button[@id='c2c-submit']")
            browser.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)
            print('Euskaltel OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Euskaltel Skipeado: (ERROR: {e})')

        #Pelayo
        try:
            browser.get('https://www.pelayo.com/nosotros_te_llamamos/tellamamos')
            time.sleep(2)
            try: #Cookies
                browser.find_element(By.XPATH, '/html/body/app-root/app-cookies-block/div[2]/div/div/a[1]').click()
                time.sleep(3)
            except:
                pass
            time.sleep(1)
            browser.find_element(By.XPATH, '//*[@id="input3"]').send_keys(number)
            browser.find_element(By.XPATH, '/html/body/app-root/div/app-layout-click-to-call/main/div/div/app-ad-elem/app-panel-window-te-llamamos/form/div[2]/button').click()
            time.sleep(3)
            print('Pelayo OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Pelayo Skipeado: (ERROR: {e})')

        #Movistar
        try:
            browser.get('https://www.movistar.es/estaticos/html/modal/modal-formulario-C2C-empresas-inside-sales-new.html')
            time.sleep(1)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(1)
            except:
                pass
            time.sleep(1)
            browser.find_element(By.XPATH, '//*[@id="nameC2CplainModal_IS"]').send_keys(name)
            browser.find_element(By.XPATH, '//*[@id="tlfC2CplainModal_IS"]').send_keys(number)
            time.sleep(1)
            browser.find_element(By.XPATH, '//*[@id="cifC2CplainModal_IS"]').send_keys('D09818238')
            browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div/form/div[1]/div[4]/select/option[33]').click()
            browser.find_element(By.XPATH, '//*[@id="modal__emp__cta"]').click()
            time.sleep(2)
            print('Movistar OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Movistar Skipeado: (ERROR: {e})')

        #SantaLucia
        try:
            browser.get('https://www.santalucia.es/')
            time.sleep(5)
            try: #Cookies
                # Try multiple cookie selectors
                cookie_btn = browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                browser.execute_script("arguments[0].click();", cookie_btn)
                time.sleep(2)
            except:
                pass
            
            # Remove cookie overlay if still present
            try:
                browser.execute_script("var element = document.querySelector('.onetrust-pc-dark-filter'); if(element) { element.parentNode.removeChild(element); }")
            except:
                pass

            # Phone input
            phone_input = browser.find_element(By.XPATH, "//input[@type='tel']")
            browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
            
            # Checkbox
            try:
                check = browser.find_element(By.XPATH, "//input[@type='checkbox']")
                browser.execute_script("arguments[0].click();", check)
            except:
                pass

            # Submit button with JS to avoid interception
            submit_btn = browser.find_element(By.XPATH, "//button[contains(., 'Recibir llamada')]")
            browser.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)
            print('SantaLucia: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'SantaLucia: Skipeado (ERROR: {e})')







        #Prosegur
        try:
            browser.get('https://www.prosegur.es/')
            time.sleep(5)
            try: #Cookies
                cookie_btn = browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                browser.execute_script("arguments[0].click();", cookie_btn)
                time.sleep(1)
            except:
                pass
            
            # Open Modal
            try:
                # Try to find the "Contratar" or "Calcular" button that opens the modal
                modal_btn = browser.find_element(By.XPATH, "//button[contains(., 'Contratar') or contains(., 'Calcular')] | //a[contains(., 'Contratar') or contains(., 'Calcular')]")
                browser.execute_script("arguments[0].click();", modal_btn)
                time.sleep(2)
            except:
                pass

            # Phone input in modal
            phone_input = browser.find_element(By.XPATH, "//input[@placeholder='Tu teléfono ']")
            browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
            
            # Privacy checkbox
            try:
                check = browser.find_element(By.XPATH, "//input[@type='checkbox'][@required or @aria-required='true']")
                browser.execute_script("arguments[0].click();", check)
            except:
                pass

            # Submit button in modal
            submit_btn = browser.find_element(By.XPATH, "//button[contains(., 'Contratar ahora')]")
            browser.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)
            print('Prosegur: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Prosegur: Skipeado (ERROR: {e})')

        #LineaDirecta
        try:
            browser.get('https://www.lineadirecta.com/te-llamamos-gratis.html')
            time.sleep(5)
            try: #Cookies
                # Try Didomi and OneTrust
                try:
                    cookie_btn = browser.find_element(By.XPATH, "//*[@id='didomi-notice-agree-button']")
                    browser.execute_script("arguments[0].click();", cookie_btn)
                except:
                    cookie_btn = browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                    browser.execute_script("arguments[0].click();", cookie_btn)
                time.sleep(1)
            except:
                pass
            
            phone = browser.find_element(By.XPATH, '//*[@id="telefono"]')
            browser.execute_script("arguments[0].value = arguments[1];", phone, number)
            
            # Try multiple selectors for the button
            btn = None
            selectors = [
                '//*[@id="btn1"]',
                '//*[@id="btn-llamar"]',
                "//button[contains(., 'Llamadme')]",
                "//a[contains(., 'Quiero que me llamen')]"
            ]
            
            for selector in selectors:
                try:
                    btn = browser.find_element(By.XPATH, selector)
                    if btn:
                        break
                except:
                    continue
            
            if btn:
                browser.execute_script("arguments[0].click();", btn)
                time.sleep(3)
                print('LineaDirecta: OK')
            else:
                print('LineaDirecta: Skipeado (ERROR: Button not found)')

        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'LineaDirecta: Skipeado (ERROR: {e})')

        #Telecable
        try:
            browser.get('https://telecable.es/')
            time.sleep(5)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(1)
            except:
                pass
            
            phone_input = browser.find_element(By.XPATH, "//input[@name='phone' or @type='tel' or contains(@id, 'phone')]")
            phone_input.send_keys(number)
            
            browser.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Llamadme')]").click()
            time.sleep(3)
            print('Telecable: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Telecable: Skipeado (ERROR: {e})')









        #iSalud
        try:
            browser.get('https://asisa.isalud.com/llama-gratis')
            time.sleep(4)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(1)
            except:
                pass
            time.sleep(2)
            browser.find_element(By.XPATH, '//*[@id="name"]').send_keys(name)
            browser.find_element(By.XPATH, '//*[@id="phone"]').send_keys(number)
            browser.find_element(By.XPATH, '//*[@id="email"]').send_keys(email)
            browser.find_element(By.XPATH, '/html/body/div[1]/section[1]/div[2]/form/div/div[5]/div/a').click()
            browser.find_element(By.XPATH, '//*[@id="contact_freecall"]').click()
            time.sleep(3)
            print('iSalud: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'iSalud: Skipeado (ERROR: {e})')

        #iSalud2
        try:
            payload = {'name': name, 'surname': surname, 'email': email, 'number': number}
            requests.post('https://vsec.es/llamada.php', data=payload)
        except:
            pass

        #Recordador
        try:
            payload = {'phoneNumber': '34'+number}
            files=[]
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': '*/*',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://recordador.com/',
            'Origin': 'https://recordador.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=0',
            'Cookie': 'ci_connect_pabbly_sesion=deehc3mngn2kmr42jkt5aotfcdmab2f1'}
            response = requests.request("POST", 'https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTY5MDYzNTA0M2M1MjZmNTUzNTUxMzci_pc', headers=headers, data=payload, files=files)
            if response.status_code == 200:
                print('Recordador: OK')
        except Exception as e:
            print(f'Recordador (ERROR: {e})')
    
        #proyectosyseguros
        try:
            browser.get('https://www.proyectosyseguros.com/te-llamamos/')
            time.sleep(3)
            browser.find_element(By.XPATH, '//*[@id="Nombre"]').send_keys(name)
            browser.find_element(By.XPATH, '//*[@id="Email"]').send_keys(email)
            browser.find_element(By.XPATH, '//*[@id="Telefono"]').send_keys(number)
            option = browser.find_element(By.XPATH, '/html/body/div[3]/main/div/div/div/div/div/form/div[3]/div/div[1]/select/option[2]')
            browser.execute_script("arguments[0].click();", option)
            
            check = browser.find_element(By.XPATH, '//*[@id="acepto_condiciones"]')
            browser.execute_script("arguments[0].click();", check)
            
            btn = browser.find_element(By.XPATH, '/html/body/div[3]/main/div/div/div/div/div/form/div[6]/button/span[1]')
            browser.execute_script("arguments[0].click();", btn)
            time.sleep(3)
            print('Proyectos y Seguros: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Proyectos y Seguros: Skipeado (ERROR: {e})')

        #MoneyGO
        try:
            browser.get('https://ctc.moneygo.es/money-go-ctc-web/ctc/04f25d44-f1ce-4554-ba40-57211f7133ce')
            time.sleep(3)
            browser.find_element(By.XPATH, '//*[@id="telefono"]').send_keys(number)
            browser.find_element(By.XPATH, '/html/body/div[1]/create-ctc/div[2]/form/div[4]/div/label').click()
            browser.find_element(By.XPATH, '/html/body/div[1]/create-ctc/div[2]/form/button').click()
            time.sleep(3)
            print('MoneyGO: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'MoneyGO: Skipeado (ERROR: {e})')

        #emagister
        try:
            browser.get('https://www.emagister.com/')
            time.sleep(2)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(1)
            except:
                pass
            btn_open = browser.find_element(By.XPATH, '/html/body/header/div[2]/div/div[3]/div/nav/div[1]/div/div/section[2]/button')
            browser.execute_script("arguments[0].click();", btn_open)
            time.sleep(1)
            browser.find_element(By.XPATH, '//*[@id="callMe-phone"]').send_keys(number)
            
            check = browser.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td[2]/div/div[2]/form/p/label/span[2]')
            browser.execute_script("arguments[0].click();", check)
            
            btn_send = browser.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td[2]/div/div[2]/form/button')
            browser.execute_script("arguments[0].click();", btn_send)
            time.sleep(3)
            print('emagister: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'emagister: Skipeado (ERROR: {e})')

        #Mundo-R
        try:
            browser.get('https://mundo-r.com/es')
            time.sleep(3)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(1)
            except:
                pass
            time.sleep(2)
            phone = browser.find_element(By.XPATH, '//*[@id="phone"]')
            browser.execute_script("arguments[0].value = arguments[1];", phone, number)
            
            btn = browser.find_element(By.XPATH, '//*[@id="c2c-submit"]')
            browser.execute_script("arguments[0].click();", btn)
            time.sleep(3)
            print('Mundo-R OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Mundo-R Skipeado: (ERROR: {e})')

        #homeserve
        try:
            browser.get('https://www.homeserve.es/servicios-reparaciones/fontaneros')
            time.sleep(3)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="basicCookies"]/div/div[2]/div[3]/div/button').click()
            except:
                pass
            time.sleep(1)
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[2]/select/option[2]').click()
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[5]/input[1]').send_keys(name)
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[5]/input[2]').send_keys(surname)
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[6]/input[1]').send_keys(number)
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[6]/input[2]').send_keys(email)
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[7]/input').click()
            browser.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/div[2]/div[1]/div[1]/form/div[9]/button').click()
            time.sleep(1)
            print('homeserve: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'homeserve: Skipeado (ERROR: {e})')

        #clinicaboccio
        try:
            browser.get('https://www.clinicaboccio.com/pide-cita/')
            time.sleep(3)
            try: #Cokies
                browser.find_element(By.XPATH, '//*[@id="cmplz-cookiebanner-container"]/div/div[6]/button[1]').click()
            except:
                pass
            name_input = browser.find_element(By.XPATH, '//*[@id="input_5_1"]')
            browser.execute_script("arguments[0].value = arguments[1];", name_input, name)
            
            phone_input = browser.find_element(By.XPATH, '//*[@id="input_5_4"]')
            browser.execute_script("arguments[0].value = arguments[1];", phone_input, number)
            
            browser.execute_script("window.scrollBy(0, 600);")
            time.sleep(3)
            
            check = browser.find_element(By.XPATH, '//*[@id="input_5_5_1"]')
            browser.execute_script("arguments[0].click();", check)
            
            btn = browser.find_element(By.XPATH, '//*[@id="gform_submit_button_5"]')
            browser.execute_script("arguments[0].click();", btn)
            time.sleep(2)
            print('Clinica Boccio: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Clinica Boccio: Skipeado (ERROR: {e})')

        #MasMovil
        try:
            browser.get('https://www.masmovil.es/')
            time.sleep(3)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                time.sleep(2)
            except:
                pass
            
            # Click c2c control
            try:
                browser.find_element(By.ID, "c2c-control").click()
                time.sleep(2)
            except:
                pass

            browser.find_element(By.XPATH, "//input[contains(@id, 'CMPhoneBySideData_')]").send_keys(number)
            browser.find_element(By.XPATH, "//input[contains(@id, 'CMCallBtnBySideData_')]").click()
            time.sleep(3)
            print('MasMovil: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'MasMovil: Skipeado (ERROR: {e})')

        #ElPaso2000
        try:
            browser.get('https://www.elpaso2000.com/te-llamamos/')
            time.sleep(1)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()
                time.sleep(2)
            except:
                pass
            browser.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div[1]/div[1]/div[1]/div[2]/form/div[1]/input').send_keys(number)
            
            check = browser.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div[1]/div[1]/div[1]/div[2]/form/label/span')
            browser.execute_script("arguments[0].click();", check)
            
            time.sleep(1)
            btn = browser.find_element(By.XPATH, '/html/body/div/div[1]/div/main/div/div[1]/div[1]/div[1]/div[2]/form/div[3]/button/span')
            browser.execute_script("arguments[0].click();", btn)
            time.sleep(2)
            print('ElPaso2000: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'ElPaso2000: Skipeado (ERROR: {e})')



        #centrodermatologicoestetico
        try:
            browser.get('https://www.centrodermatologicoestetico.com/te-llamamos/')
            time.sleep(3)
            try: #Cookies
                browser.find_element(By.XPATH, '//*[@id="cookie_action_close_header"]').click()
                time.sleep(2)
            except:
                pass
            browser.find_element(By.XPATH, '/html/body/main/div/div[1]/section/div[2]/div[1]/div/div[4]/div/form/input[5]').send_keys(name)
            browser.find_element(By.XPATH, '//*[@id="international_PhoneNumber_countrycode"]').send_keys(number)
            browser.find_element(By.XPATH, '/html/body/main/div/div[1]/section/div[2]/div[1]/div/div[4]/div/form/input[7]').send_keys(email)
            
            check = browser.find_element(By.XPATH, '/html/body/main/div/div[1]/section/div[2]/div[1]/div/div[4]/div/form/div/div/div/input')
            browser.execute_script("arguments[0].click();", check)
            
            btn = browser.find_element(By.XPATH, '/html/body/main/div/div[1]/section/div[2]/div[1]/div/div[4]/div/form/button')
            browser.execute_script("arguments[0].click();", btn)
            time.sleep(2)
            print('centrodermatologicoestetico: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'centrodermatologicoestetico: Skipeado (ERROR: {e})')








        

        #regal
        try:
            browser.get('https://te-llamamos.regal.es/user-details')
            time.sleep(3)
            browser.find_element(By.XPATH, '(//*[@id="primaryPhoneInput"])[1]').send_keys(number)
            browser.find_element(By.XPATH, '(//*[@id="primaryPhoneInput"])[2]').send_keys(number)
            btn = browser.find_element(By.XPATH, '//*[@id="continueButton"]')
            browser.execute_script("arguments[0].click();", btn)
            time.sleep(2)
            print('Regal: OK')
        except KeyboardInterrupt:
            browser.close()
            quit()
        except Exception as e:
            print(f'Regal: Skipeado (ERROR: {e})')









        if repeat == 1:
            browser.close()
            print('Repeat ON')
        else:
            if args.start:
                try:
                    browser.close()
                except:
                    pass
                sys.exit()
            else:
                browser.quit()
                break

# Menu
def modo_automatico():
    print(Fore.GREEN + '[*] INICIALIZANDO ATAQUE AUTOMÁTICO...' + Style.RESET_ALL)
    time.sleep(0.5)
    formulario()
    main()

def menu_principal():
    while True:
        clear_console()
        print(pakito_header)
        print(Fore.GREEN + "SISTEMA LISTO - SELECCIONE OPERACIÓN" + Style.RESET_ALL)
        print(Fore.GREEN + "[1] EJECUTAR ATAQUE AUTOMÁTICO" + Style.RESET_ALL)
        print(Fore.GREEN + "[0] SALIR" + Style.RESET_ALL)
        
        try:
            opcion = input(Fore.GREEN + Style.BRIGHT + "Seleccione una opción: " + Style.RESET_ALL)
            if opcion == '1':
                modo_automatico()
            elif opcion == '0':
                sys.exit()
        except EOFError:
            sys.exit()
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: handle_interrupt(browser))
    if args.start:
        global number, name, surname, email
        name, surname, number, email = args.start
        main()
    elif debug:
        modo_automatico()
    else:
        menu_principal()
