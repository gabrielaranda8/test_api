import os
from flask import Flask, request, g, jsonify, abort
from flask_restful import Api, Resource
from flask_wtf.csrf import CSRFProtect
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

from globales import api_name, PORT
from utils.logueo import log_console
from utils.data_base import get_db, init_db
import sqlite3

SWAGGER_ROUTE = '/api/docs'
API_ROUTE_FILE = '/static/swagger.yaml'

# Generar una clave secreta
SECRET_KEY = os.urandom(24)

# Configurar la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_ROUTE,
    API_ROUTE_FILE,
    config={
        'app_name': api_name
    }
)

# Iniciamos la base
init_db()

class Character(Resource):
    def get(self, character_id=None):
        db = get_db()
        cursor = db.cursor()
        
        # Configurar el tipo de fila del cursor como un diccionario
        cursor.row_factory = sqlite3.Row

        if character_id is None:
            # Consultar todos los personajes
            cursor.execute("SELECT id, name, height, mass, birth_year, eye_color FROM Character")
            characters = cursor.fetchall()
            response = [{'id': row['id'], 'name': row['name'], 'height': row['height'], 'mass': row['mass'], 'birth_year': row['birth_year'], 'eye_color': row['eye_color']} for row in characters]
        else:
            # Consultar un personaje por su ID
            cursor.execute("SELECT * FROM Character WHERE id = ?", (character_id,))
            character = cursor.fetchone()
            if character:
                response = {'id': character['id'], 'name': character['name'], 'height': character['height'], 'mass': character['mass'], 'birth_year': character['birth_year'], 'eye_color': character['eye_color']}
            else:
                response = {'message': 'Character not found'}

        db.close()
        return response

    def post(self):
        data = request.json
        if not all(key in data for key in ('id', 'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year')):
            abort(400, "Missing fields")
        if any(data[key] is None for key in data):
            abort(400, "Fields cannot be null")
        try:
            int(data['id'])
            int(data['height'])
            int(data['mass'])
        except ValueError:
            abort(400, "ID, Height, and Mass must be integers")
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM Character WHERE id = ?", (data['id'],))
        existing_character = cursor.fetchone()
        if existing_character:
            abort(400, "Character with id {} already exists".format(data['id']))
        
        character_values = (data['id'], data['name'], data['height'], data['mass'], data['hair_color'], data['skin_color'], data['eye_color'], data['birth_year'])
        cursor.execute("INSERT INTO Character (id, name, height, mass, hair_color, skin_color, eye_color, birth_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", character_values)
        db.commit()
        db.close()

        return data, 201

    def delete(self, character_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM Character WHERE id = ?", (character_id,))
        character = cursor.fetchone()
        if character:
            cursor.execute("DELETE FROM Character WHERE id = ?", (character_id,))
            db.commit()
            db.close()
            return {'message': 'Character deleted'}, 200
        else:
            db.close()
            abort(400, "Character not found")

        db.commit()
        db.close()

        return {'message': 'Character deleted'}, 200

# Proceso principal de Flask, aca creamos y configuramos la app
api = Api(app)
api.add_resource(Character, '/character/getAll', endpoint='get_all_characters')
api.add_resource(Character, '/character/get/<int:character_id>', endpoint='get_character_by_id')
api.add_resource(Character, '/character/add', endpoint='add_character')
api.add_resource(Character, '/character/delete/<int:character_id>', endpoint='delete_character')

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_ROUTE)

@app.route('/static/swagger.yaml')
def swagger_file():
    with open('static/swagger.yaml', 'r') as f:
        return f.read()

app.run(host='0.0.0.0', port=PORT, threaded=True)
