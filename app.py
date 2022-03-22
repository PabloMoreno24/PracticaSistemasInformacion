from flask import Flask
import sqlite3
import json
import pandas as pd
import numpy as np

app = Flask(__name__)

f = open('legal.json')
f2 = open('users.json')
data = json.load(f)
data2 = json.load(f2)


con = sqlite3.connect('practica.db')
cursor_obj = con.cursor()
cursor_obj.execute("DROP TABLE legal")
cursor_obj.execute("DROP TABLE users")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS legal (nombrel,cookies,aviso,proteccion_de_datos,creacion, primary key(nombrel))")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,fechas,num_fechas,ips,num_ips,primary key (nombre))")
insert_legal = """INSERT INTO legal (nombrel,cookies,aviso,proteccion_de_datos,creacion) VALUES (?,?,?,?,?)"""
insert_users = """INSERT INTO users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,fechas,num_fechas,ips,num_ips) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"""
for i in data['legal']:
    for j in i.keys():
        for k in i.values():
            datos_legal = (j, k['cookies'], k['aviso'], k['proteccion_de_datos'], k['creacion'])

        cursor_obj.execute(insert_legal, datos_legal)
        con.commit()

for i in data2['usuarios']:
    for j in i.keys():
        for k in i.values():
            datos_users = (j, k['telefono'], k['contrasena'], k['provincia'], k['permisos'], k['emails']['total'], k['emails']['phishing'], k['emails']['cliclados'], str(k['fechas']), len(k['fechas']), str(k['ips']), len(k['ips']))
        cursor_obj.execute(insert_users, datos_users)
        con.commit()

con.commit()

df = pd.DataFrame()

cursor_obj.execute('SELECT num_fechas FROM users')
rows = cursor_obj.fetchall()
res=[]
for i in rows:
    res+=[i[0]]
df['Numero Fechas'] = res

cursor_obj.execute('SELECT num_ips FROM users')
rows = cursor_obj.fetchall()
res=[]
for i in rows:
    res+=[i[0]]
df['Numero IPS'] = res

cursor_obj.execute('SELECT total_emails FROM users')
rows = cursor_obj.fetchall()
res=[]
for i in rows:
    res+=[i[0]]
df['Total Emails'] = res
print(df)
print(df.mean())
print(df.describe())
con.close()

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
