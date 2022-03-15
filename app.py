from flask import Flask
import sqlite3
import json

app = Flask(__name__)

f = open('legal.json')
data = json.load(f)


con = sqlite3.connect('practica.db')
cursor_obj = con.cursor()
cursor_obj.execute("CREATE TABLE IF NOT EXISTS legal (nombre,cookies,aviso,proteccion_de_datos,creacion, primary key(nombre))")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS users (id,nombre,telefono,password,provincia,permisos,total_emails,phishing_email,ciclados_email,fechas,num_fechas,ips,num_ips,primary key (id))")
inser = """INSERT INTO legal (nombre) VALUES (?)"""

for i in data['legal']:
    for j in i.keys():
        datos = (j,)
        cursor_obj.execute(inser, datos)
        con.commit()

con.commit()
con.close()

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
