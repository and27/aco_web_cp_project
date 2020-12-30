#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g
import flask_sijax 
import os
import time
import math
import random
from  geopy.distance import geodesic
from flask_googlemaps import GoogleMaps, Map, icons
from dynaconf import FlaskDynaconf

DEVELOPMENT_ENV  = True

app = Flask(__name__)

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = path
flask_sijax.Sijax(app)


class Grafo(object):
    def __init__(self, matriz_adjacencia, rank):
        self.matriz = matriz_adjacencia
        self.rank = rank
        self.feromonio = [[1 / (rank * rank) for j in range(rank)]
                          for i in range(rank)]  # m x m

#ACO algorithm implementation
class ACO(object):
    def __init__(self, cont_formiga, generations, alfa, beta, ro, Q=0.0):
        self.Q = Q
        self.ro = ro
        self.beta = beta
        self.alfa = alfa
        self.cont_formiga = cont_formiga
        self.generations = generations

    def resolve(self, grafo):
            melhor_custo = float('inf')
            melhor_solucao = []
            for gen in range(self.generations):
                formigas = [
                    _Ant(self, grafo) for i in range(self.cont_formiga)
                ]
                for ant in formigas:
                    for i in range(grafo.rank - 1):
                        ant._seleciona_proximo()
                    ant.custo_total += grafo.matriz[ant.tabu[-1]][  # retorno para city inicial
                        ant.tabu[0]]
                    if ant.custo_total < melhor_custo:
                        melhor_custo = ant.custo_total
                        melhor_solucao = [] + ant.tabu
                    #ant._atualiza_feromonio_delta()  # atualiza feromonio
                #self._atualiza_feromonio(grafo, formigas)
            return melhor_solucao, melhor_custo

class _Ant(object):
    def __init__(self, aco, grafo):

        self.colonia = aco
        self.grafo = grafo
        self.custo_total = 0.0  # Lk
        self.tabu = []  # caminho escolhido pela ant em uma geração
        self.feromonio_delta = []  #deltaT^Kij
        self.permitido = [i for i in range(grafo.rank)]
        self.eta = [[  # 1/Lij
            0 if i == j else 1 / grafo.matriz[i][j] for j in range(grafo.rank)
        ] for i in range(grafo.rank)]
        inicio = random.randint(0, grafo.rank - 1)  # inicio aleatório
        self.tabu.append(inicio)
        self.atual = inicio
        self.permitido.remove(inicio)

    def _seleciona_proximo(self):
        denominador = 0
        for j in self.permitido:
            denominador += self.grafo.feromonio[
                self.atual][j]**self.colonia.alfa * self.eta[
                    self.atual][j]**self.colonia.beta
        probabilidades = [
            0 for i in range(self.grafo.rank)
        ]  # probabilidades de mover para uma city no próximo passo
        for i in range(self.grafo.rank):
            try:
                self.permitido.index(i)
                probabilidades[i] = self.grafo.feromonio[self.atual][i] ** self.colonia.alfa * \
                    self.eta[self.atual][i] ** self.colonia.beta / denominador
            except ValueError:
                pass   # descarta se a city nao for permitida

        # Select next city using roulette wheel method
        selecionado = 0
        rand = random.random()
        for i, probabilidade in enumerate(probabilidades):
            rand -= probabilidade
            if rand <= 0:
                selecionado = i
                break
        self.permitido.remove(selecionado)
        self.tabu.append(selecionado)
        self.custo_total += self.grafo.matriz[self.atual][selecionado]
        self.atual = selecionado


def calc_distancia(city1, city2):
    coords_1 = (city1['x'], city1['y'])
    coords_2 = (city2['x'], city2['y'])
    return geodesic(coords_1, coords_2).km


cities = [
    {'index':0, 'x':-2.1833, 'y':-79.8833, 'name':'Quito'},
    {'index':1, 'x':-0.2186, 'y':-78.5097, 'name':'Guayaquil'},
    {'index':2, 'x':-1.2417, 'y':-78.6197, 'name':'Ambato'},
    {'index':3, 'x':44.000000, 'y':-72.699997, 'name': 'Vermont'}
]

matriz_adjacencia = []
rank = len(cities)
# Lets calculate adjacency matrix
for i in range(rank):  
    linha = []
    for j in range(rank):
        linha.append(calc_distancia(cities[i], cities[j]))
    matriz_adjacencia.append(linha)

@app.route('/aco')
def index():
    aco = ACO(cont_formiga=10, generations=1, alfa=1.0, beta=10.0, ro=0.5, Q=10)
    grafo = Grafo(matriz_adjacencia, rank)
    caminho, custo = aco.resolve(grafo)
    print(caminho)
    return render_template('index.html')

@app.route('/')
def main_page():
    return render_template("ardu.html")

@flask_sijax.route(app, '/<int:req>')
def ardu(req):
    if req == 100:
        with open("test.txt", 'w') as f:
                f.write(str(100))
                f.close()
                time.sleep(1)
    elif req == 0:
        with open("test.txt", 'w') as f:
                f.write(str(0))
                f.close()

    content = None
    def retrieve_data(obj_response):
        with open("test.txt", "r") as f:
            content = f.read()
            if int(content) == 100:
                obj_response.html("#element", "We have <br>a new node:")
                obj_response.css("#img_element", "display","block")
                obj_response.script("$('#exampleModal').modal('show');")
                obj_response.script("routes()")                
            else:
                obj_response.script("$('#exampleModal').modal('hide')")


        f.close()
        with open("test.txt", 'w') as f:
                f.write(str(0))
                f.close()

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('ardu', retrieve_data) 
        return g.sijax.process_request()
          
    return render_template("ardu.html")


@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug=DEVELOPMENT_ENV, host="0.0.0.0")