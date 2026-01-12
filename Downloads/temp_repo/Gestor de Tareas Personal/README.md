# Gestor de Tareas Personal

Aplicación web para gestionar tareas personales desarrollada con Flask.

## Características

- ✅ Crear nuevas tareas con título y descripción
- ✅ Marcar tareas como completadas
- ✅ Eliminar tareas
- ✅ Interfaz moderna y responsive
- ✅ Almacenamiento en memoria (las tareas se pierden al reiniciar)

## Requisitos

- Python 3.7 o superior
- Flask

## Instalación

1. Instala Flask si no lo tienes instalado:
```bash
py -m pip install flask
```

## Uso

1. Ejecuta la aplicación:
```bash
py app.py
```

2. Abre tu navegador en `http://127.0.0.1:5000`

## Estructura del Proyecto

```
Gestor de Tareas Personal/
├── app.py                 # Aplicación principal Flask
├── templates/             # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── index.html        # Página principal
│   └── agregar.html      # Formulario para agregar tareas
├── README.md             # Este archivo
└── .gitignore           # Archivos a ignorar en Git
```

## Funcionalidades

### Agregar Tarea
- Navega a "Agregar Tarea" desde el menú
- Completa el formulario con título (obligatorio) y descripción (opcional)
- Guarda la tarea

### Completar Tarea
- Haz clic en el botón "Completar" en cualquier tarea
- Las tareas completadas se marcan visualmente

### Eliminar Tarea
- Haz clic en el botón "Eliminar" en cualquier tarea
- Confirma la eliminación

## Notas

- Las tareas se almacenan en memoria, por lo que se pierden al reiniciar la aplicación
- Para producción, considera usar una base de datos (SQLite, PostgreSQL, etc.)
