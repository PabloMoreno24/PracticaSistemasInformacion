import plotly.utils
from flask import Flask, render_template
import sqlite3
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go

app = Flask(__name__)

f = open('legal.json')
f2 = open('users.json')
data = json.load(f)
data2 = json.load(f2)

con = sqlite3.connect('practica.db')
cursor_obj = con.cursor()
cursor_obj.execute("DROP TABLE legal")
cursor_obj.execute("DROP TABLE users")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS legal (nombrel,cookies,aviso,proteccion_de_datos,politicas,creacion,primary key(nombrel))")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,fechas,num_fechas,ips,num_ips,primary key (nombre))")
insert_legal = """INSERT INTO legal (nombrel,cookies,aviso,proteccion_de_datos,politicas,creacion) VALUES (?,?,?,?,?,?)"""
insert_users = """INSERT INTO users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,fechas,num_fechas,ips,num_ips) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"""
for i in data['legal']:
    for j in i.keys():
        for k in i.values():
            datos_legal = (j, k['cookies'], k['aviso'], k['proteccion_de_datos'], k['cookies'] + k['aviso'] + k['proteccion_de_datos'],k['creacion'])
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
    df_usuarios['Phishing Emails Permisos Usuario'] = res

    cursor_obj.execute('SELECT phishing_email FROM users where permisos="1"')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_admins['Phishing Emails Permisos Admin'] = res

    cursor_obj.execute('SELECT phishing_email FROM users where total_emails<200')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_menorDoscientos['Phishing Emails De Gente con < 200 correos'] = res

    cursor_obj.execute('SELECT phishing_email FROM users where total_emails>=200')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_mayorDoscientos['Phishing Emails de Gente >= 200 correos'] = res

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

    totalDF = pd.concat([df_admins,df_usuarios,df_mayorDoscientos,df_menorDoscientos],axis = 1)
    print(totalDF.describe())
    print(totalDF)

df_legal = pd.DataFrame()
df_privacidad = pd.DataFrame()
def ejercicioCuatro():

    cursor_obj.execute('SELECT nombrel,cookies,aviso,proteccion_de_datos FROM legal ORDER BY politicas')
    rows = cursor_obj.fetchall()
    nombre = []
    cookies = []
    avisos = []
    proteccion_de_datos = []
    for i in range(0,5):
        nombre += [rows[i][0]]
        cookies += [rows[i][1]]
        avisos += [rows[i][2]]
        proteccion_de_datos += [rows[i][3]]
    df_legal['Nombre'] = nombre
    df_legal['Cookies'] = cookies
    df_legal['Avisos'] = avisos
    df_legal['Proteccion de Datos'] = proteccion_de_datos



    cursor_obj.execute('SELECT DISTINCT creacion FROM legal ORDER BY creacion')
    rows = cursor_obj.fetchall()
    creacion = []
    for i in range(len(rows)):
        creacion += [rows[i][0]]
    df_privacidad['Creacion'] = creacion

    cursor_obj.execute('SELECT creacion,proteccion_de_datos FROM legal where proteccion_de_datos=1 ORDER BY creacion')
    rows = cursor_obj.fetchall()
    se_cumple = [0]*len(creacion)
    for i in range(len(creacion)):
        for j in range(len(rows)):
            if rows[j][0] == creacion[i]:
                se_cumple[i] = 1 + se_cumple[i]
    df_privacidad['Se cumple'] = se_cumple

    cursor_obj.execute('SELECT creacion,proteccion_de_datos FROM legal where proteccion_de_datos=0 ORDER BY creacion')
    rows = cursor_obj.fetchall()
    print(rows)
    no_se_cumple = [0] * len(creacion)
    for i in range(len(creacion)):
        for j in range(len(rows)):
            if rows[j][0] == creacion[i]:
                no_se_cumple[i] = 1 + no_se_cumple[i]
    df_privacidad['No se cumple'] = no_se_cumple
    print(df_privacidad)


#    fig = go.Figure(data=[
#        go.Bar(name='Se cumple', x=creacion, y=se_cumple,marker_color='steelblue'),
#        go.Bar(name='No se cumple', x=creacion, y=no_se_cumple,marker_color='lightsalmon')
#    ])
    # Change the bar mode
#    fig.update_layout(title_text="Comparativa Privacidad segun el Año de Creación",title_font_size=41,barmode='stack')
#    fig.show()

ejercicioCuatro()
ejercicioDos()
con.close()

@app.route('/')
def index():  # put application's code here

    return render_template('index.html')

@app.route('/ejeruno')
def ejerUno():

    return render_template('ejer_uno.html')


@app.route('/ejerdos')
def ejerDos():
    return render_template('ejer_dos.html')



@app.route('/ejertres')
def ejerTres():
    return render_template('ejer_tres.html')


@app.route('/ejercuatro')
def ejerCuatro():
    return render_template('ejer_cuatro.html')

@app.route('/cuatroa')
def cuatroA():
    fig = go.Figure(data=[
        go.Bar(name='Se cumple', x=df_privacidad['Creacion'], y=df_privacidad['Se cumple'], marker_color='steelblue'),
        go.Bar(name='No se cumple', x=df_privacidad['Creacion'], y=df_privacidad['No se cumple'], marker_color='lightsalmon')
    ])
    # Change the bar mode
    fig.update_layout(title_text="Comparativa Privacidad segun el Año de Creación", title_font_size=41, barmode='stack')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run()
