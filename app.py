#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g, request, jsonify
import json
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

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyDVKeBLvxyowU6N9aeqOnytCCoII44Y4Gc"
cities_js = []
global optimum_route
# you can also pass key here
GoogleMaps(app, key="AIzaSyDVKeBLvxyowU6N9aeqOnytCCoII44Y4Gc")

# NOTE: this example is using a form to get the apikey


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
    coords_1 = (city1['lat'], city1['lng'])
    coords_2 = (city2['lat'], city2['lng'])
    return geodesic(coords_1, coords_2).km


cities = [
    {'index':0, 'lat':-2.1833, 'lng':-79.8833, 'name':'Quito'},
    {'index':1, 'lat':-0.2186, 'lng':-78.5097, 'name':'Guayaquil'},
    {'index':2, 'lat':-1.2417, 'lng':-78.6197, 'name':'Ambato'},
    {'index':3, 'lat':-2.90055, 'lng':-79.00453, 'name': 'Cuenca'}
]


for ci in cities:
    cities_js.append(json.dumps(ci))

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
    global optimum_route
    optimum_route, custo = aco.resolve(grafo)
    print(optimum_route)
    return render_template('index.html')



@app.route('/', methods=["GET", "POST"])
def main_page():

    # Get the optimum path
    aco = ACO(cont_formiga=10, generations=1, alfa=1.0, beta=10.0, ro=0.5, Q=10)
    grafo = Grafo(matriz_adjacencia, rank)
    optimum_route, custo = aco.resolve(grafo)
    print(optimum_route)
    # ------------------------- #

    #The request can optionally contain the lat, lng or req(to wake up the server)
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    requ = request.args.get('req')
    if requ != None:
        requ = int(requ)

        #Hello I am <b style='color:blue;'>BLUE</b>!"

    defined="<b style='color:black;'>The defined route is: "
    for i in optimum_route:
        defined=defined+cities[i]['name']+" "
    defined=defined+"</b>"

    #Draw lines in google map
    polyline = {
        "stroke_color": "#0AB0DE",
        "stroke_opacity": 1.0,
        "stroke_weight": 3,
        "path": [{"lat": cities[i]['lat'], "lng": cities[i]['lng']} for i in optimum_route],
        "infobox": defined
    }

    print(polyline['path'])

    path1 = [
        (-1.51, -78.51),
        (-1.52, -78.52),
        (-1.53, -78.53),
        (-1.54, -78.54),
    ]

    markers=[]
    for i in range(len(cities)):
        markers.append({'lat':cities[i]['lat'], 'lng':cities[i]['lng'], 'infobox':cities[i]['name']})

    gmap = Map(
        zoom=7,
        identifier="gmap",
        varname="gmap",
        lat=cities[2]['lat'],
        lng=cities[2]['lng'],
        markers = markers,
        style="height:100vh;margin:0;",
        polylines=[polyline],#, path1],
    )

    if (lat != None) & (lng != None):
        cities_js.append(json.dumps({'index':len(cities), 'lat':float(lat), 'lng':float(lng), 'name':'default'}))
        return "0"

    if requ == 100:
        with open("test.txt", 'w') as f:
                f.write(str(100))
                f.close()
                time.sleep(1)
        return "0"

    content = None

    #Ajax function to respond when the server gets an event
    def retrieve_data(obj_response):
        with open("test.txt", "r") as f:
            content = f.read()
            if int(content) == 100:
                obj_response.html("#element", "New node <br> detected")
                obj_response.css("#img_element", "display","block")
                obj_response.script("$('#exampleModal').modal('show');")
                obj_response.script("routes()")
                obj_response.call("initMap", [cities_js])
            else:
                obj_response.script("$('#exampleModal').modal('hide')")

        f.close()
        with open("test.txt", 'w') as f:
                f.write(str(0))
                f.close()

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('retrieve_data', retrieve_data)
        return g.sijax.process_request()


    return render_template("ardu.html", gmap=gmap, cities=cities)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(port=5050, host="0.0.0.0")#,debug=DEVELOPMENT_ENV, host="0.0.0.0")
