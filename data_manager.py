import json
from datetime import datetime
import tkinter.filedialog as filedialog
from tkinter import messagebox

class DataManager:
    def __init__(self):
        self.series = {}
        self.directores = {}  # Nuevo diccionario para almacenar los directores
        self.fechas = {}
        self.capitulos_finalizados = set()
        self.capitulos_coloreados = {}
        self.ultima_fecha = datetime.now()
        
        self.undo_stack = []
        self.redo_stack = []

        self.cargar_datos()

    def guardar_estado(self):
        estado_actual = self.datos_actuales()
        self.undo_stack.append(estado_actual)
        if len(self.undo_stack) > 50:  # Limit the stack size to 50 states
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def deshacer(self):
        if self.undo_stack:
            self.redo_stack.append(self.datos_actuales())
            estado_anterior = self.undo_stack.pop()
            self.establecer_datos(estado_anterior)

    def rehacer(self):
        if self.redo_stack:
            self.undo_stack.append(self.datos_actuales())
            estado_futuro = self.redo_stack.pop()
            self.establecer_datos(estado_futuro)

    def datos_actuales(self):
        return {
            'series': self.series,
            'directores': self.directores,
            'fechas': self.fechas,
            'capitulos_finalizados': list(self.capitulos_finalizados),
            'capitulos_coloreados': self.capitulos_coloreados,
            'ultima_fecha': self.ultima_fecha.strftime("%Y-%m-%d")
        }

    def establecer_datos(self, datos):
        self.series = datos['series']
        self.directores = datos['directores']
        self.fechas = datos['fechas']
        self.capitulos_finalizados = set(datos['capitulos_finalizados'])
        self.capitulos_coloreados = datos['capitulos_coloreados']
        self.ultima_fecha = datetime.strptime(datos['ultima_fecha'], "%Y-%m-%d")
        self.guardar_datos()
        self.actualizar_listas()
        self.actualizar_vista_asignacion()

    def guardar_datos(self, event=None):
        self.guardar_estado()
        datos = self.datos_actuales()
        with open('datos_series.json', 'w') as f:
            json.dump(datos, f, default=str)

    def cargar_datos(self):
        try:
            with open('datos_series.json', 'r') as f:
                datos = json.load(f)
            self.series = datos['series']
            self.directores = datos.get('directores', {})
            self.fechas = datos['fechas']
            self.capitulos_finalizados = set(datos['capitulos_finalizados'])
            self.capitulos_coloreados = datos['capitulos_coloreados']
            self.ultima_fecha = datetime.strptime(datos['ultima_fecha'], "%Y-%m-%d")
        except FileNotFoundError:
            pass

    def exportar_datos(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivos JSON", "*.json")])
        if archivo:
            with open(archivo, 'w') as f:
                json.dump(self.datos_actuales(), f, default=str)
            messagebox.showinfo("Exportar datos", "Datos exportados exitosamente.")

    def importar_datos(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if archivo:
            with open(archivo, 'r') as f:
                datos = json.load(f)
            self.establecer_datos(datos)
            messagebox.showinfo("Importar datos", "Datos importados exitosamente.")
