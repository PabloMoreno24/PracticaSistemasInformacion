

from collections import namedtuple
from subprocess import call

import pandas
import plotly.utils
from flask import Flask, render_template, request,redirect, session
import sqlite3
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from urllib.request import urlopen
import hashlib
import requests
import matplotlib.pyplot as plt
import graphviz
from plotly.subplots import make_subplots
from sklearn import datasets, linear_model, tree
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestClassifier
from fpdf import FPDF
import os
import kaleido



app = Flask(__name__)


f = open('legal.json')
f2 = open('users.json')
f3 = open('users_IA_clases.json')
f4 = open('users_IA_predecir.json')
data = json.load(f)
data2 = json.load(f2)
dataClases = json.load(f3)
dataPredecir = json.load(f4)

X = []
arrayUsersXp = []
arrayUsersY = []

for i in dataClases['usuarios']:

    auxArray = []

    if (i['emails_phishing_recibidos'] == 0):
        auxArray.append(0)
    else:
        auxArray.append(i['emails_phishing_clicados'] / i['emails_phishing_recibidos'])

    arrayUsersY.append(i['vulnerable'])
    arrayUsersXp.append(auxArray)
    X.append([i['emails_phishing_clicados'], i['emails_phishing_recibidos']])

X_train = X[:-20]
X_test = arrayUsersXp[-20:]
Y_train = arrayUsersY[:-20]
Y_test = arrayUsersY[-20:]
feat_names = ['Emails Recibidos (phishing)', 'Emails cliclados (phishing)']
targ_name = ['No Vulnerable','Vulnerable']


def linear():
    print(arrayUsersXp)
    print(arrayUsersY)
    print(X)
    reg = linear_model.LinearRegression().fit(X_train, Y_train)
    c = reg.coef_
    print(c.T[0])
    inter = reg.intercept_
    multi = []
    for i in range(len(X_test)):
        aux = X_test[i]
        multi.append(c.T[0] * aux[0] + inter)
    print(reg.intercept_)
    plt.scatter(X_test, Y_test, color="red")
    plt.plot(X_test, multi, color="blue", linewidth="3")
    plt.xticks(())
    plt.yticks(())
    plt.savefig('./static/images/plot.png')

randomRess = []
def randomBosque():
    clf = RandomForestClassifier(max_depth=2, random_state=0, n_estimators=10)
    clf.fit(X_train, Y_train)
    for i in test:
        randomRess.append(clf.predict([i]))
    for i in range(len(clf.estimators_)):
        estimator = clf.estimators_[i]
        export_graphviz(estimator, out_file='tree1.dot',feature_names=feat_names,class_names=targ_name, rounded=True, proportion=False, precision=2, filled=True)

        call(['dot', '-Tpng', 'tree1.dot', '-o', 'tree' + str(i) + '.png', '-Gdpi=600'])

arbolResultados = []
def arbolito():
    clf = tree.DecisionTreeClassifier()
    clf.fit(X_train, Y_train)
    for i in test:
        arbolResultados.append(clf.predict([i]))
    dot_data = tree.export_graphviz(clf, out_file=None)
    graph = graphviz.Source(dot_data)
    dot_data = tree.export_graphviz(clf, out_file=None,feature_names=feat_names,class_names=targ_name,
                                    filled=True, rounded=True,
                                    special_characters=True)
    graph = graphviz.Source(dot_data)
    graph.render('test.gv', view = True).replace('\\', '/')

#linear()
#randomBosque()
#arbolito()

def comprobarPassword(password):
    print("Comprobando ",password)
    md5hash = password
    try:
        password_list = str(urlopen(
            "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(),
                            'utf-8')
        for password in password_list.split('\n'):
            guess = hashlib.md5(bytes(password, 'utf-8')).hexdigest()
            if guess == md5hash:
                return 1
                break
            elif guess != md5hash:
                continue
            else:
                return 2
        return 2
    except Exception as exc:
        return 2

def probabilidadClick(cliclados,total):
    if (total!=0):
        return (cliclados/total) * 100
    else:
        return 0

con = sqlite3.connect('practica.db')
cursor_obj = con.cursor()
cursor_obj.execute("DROP TABLE legal")
cursor_obj.execute("DROP TABLE users")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS legal (nombrel,cookies,aviso,proteccion_de_datos,politicas,creacion,primary key(nombrel))")
cursor_obj.execute("CREATE TABLE IF NOT EXISTS users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,probabilidad_click,fechas,num_fechas,ips,num_ips,passVul,primary key (nombre))")
insert_legal = """INSERT INTO legal (nombrel,cookies,aviso,proteccion_de_datos,politicas,creacion) VALUES (?,?,?,?,?,?)"""
insert_users = """INSERT INTO users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,probabilidad_click,fechas,num_fechas,ips,num_ips,passVul) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
for i in data['legal']:
    for j in i.keys():
        for k in i.values():
            datos_legal = (j, k['cookies'], k['aviso'], k['proteccion_de_datos'], k['cookies'] + k['aviso'] + k['proteccion_de_datos'],k['creacion'])
        cursor_obj.execute(insert_legal, datos_legal)
        con.commit()

for i in data2['usuarios']:
    for j in i.keys():
        for k in i.values():
            datos_users = (j, k['telefono'], k['contrasena'], k['provincia'], k['permisos'], k['emails']['total'], k['emails']['phishing'], k['emails']['cliclados'],probabilidadClick(k['emails']['cliclados'],k['emails']['phishing']), str(k['fechas']), len(k['fechas']), str(k['ips']), len(k['ips']), comprobarPassword(k['contrasena']))
        cursor_obj.execute(insert_users, datos_users)
        con.commit()

con.commit()
class PDF(FPDF):
    pass


df = pd.DataFrame()

def ejercicioDos():
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

    print("Ejercicio 2\n-----------\n")
    print("Numero de Observaciones\n-----------")
    print(df.count(),"\n")
    print("Media y Desviación Estandar\n-----------")
    print("Medias\n",df.mean(),"\n")
    print("Desviaciones\n",df.std(),"\n")
    print("Maximo y Minimo de Total Fechas\n-----------")
    print("Maximo",df['Numero Fechas'].max())
    print("Minimo",df['Numero Fechas'].min())
    print("\n")


df_usuarios = pd.DataFrame()
df_admins = pd.DataFrame()
df_menorDoscientos = pd.DataFrame()
df_mayorDoscientos = pd.DataFrame()
totalDF = pd.DataFrame()
def ejercicioTres():


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
    print(df_usuarios)
    num_missing = df_usuarios.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Permisos Administrador\n-----------------------------------------")
    print(df_admins.describe())
    print(df_admins)
    num_missing = df_admins.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Personas con menos de 200 correos\n----------------------------------------------------")
    print(df_menorDoscientos.describe())
    print(df_menorDoscientos)
    num_missing = df_menorDoscientos.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Personas con mas o igual de 200 correos\n----------------------------------------------------------")
    print(df_mayorDoscientos)
    print(df_mayorDoscientos.describe())
    num_missing = df_mayorDoscientos.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    totalDF = pd.concat([df_admins,df_usuarios,df_mayorDoscientos,df_menorDoscientos],axis = 1)
    print("Numero de Observaciones\n------------------------------")
    print(totalDF.count(),"\n")
    print("Numero de valores Missing\n----------------------------")
    print(totalDF.isna().sum(),"\n")
    print("Medianas\n----------------------------")
    print(totalDF.median(),"\n")
    print("Medias\n---------------------------")
    print(totalDF.mean(),"\n")
    print("Desviaciones\n-------------------------------")
    print(totalDF.std(),"\n")
    print("Maximos\n-------------------------------")
    print(totalDF.max(),"\n")
    print("Minimos\n---------------------------------------")
    print(totalDF.min(),"\n")


df_legal = pd.DataFrame()
df_privacidad = pd.DataFrame()
df_vulnerable = pd.DataFrame()
df_conexiones = pd.DataFrame()
df_critico = pd.DataFrame()


def ejercicioCuatro():

    cursor_obj.execute('SELECT nombrel,cookies,aviso,proteccion_de_datos FROM legal ORDER BY politicas')
    rows = cursor_obj.fetchall()
    nombre = []
    cookies = []
    avisos = []
    proteccion_de_datos = []
    for i in range(len(rows)):
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
    no_se_cumple = [0] * len(creacion)
    for i in range(len(creacion)):
        for j in range(len(rows)):
            if rows[j][0] == creacion[i]:
                no_se_cumple[i] = 1 + no_se_cumple[i]
    df_privacidad['No se cumple'] = no_se_cumple


    cursor_obj.execute('SELECT COUNT(num_ips) FROM users where num_ips>=10')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_vulnerable['Comprometidas'] = res

    cursor_obj.execute('SELECT COUNT(num_ips) FROM users where num_ips<10')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_vulnerable['No Comprometidas'] = res


    cursor_obj.execute('SELECT AVG (num_ips) FROM users where passVul=1')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_conexiones['Vulnerables'] = res

    cursor_obj.execute('SELECT AVG(num_ips) FROM users where passVul=2')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_conexiones['No Vulnerables'] = res



    cursor_obj.execute('SELECT probabilidad_click FROM users where passVul=1 ORDER BY probabilidad_click DESC')
    rows = cursor_obj.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    df_critico['Probabilidad de Click'] = res

#def regresionLineal():


ejercicioDos()
ejercicioTres()
ejercicioCuatro()




con.close()

@app.route('/')
def index():  # put application's code here
    return render_template('Login.html')

@app.route('/Casa.html')
def Casa():  # put application's code here
        return render_template("Casa.html")


users = [["admin","admin"],["normal","abc"]]
app.secret_key = "TheSecretKey"

@app.route('/Login.html',methods=["GET","POST"])
def login():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        for i in range(len(users)):
            if (users[i][0]==username and users[i][1]==password):
                session['user'] = username
                return redirect('/Casa.html')

        return "<h1>Wrong username or password</h1>"

    return render_template("Login.html")

@app.route('/Register.html',methods=["GET","POST"])
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        users.append([username,password])

    return render_template("Register.html")

@app.route('/TopUsuariosCriticos.html', methods=["GET","POST"])
def topUssersCrit():
    num = request.form.get('numero', default=10)
    probNum = request.form.get('porcentaje',default='0')
    if(num==''):
        num = 10
    df_critico = pandas.DataFrame()
    con = sqlite3.connect('practica.db')
    cursor_obj = con.cursor()

    if(probNum == '0'):
        query = """SELECT nombre,probabilidad_click FROM users where passVul=1 ORDER BY probabilidad_click DESC LIMIT (?)"""
    elif(probNum == '1'):
        query = """SELECT nombre,probabilidad_click FROM users where passVul=1 AND probabilidad_click>=50 ORDER BY probabilidad_click DESC LIMIT (?)"""
    elif(probNum =='2'):
        query = """SELECT nombre,probabilidad_click FROM users where passVul=1 AND probabilidad_click<50 ORDER BY probabilidad_click DESC LIMIT (?)"""

    cursor_obj.execute(query, (num,))
    rows = cursor_obj.fetchall()
    nombre = []
    prob = []
    for i in range(len(rows)):
        nombre += [rows[i][0]]
        prob += [rows[i][1]]
    df_critico['Nombre'] = nombre
    df_critico['Probabilidad de Click'] = prob
    fig = px.bar(df_critico, x=df_critico['Nombre'], y=df_critico['Probabilidad de Click'])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSONUno = json.dumps(fig, cls=a)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf_w = 210
    pdf_h = 297
    plotly.io.write_image(fig, file='pltx.png', format='png', width=700, height=450)
    pltx = (os.getcwd() + '/' + "pltx.png")
    pdf.set_xy(40.0, 25.0)
    pdf.image(pltx, link='', type='', w=700 / 5, h=450 / 5)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    txt = "Se muestra el top de usuarios críticos. En el eje X podemos ver los nombres de los usuarios cuestion.El eje Y representa la probabilidad de que el usuario pulse un correo spam."
    pdf.set_xy(10.0, 130.0)
    pdf.multi_cell(w=0, h=10, txt=txt, align='L')
    pdf.output('static/topUsuariosCriticos.pdf', 'F')
    con.close()
    return render_template('TopUsuariosCriticos.html', graphJSONUno=graphJSONUno)

@app.route('/TopPaginasVulnerables.html', methods=["GET","POST"])
def topWebsVuln():
    num = request.form.get('numero', default=10)
    if (num == ''):
        num = 10
    df_topWebs =pandas.DataFrame()
    con = sqlite3.connect('practica.db')
    cursor_obj = con.cursor()
    query = """SELECT nombrel,cookies,aviso,proteccion_de_datos FROM legal ORDER BY politicas LIMIT (?)"""
    cursor_obj.execute(query, (num,))
    rows = cursor_obj.fetchall()
    nombre = []
    cookies = []
    avisos = []
    proteccion_de_datos = []
    for i in range(len(rows)):
        nombre += [rows[i][0]]
        cookies += [rows[i][1]]
        avisos += [rows[i][2]]
        proteccion_de_datos += [rows[i][3]]
    df_topWebs['Nombre'] = nombre
    df_topWebs['Cookies'] = cookies
    df_topWebs['Avisos'] = avisos
    df_topWebs['Proteccion de Datos'] = proteccion_de_datos
    fig = go.Figure(data=[
        go.Bar(name='Cookies', x=df_topWebs['Nombre'], y=df_topWebs['Cookies'], marker_color='steelblue'),
        go.Bar(name='Avisos', x=df_topWebs['Nombre'], y=df_topWebs['Avisos'], marker_color='lightsalmon'),
        go.Bar(name='Proteccion de datos', x=df_topWebs['Nombre'], y=df_topWebs['Proteccion de Datos'], marker_color='red')
    ])
    # Change the bar mode
    fig.update_layout(title_text="Peores Webs", title_font_size=41, barmode='group')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf_w = 210
    pdf_h = 297
    plotly.io.write_image(fig, file='pltx.png', format='png', width=700, height=450)
    pltx = (os.getcwd() + '/' + "pltx.png")
    pdf.set_xy(40.0, 25.0)
    pdf.image(pltx, link='', type='', w=700 / 5, h=450 / 5)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0,0,0)
    txt="Se muestra el grafico de las paginas web mas vulnerables. En el eje X podemos ver los nombres de las paginas web en cuestion.El eje Y representa que si esta a 1 la politica esta activada y si esta a 0 no. "
    pdf.set_xy(10.0, 140.0)
    pdf.multi_cell(w=0, h=10, txt=txt,align='L')
    pdf.output('static/topPaginasVulnerables.pdf', 'F')
    return render_template('TopPaginasVulnerables.html', graphJSON=graphJSON)

@app.route("/IA.html")
def IA():

    return render_template("IA.html")

def ejerDos():
    return render_template('TopPaginasVulnerables.html')

@app.route('/ejertres')
def ejerTres():
    observaciones = totalDF.count()

    missing = totalDF.isna().sum()

    mediana = totalDF.median()

    media = totalDF.mean()

    varianza = totalDF.std()

    max = totalDF.max()

    min = totalDF.min()
    return render_template('ejer_tres.html', observaciones=observaciones, missing=missing, mediana=mediana, media=media, varianza=varianza, max=max, min=min)


@app.route('/Ultimas10Vulnerabilidades.html')
def ejerCuatro():
    page = requests.get("https://cve.circl.lu/api/last")
    jsons = page.json()
    lista1 = []
    lista2 = []
    for i in range(0,10):
        lista1 += [jsons[i]['id']]
        lista2 += [jsons[i]['summary']]
    fig = go.Figure(data=[go.Table(header=dict(values=['Vulnerability','Description']),cells=dict(values=[lista1,lista2]))])
    table = plotly.io.to_html(fig)
    return render_template('Ultimas10Vulnerabilidades.html',tableHTML=table)

@app.route('/cuatroa')
def cuatroA():
    fig = px.bar(df_critico, x=df_critico['Nombre'], y=df_critico['Probabilidad de Click'])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/cuatrob')
def cuatroB():
    fig = go.Figure(data=[
        go.Bar(name='Cookies', x=df_legal['Nombre'], y=df_legal['Cookies'], marker_color='steelblue'),
        go.Bar(name='Avisos', x=df_legal['Nombre'], y=df_legal['Avisos'], marker_color='lightsalmon'),
        go.Bar(name='Proteccion de datos', x=df_legal['Nombre'], y=df_legal['Proteccion de Datos'], marker_color='red')
    ])
    # Change the bar mode
    fig.update_layout(title_text="Cinco Peores", title_font_size=41, barmode='group')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/cuatroc')
def cuatroC():
    labels = ['Vulnerables', 'No Vulnerables']
    values = [df_conexiones.at[0, 'Vulnerables'], df_conexiones.at[0, 'No Vulnerables']]
    fig = go.Figure(data=[
        go.Pie(labels=labels, values=values)])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)


@app.route('/cuatrod')
def cuatroD():
    fig = go.Figure(data=[
        go.Bar(name='Se cumple', x=df_privacidad['Creacion'], y=df_privacidad['Se cumple'], marker_color='steelblue'),
        go.Bar(name='No se cumple', x=df_privacidad['Creacion'], y=df_privacidad['No se cumple'], marker_color='lightsalmon')
    ])
    # Change the bar mode
    fig.update_layout(title_text="Comparativa Privacidad segun el Año de Creación", title_font_size=41, barmode='stack')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/cuatroe')
def cuatroE():
    labels = ['No Comprometidas', 'Comprometidas']
    values = [df_vulnerable.at[0, 'No Comprometidas'], df_vulnerable.at[0, 'Comprometidas']]
    fig = go.Figure(data=[
        go.Pie(labels=labels, values=values)])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)


### define a method
def charts(self):
        self.set_xy(40.0,25.0)
        self.image(plt,  link='', type='', w=700/5, h=450/5)


if __name__ == '__main__':
    app.run()
