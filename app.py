from flask import Flask, request, jsonify, render_template
import math
import random

app = Flask(__name__)

# Definición de coordenadas de ciudades
coord = {
    "Jiloyork": [19.916012, -99.580580],
    "Toluca": [19.289165, -99.655697],
    "Atlacomulco": [19.799520, -99.873844],
    "Guadalajara": [20.677754, -103.346253],
    "Monterrey": [25.691611, -100.321838],
    "QuintanaRoo": [21.163111, -86.802315],
    "Michohacan": [19.701400, -101.208296],
    "Aguascalientes": [21.876410, -102.264386],
    "CDMX": [19.432713, -99.133183],
    "QRO": [20.597194, -100.386670]
}

# Función para calcular distancia entre ciudades
def distancia(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Evaluar distancia total de una ruta
def evalua_ruta(ruta):
    total = sum(distancia(coord[ruta[i]], coord[ruta[i+1]]) for i in range(len(ruta)-1))
    total += distancia(coord[ruta[-1]], coord[ruta[0]])  # Cierra el circuito
    return total

# Algoritmo de templado simulado
def simulated_annealing(ruta, T, T_MIN, V_enfriamiento):
    while T > T_MIN:
        dist_actual = evalua_ruta(ruta)
        for _ in range(V_enfriamiento):
            i, j = random.sample(range(1, len(ruta)-1), 2)  # Evita mover origen/destino
            ruta_tmp = ruta[:]
            ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
            dist_nueva = evalua_ruta(ruta_tmp)
            delta = dist_actual - dist_nueva
            if dist_nueva < dist_actual or random.random() < math.exp(delta/T):
                ruta = ruta_tmp
                dist_actual = dist_nueva

        T -= 0.005
    
    return ruta

# Página principal con el formulario
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar datos y calcular la mejor ruta
@app.route('/ruta', methods=['POST'])
def obtener_ruta():
    datos = request.json

    print("Datos recibidos:", datos)  # Depuración: Ver los datos en la consola

    if not datos:
        return jsonify({'error': 'No se recibieron datos'}), 400

    origen = datos.get('origen')
    destino = datos.get('destino')

    if not origen or not destino:
        return jsonify({'error': 'Debes seleccionar una ciudad de origen y destino'}), 400

    if origen not in coord or destino not in coord:
        return jsonify({'error': 'Las ciudades seleccionadas no son válidas'}), 400

    T = datos.get('temperatura_inicial', 100)
    T_MIN = datos.get('temperatura_minima', 1)
    V_enfriamiento = datos.get('velocidad_enfriamiento', 500)

    # Filtrar ciudades intermedias
    ciudades_intermedias = [ciudad for ciudad in coord.keys() if ciudad not in [origen, destino]]
    random.shuffle(ciudades_intermedias)

    # Generar ruta inicial con origen y destino fijos
    ruta_inicial = [origen] + ciudades_intermedias + [destino]
    ruta_optima = simulated_annealing(ruta_inicial, T, T_MIN, V_enfriamiento)

    return jsonify({
        'ruta_optima': ruta_optima,
        'distancia_total': evalua_ruta(ruta_optima)
    })

if __name__ == '__main__':
    app.run(debug=True)
