# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 19:43:43 2024

@author: Edgar Ruíz
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import sqlite3

# Base de datos y diagnóstico
def crear_base_datos():
    conexion = sqlite3.connect('diagnostico_automotriz.db')
    cursor = conexion.cursor()

    # Eliminar tablas existentes
    cursor.execute('DROP TABLE IF EXISTS categorias')
    cursor.execute('DROP TABLE IF EXISTS sintomas')
    cursor.execute('DROP TABLE IF EXISTS problemas')
    cursor.execute('DROP TABLE IF EXISTS preguntas')
    cursor.execute('DROP TABLE IF EXISTS respuestas')

    # Crear tablas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY,
        nombre TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sintomas (
        id INTEGER PRIMARY KEY,
        descripcion TEXT,
        id_categoria INTEGER,
        FOREIGN KEY (id_categoria) REFERENCES categorias(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS problemas (
        id INTEGER PRIMARY KEY,
        descripcion TEXT,
        solucion TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS preguntas (
        id INTEGER PRIMARY KEY,
        id_sintoma INTEGER,
        texto TEXT,
        FOREIGN KEY (id_sintoma) REFERENCES sintomas(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS respuestas (
        id INTEGER PRIMARY KEY,
        id_pregunta INTEGER,
        respuesta TEXT,
        id_problema INTEGER,
        puntuacion INTEGER,
        FOREIGN KEY (id_pregunta) REFERENCES preguntas(id),
        FOREIGN KEY (id_problema) REFERENCES problemas(id)
    )
    ''')

    # Poblar base de datos con datos iniciales
    categorias = [
        (1, "Motor"),
        (2, "Transmisión"),
        (3, "Frenos"),
        (4, "Suspensión")
    ]
    sintomas = [
        (1, "El motor no arranca", 1),
        (2, "El motor pierde potencia o fuerza",1),
        (3, "Ruidos en la transmisión", 2),
        (4, "Frenos débiles", 3),
        (6, "Ruido al pasar baches", 4)
    ]
    problemas = [
        (1, "Batería descargada", "Revisar y cargar o reemplazar la batería."),
        (2, "Fallas en el alternador", "Revisar el alternador y reemplazarlo si es necesario."),
        (3, "Falta de líquido de frenos", "Revisar y llenar el líquido de frenos."),
        (4, "Amortiguadores desgastados", "Reemplazar los amortiguadores."),
        (5, "Las bujias pueden estar dañadas", "Reemplace las bujias."),
    ]
    preguntas = [
        (1, 1, "¿La batería está completamente cargada?"),
        (2, 1, "¿Se escucha un clic al girar la llave?"),
        (3, 2, "¿Has cambiado las bujías del motor?"),
        (4, 4, "¿El pedal de freno está esponjoso?"),
        (5, 6, "¿Se escucha un ruido metálico al pasar baches?"),
    ]
    respuestas = [
        (1, 1, "No", 1, 10),  # Batería descargada
        (1, 2, "No", 2, 10),  # Fallas en el alternador
        (2, 3, "No", 5, 10),  # Cambie las bujias 
        (3, 4, "Sí", 3, 10),  # Falta de líquido de frenos
        (4, 5, "Sí", 4, 10),  # Amortiguadores desgastados
    ]

    # Insertar datos en las tablas
    cursor.executemany('INSERT OR IGNORE INTO categorias VALUES (?, ?)', categorias)
    cursor.executemany('INSERT OR IGNORE INTO sintomas VALUES (?, ?, ?)', sintomas)
    cursor.executemany('INSERT OR IGNORE INTO problemas VALUES (?, ?, ?)', problemas)
    cursor.executemany('INSERT OR IGNORE INTO preguntas VALUES (?, ?, ?)', preguntas)
    cursor.executemany('INSERT OR IGNORE INTO respuestas VALUES (?, ?, ?, ?, ?)', respuestas)

    conexion.commit()
    conexion.close()

# Selección de síntomas por categoría
def cargar_sintomas_por_categoria():
    global id_categoria_actual
    id_categoria_actual = categorias_combobox.current() + 1

    if id_categoria_actual is None:
        return

    # Obtener síntomas de la categoría seleccionada
    conexion = sqlite3.connect('diagnostico_automotriz.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT id, descripcion FROM sintomas WHERE id_categoria = ?', (id_categoria_actual,))
    sintomas = cursor.fetchall()
    conexion.close()

    # Limpiar y actualizar el combobox de síntomas
    if sintomas:
        sintomas_combobox['values'] = [s[1] for s in sintomas]
        sintomas_combobox.set('')  # Resetear selección
        area_chat.insert(tk.END, "Sistema: Selecciona un síntoma para continuar.\n")
    else:
        sintomas_combobox['values'] = []
        sintomas_combobox.set('')  # No hay síntomas disponibles
        area_chat.insert(tk.END, "Sistema: No se encontraron síntomas para esta categoría.\n")

# Diagnóstico basado en el síntoma seleccionado
def iniciar_diagnostico():
    global id_sintoma_actual, id_pregunta_actual, puntajes

    sintoma_seleccionado = sintomas_combobox.get()
    if not sintoma_seleccionado:
        messagebox.showerror("Error", "Por favor selecciona un síntoma.")
        return

    # Obtener ID del síntoma
    conexion = sqlite3.connect('diagnostico_automotriz.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT id FROM sintomas WHERE descripcion = ? AND id_categoria = ?',
                   (sintoma_seleccionado, id_categoria_actual))
    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        id_sintoma_actual = resultado[0]
        id_pregunta_actual = 0
        puntajes = {}
        area_chat.insert(tk.END, f"Sistema: Síntoma seleccionado: {sintoma_seleccionado}\n")
        area_chat.insert(tk.END, "Sistema: Vamos a realizar algunas preguntas.\n")
        enviar_pregunta()
    else:
        messagebox.showerror("Error", "No se encontró información para este síntoma.")

# Realizar una pregunta
def enviar_pregunta():
    global id_pregunta_actual

    conexion = sqlite3.connect('diagnostico_automotriz.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT id, texto FROM preguntas WHERE id_sintoma = ? AND id > ? ORDER BY id ASC LIMIT 1',
                   (id_sintoma_actual, id_pregunta_actual))
    pregunta = cursor.fetchone()
    conexion.close()

    if pregunta:
        id_pregunta_actual = pregunta[0]
        area_chat.insert(tk.END, f"Sistema: {pregunta[1]}\n")
        opciones_respuesta_frame.pack(pady=5)
    else:
        diagnostico_final()

# Procesar respuesta y continuar
def procesar_respuesta(respuesta_usuario):
    global puntajes

    # Actualizar puntuaciones
    conexion = sqlite3.connect('diagnostico_automotriz.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT id_problema, puntuacion FROM respuestas WHERE id_pregunta = ? AND respuesta = ?',
                   (id_pregunta_actual, respuesta_usuario))
    resultados = cursor.fetchall()
    conexion.close()

    for id_problema, puntuacion in resultados:
        puntajes[id_problema] = puntajes.get(id_problema, 0) + puntuacion

    # Siguiente pregunta
    enviar_pregunta()

# Diagnóstico final
def diagnostico_final():
    global puntajes

    if not puntajes:
        area_chat.insert(tk.END, "Sistema: No pude determinar el problema con la información proporcionada.\n")
        return

    conexion = sqlite3.connect('diagnostico_automotriz.db')
    cursor = conexion.cursor()
    id_mejor_opcion = max(puntajes, key=puntajes.get)
    cursor.execute('SELECT descripcion, solucion FROM problemas WHERE id = ?', (id_mejor_opcion,))
    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        area_chat.insert(tk.END, f"Sistema: Diagnóstico final:\nProblema: {resultado[0]}\nSolución: {resultado[1]}\n")
    else:
        area_chat.insert(tk.END, "Sistema: No pude determinar el problema con la información proporcionada.\n")

# Crear la base de datos
crear_base_datos()

# Variables globales
id_categoria_actual = None
id_sintoma_actual = None
id_pregunta_actual = 0
puntajes = {}

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Sistema Experto - Diagnóstico Automotriz")
ventana.geometry("600x600")

# Área de chat
area_chat = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, state='normal', height=20, font=("Arial", 10))
area_chat.pack(padx=10, pady=10)
area_chat.insert(tk.END, "Sistema: Bienvenido. Selecciona una categoría para comenzar.\n")

# Menú de categorías
categorias_label = tk.Label(ventana, text="Categoría:", font=("Arial", 12))
categorias_label.pack(pady=5)

categorias_combobox = ttk.Combobox(ventana, state="readonly", font=("Arial", 12))
categorias_combobox['values'] = ["Motor", "Transmisión", "Frenos", "Suspensión"]
categorias_combobox.pack(pady=5)
categorias_combobox.bind("<<ComboboxSelected>>", lambda _: cargar_sintomas_por_categoria())

# Menú de síntomas
sintomas_label = tk.Label(ventana, text="Síntoma:", font=("Arial", 12))
sintomas_label.pack(pady=5)

sintomas_combobox = ttk.Combobox(ventana, state="readonly", font=("Arial", 12))
sintomas_combobox.pack(pady=5)

# Botón para iniciar diagnóstico
iniciar_diagnostico_boton = tk.Button(ventana, text="Iniciar Diagnóstico", command=iniciar_diagnostico, font=("Arial", 12))
iniciar_diagnostico_boton.pack(pady=10)

# Opciones de respuesta
opciones_respuesta_frame = tk.Frame(ventana)
opciones_respuesta_si = tk.Button(opciones_respuesta_frame, text="Sí", font=("Arial", 12),
                                   command=lambda: procesar_respuesta("Sí"))
opciones_respuesta_si.grid(row=0, column=0, padx=5)
opciones_respuesta_no = tk.Button(opciones_respuesta_frame, text="No", font=("Arial", 12),
                                   command=lambda: procesar_respuesta("No"))
opciones_respuesta_no.grid(row=0, column=1, padx=5)

ventana.mainloop()
