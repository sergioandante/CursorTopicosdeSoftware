from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)

# Almacenamiento temporal en memoria (en producción usarías una base de datos)
tareas = []
contador_id = 1

@app.route('/')
def index():
    """Página principal que muestra todas las tareas"""
    return render_template('index.html', tareas=tareas)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_tarea():
    """Agregar una nueva tarea"""
    if request.method == 'POST':
        global contador_id
        nueva_tarea = {
            'id': contador_id,
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'completada': False,
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tareas.append(nueva_tarea)
        contador_id += 1
        return redirect(url_for('index'))
    return render_template('agregar.html')

@app.route('/completar/<int:tarea_id>')
def completar_tarea(tarea_id):
    """Marcar una tarea como completada o no completada"""
    for tarea in tareas:
        if tarea['id'] == tarea_id:
            tarea['completada'] = not tarea['completada']
            break
    return redirect(url_for('index'))

@app.route('/eliminar/<int:tarea_id>')
def eliminar_tarea(tarea_id):
    """Eliminar una tarea"""
    global tareas
    tareas = [t for t in tareas if t['id'] != tarea_id]
    return redirect(url_for('index'))

@app.route('/api/tareas', methods=['GET'])
def api_tareas():
    """API endpoint para obtener todas las tareas en JSON"""
    return jsonify(tareas)

if __name__ == '__main__':
    app.run(debug=True)
