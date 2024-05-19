from flask import Flask, jsonify, render_template, request
from models import db, Vetor, ItemVetor
import os, random, secrets, time
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
import plotly.express as px
import pandas as pd

load_dotenv()

app = Flask(__name__)

databasePassword = os.getenv('DATABASE_PASSWORD')
databaseUser = os.getenv('DATABASE_USER')
databaseUrl = os.getenv('DATABASE_URL')
databaseSchema = os.getenv('DATABASE_SCHEMA')

dbURL = "mysql://"+databaseUser+":"+databasePassword+"@"+databaseUrl+"/"+databaseSchema
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config["SECRET_KEY"] = secrets.token_hex(32)
db.init_app(app)

def fisher_yates(valores):
    for i in range(len(valores)-1, 0, -1):
        j = random.randint(0, i)
        valores[i], valores[j] = valores[j], valores[i]
    return valores

def partition(array, menor, maior):
    pivot = array[maior]
    i = menor - 1

    # Percorre todos os elementos
    for j in range(menor, maior):
        if array[j] <= pivot:
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])

    (array[i + 1], array[maior]) = (array[maior], array[i + 1])

    return i + 1

def quickSort(array, menor, maior):
    if menor < maior:
        pi = partition(array, menor, maior)

        quickSort(array, menor, pi - 1)

        quickSort(array, pi + 1, maior)

@app.route('/', methods=['GET', 'POST'])
def criar_grafico():
    if request.method == 'POST':
        x = request.form['x']
        y = request.form['y']
        z = request.form['z']
        grafico_selecionado = request.form.get('tipo_grafico')

        vetx = [float(num.replace(',', '.')) for num in x.split()]
        vety = [float(num.replace(',', '.')) for num in y.split()]
        vetz = [float(num.replace(',', '.')) for num in z.split()]

        print(vetx)
        print(vety)

        df = pd.DataFrame({
            'x': vetx,
            'y': vety
        })

        if grafico_selecionado == 'scatter':
            fig = px.scatter(df, x='x', y='y')
        elif grafico_selecionado == 'line':
            fig = px.line(df, x='x', y='y')
        elif grafico_selecionado == 'bar':
            fig = px.bar(df, x='x', y='y')
        elif grafico_selecionado == 'bubble':
            fig = px.scatter(df, x='x', y='y', size=vetz, size_max=60)
        else: # dot
            fig = px.scatter(df, x='x', y='y')

        graph_html = fig.to_html(full_html=False)

        return render_template('index.html', graph=graph_html)


    return render_template('index.html')

@app.route('/randomizar/<nome_vetor>', methods=['GET'])
def randomizar(nome_vetor):

    numbers = list(range(1, 50001))
    tempo_inicio = time.time()
    valores_randomizados = fisher_yates(numbers)

    tempo_fim = time.time()  # Para o cronômetro
    tempo_execucao = (tempo_fim - tempo_inicio) * 1000

    try:
        vetor = Vetor(nome_vetor=nome_vetor)
        db.session.add(vetor)
        db.session.commit()
    except IntegrityError:
        return "Erro: o nome do vetor já existe no banco", 400

    for i, valor in enumerate(valores_randomizados, start=1):
        item = ItemVetor(valor=valor, id_vetor=vetor.id, seq_valor=i)
        db.session.add(item)

    db.session.commit()

    return jsonify({"vetor": valores_randomizados, "tempo": "{:.2f}".format(tempo_execucao)+"ms"})

@app.route('/ordenar/<nome_vetor>', methods=['GET'])
def ordenar(nome_vetor):
    vetor = Vetor.query.filter_by(nome_vetor=nome_vetor).first()

    if not vetor:
        return "Erro: o nome do vetor não existe no banco", 400

    valores = [item.valor for item in vetor.valores]

    tamanho = len(valores)

    tempo_inicio = time.time()

    quickSort(valores, 0, tamanho - 1)

    tempo_fim = time.time()
    tempo_execucao = (tempo_fim - tempo_inicio) * 1000

    return jsonify({"vetor": valores, "tempo": "{:.2f}".format(tempo_execucao)+"ms"})

if __name__ == '__main__':
    app.app_context().push()
    app.debug = True
    db.create_all()
    app.run()
