import os
from flask import Flask, request, abort
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import sqlite3

from globales import api_name, PORT
from utils.data_base import get_db, init_db
from utils.logueo import log_console
from datetime import datetime

# Ruta para la documentación Swagger
SWAGGER_ROUTE = '/api/docs'
API_ROUTE_FILE = '/static/swagger.yaml'

# Generar una clave secreta
SECRET_KEY = os.urandom(24)

# Configurar la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Configurar Swagger UI
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_ROUTE,
    API_ROUTE_FILE,
    config={
        'app_name': api_name
    }
)

# Iniciar la base de datos
init_db()

class Character(Resource):
    def get(self, character_id=None):
        """
        Obtener información de un personaje o de todos los personajes.

        :param character_id: ID del personaje (opcional)
        :return: Información del personaje o de todos los personajes en formato JSON.
        """

        function_name = "Character_get"

        tiempo_inicial = datetime.now()
        log_console("Iniciando API", "INFO", function_name)

        db = get_db()
        cursor = db.cursor()

        # Configurar el tipo de fila del cursor como un diccionario
        cursor.row_factory = sqlite3.Row

        if character_id is None:
            # Consultar todos los personajes
            log_console("Procedemos a buscar todos los Personajes", 'INFO', function_name)
            cursor.execute("SELECT id, name, height, mass, birth_year, eye_color FROM Character")
            characters = cursor.fetchall()
            response = [{'id': row['id'], 'name': row['name'], 'height': row['height'], 'mass': row['mass'], 'birth_year': row['birth_year'], 'eye_color': row['eye_color']} for row in characters]
        else:
            # Consultar un personaje por su ID
            log_console(f"Procedemos a buscar el personaje con id: {character_id}", 'INFO', function_name)
            cursor.execute("SELECT * FROM Character WHERE id = ?", (character_id,))
            character = cursor.fetchone()
            if character:
                log_console(f"Personaje encontrado con exito para el id: {character_id}", 'INFO', function_name)
                response = {'id': character['id'], 'name': character['name'], 'height': character['height'], 'mass': character['mass'], 'birth_year': character['birth_year'], 'eye_color': character['eye_color']}
            else:
                log_console(f"El Personaje NO fue encontrado para el id: {character_id}", 'INFO', function_name)
                response = {'message': 'Character not found'}

        tiempo_final = datetime.now()
        log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}", 'INFO', function_name)
        db.close()
        return response

    def post(self):
        """
        Agregar un nuevo personaje a la base de datos.

        :return: Datos del nuevo personaje agregado en formato JSON.
        """

        function_name = "Character_post"

        tiempo_inicial = datetime.now()
        log_console("Iniciando API", "INFO", function_name)

        data = request.json
        if not all(key in data for key in ('id', 'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year')):
            log_console("Algunas de las key enviadas no son correctas o han sido omitidas", 'INFO', function_name)
            tiempo_final = datetime.now()
            log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 400", 'ERROR', function_name)
            abort(400, "Missing fields")
        if any(data[key] is None for key in data):
            log_console("Algunas de las key enviadas son nulas", 'INFO', function_name)
            tiempo_final = datetime.now()
            log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 400", 'ERROR', function_name)
            abort(400, "Fields cannot be null")
        try:
            int(data['id'])
            int(data['height'])
            int(data['mass'])
        except ValueError:
            log_console("Algunas de las key no respetan la estructura", 'INFO', function_name)
            tiempo_final = datetime.now()
            log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 400", 'ERROR', function_name)
            abort(400, "ID, Height, and Mass must be integers")
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM Character WHERE id = ?", (data['id'],))
        existing_character = cursor.fetchone()
        if existing_character:
            log_console("Ya existe un personaje con ese ID", 'INFO', function_name)
            tiempo_final = datetime.now()
            log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 400", 'ERROR', function_name)
            abort(400, "Character with id {} already exists".format(data['id']))
        
        log_console("Procedemos a guardar el personaje", 'INFO', function_name)
        character_values = (data['id'], data['name'], data['height'], data['mass'], data['hair_color'], data['skin_color'], data['eye_color'], data['birth_year'])
        cursor.execute("INSERT INTO Character (id, name, height, mass, hair_color, skin_color, eye_color, birth_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", character_values)
        db.commit()
        db.close()

        tiempo_final = datetime.now()
        log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 201", 'INFO', function_name)
        return data, 201

    def delete(self, character_id):
        """
        Eliminar un personaje de la base de datos.

        :param character_id: ID del personaje a eliminar.
        :return: Mensaje de confirmación en formato JSON si se eliminó correctamente, de lo contrario, un mensaje de error.
        """

        function_name = "Character_delete"

        tiempo_inicial = datetime.now()
        log_console("Iniciando API", "INFO", function_name)

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM Character WHERE id = ?", (character_id,))
        character = cursor.fetchone()
        if character:
            log_console("Procedemos a eliminar el personaje", 'INFO', function_name)
            cursor.execute("DELETE FROM Character WHERE id = ?", (character_id,))
            db.commit()
            db.close()
            tiempo_final = datetime.now()
            log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 200", 'INFO', function_name)
            return {'message': 'Character deleted'}, 200
        else:
            log_console("No encontramos personaje", 'INFO', function_name)
            db.close()
            tiempo_final = datetime.now()
            log_console(f"Fin de request, duracion de la funcion: {(tiempo_final - tiempo_inicial).total_seconds()}, response 400", 'ERROR', function_name)
            abort(400, "Character not found")

# Proceso principal de Flask, aquí creamos y configuramos la aplicación
api = Api(app)
api.add_resource(Character, '/character/getAll', endpoint='get_all_characters')
api.add_resource(Character, '/character/get/<int:character_id>', endpoint='get_character_by_id')
api.add_resource(Character, '/character/add', endpoint='add_character')
api.add_resource(Character, '/character/delete/<int:character_id>', endpoint='delete_character')

# Registrar la documentación Swagger
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_ROUTE)

# Ruta para servir el archivo YAML de Swagger
@app.route('/static/swagger.yaml')
def swagger_file():
    with open('static/swagger.yaml', 'r') as f:
        return f.read()

# Ejecutar la aplicación Flask
app.run(host='0.0.0.0', port=PORT, threaded=True)