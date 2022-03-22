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

def ejercicioDos():
    df = pd.DataFrame()
    cursor_obj.execute('SELECT num_fechas FROM users')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df['Numero Fechas'] = res

    cursor_obj.execute('SELECT num_ips FROM users')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df['Numero IPS'] = res

    cursor_obj.execute('SELECT total_emails FROM users')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df['Total Emails'] = res

    print("Ejercicio 2\n-----------")
    print(df.describe())
    print("\n")

def ejercicioTres():
    df_usuarios = pd.DataFrame()
    df_admins = pd.DataFrame()
    df_menorDoscientos = pd.DataFrame()
    df_mayorDoscientos = pd.DataFrame()

    cursor_obj.execute('SELECT phishing_email FROM users where permisos="0"')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_usuarios['Phishing Emails'] = res

    cursor_obj.execute('SELECT phishing_email FROM users where permisos="1"')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_admins['Phishing Emails'] = res

    cursor_obj.execute('SELECT phishing_email FROM users where total_emails<200')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_menorDoscientos['Phishing Emails'] = res

    cursor_obj.execute('SELECT phishing_email FROM users where total_emails>=200')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_mayorDoscientos['Phishing Emails'] = res

    print("Ejercicio 3\n-----------")
    print("Phishing Emails de Permisos Usuario\n-----------------------------------")
    print(df_usuarios.describe())
    num_missing = df_usuarios.isnull().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Permisos Administrador\n-----------------------------------------")
    print(df_admins.describe())
    num_missing = df_admins.isnull().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Personas con menos de 200 correos\n----------------------------------------------------")
    print(df_menorDoscientos.describe())
    num_missing = df_menorDoscientos.isnull().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Personas con mas o igual de 200 correos\n----------------------------------------------------------")
    print(df_mayorDoscientos.describe())
    num_missing = df_mayorDoscientos.isnull().sum()
    print("Valores Missing de", num_missing)
    print("\n")

con.close()
@app.route('/')
def hello_world():  # put application's code here

    return 'Hello World|'


if __name__ == '__main__':
    app.run()
