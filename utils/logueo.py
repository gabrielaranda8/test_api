from globales import app_domain
from datetime import datetime
import time
import threading

# Defino función para loguear en consola
def log_console(mensaje, tipo_log, nombre_funcion):

    # Flask levanta varios hilos para manejar muchos requests
    # No hay garantia del hilo que corre esta funcion. Es importante que separemos cada hilo y sus logs.
    thread_id = threading.get_ident()

    log = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} | {thread_id} | {tipo_log} | {app_domain} | {nombre_funcion} | {mensaje}"

    # logueo el output para poder leerlo localmente.
    print(log)