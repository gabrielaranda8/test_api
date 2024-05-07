
import sqlite3
from flask import Flask, g

app = Flask(__name__)
DATABASE = 'characters.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Define la estructura de la tabla Character
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Character (
                id INTEGER PRIMARY KEY,
                name TEXT,
                height INTEGER,
                mass INTEGER,
                hair_color TEXT,
                skin_color TEXT,
                eye_color TEXT,
                birth_year INTEGER
            )
        ''')
        db.commit()

if __name__ == '__main__':
    init_db()