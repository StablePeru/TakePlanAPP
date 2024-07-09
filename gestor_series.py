import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, simpledialog
from tkcalendar import Calendar
from datetime import datetime, timedelta
from tooltips import ToolTip
from data_manager import DataManager

class GestorSeries:
    def __init__(self, root):
        print("Inicializando la aplicación...")  # Depuración
        self.root = root
        self.root.title("Gestor de Series y Capítulos")
        self.root.geometry("1200x800")

        # Establecer tema ttk
        self.root.style = ttk.Style()
        self.root.style.theme_use('clam')
        self.root.configure(background='#f0f0f0')

        print("Inicializando DataManager...")  # Depuración
        self.data_manager = DataManager()

        print("Creando notebook...")  # Depuración
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.fecha_seleccionada = None
        self.arrastrando = False
        self.modo_finalizado = False
        self.actualizando_vista = False  # Flag para evitar recursión infinita

        # Inicializar atributos
        self.leyenda_frame = None
        self.scrollable_frame = None
        self.canvas = None
        self.tabla_frame = None
        self.scrollbar = None
        self.search_entry = None
        self.btn_finalizado = None

        print("Creando vista de creación...")  # Depuración
        self.crear_vista_creacion()
        print("Vista de creación creada.")  # Depuración

        print("Creando vista de asignación...")  # Depuración
        self.crear_vista_asignacion()
        print("Vista de asignación creada.")  # Depuración

        self.root.bind('<Control-s>', self.data_manager.guardar_datos)
        self.notebook.bind("<<NotebookTabChanged>>", self.actualizar_vista_asignacion)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        print("Actualizando listas...")  # Depuración
        self.actualizar_listas()
        print("Listas actualizadas.")  # Depuración

    def crear_vista_creacion(self):
        print("Inicializando vista de creación...")  # Depuración
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Crear Series y Fechas")
        
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(8, weight=1)
        
        series_frame = ttk.LabelFrame(frame, text="Agregar Serie", padding=(10, 10))
        series_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ttk.Label(series_frame, text="Nombre de la Serie:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.serie_entry = ttk.Entry(series_frame, width=30)
        self.serie_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(series_frame, text="Número de Capítulos:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.capitulos_entry = ttk.Entry(series_frame, width=10)
        self.capitulos_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(series_frame, text="Director:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.director_entry = ttk.Entry(series_frame, width=30)
        self.director_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(series_frame, text="Agregar Serie", command=self.agregar_serie).grid(row=3, column=0, columnspan=2, pady=10)
        
        dates_frame = ttk.LabelFrame(frame, text="Agregar Semana", padding=(10, 10))
        dates_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ttk.Label(dates_frame, text="Semana:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.fecha_entry = ttk.Entry(dates_frame, width=20, state='readonly')
        self.fecha_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(dates_frame, text="Seleccionar Semana", command=self.abrir_calendario).grid(row=0, column=2, padx=5, pady=5)
        
        self.color_button = ttk.Button(dates_frame, text="Elegir Color", command=self.elegir_color)
        self.color_button.grid(row=1, column=0, pady=5)
        self.color_label = ttk.Label(dates_frame, text="       ", background="white", borderwidth=1, relief="solid")
        self.color_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(dates_frame, text="Agregar Semana", command=self.agregar_fecha).grid(row=2, column=0, columnspan=3, pady=10)
        
        lists_frame = ttk.Frame(frame)
        lists_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.columnconfigure(1, weight=1)
        
        series_list_frame = ttk.LabelFrame(lists_frame, text="Series", padding=(10, 10))
        series_list_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.series_listbox = tk.Listbox(series_list_frame, width=40, height=10, activestyle='none', highlightthickness=1, selectbackground="#5a9")
        self.series_listbox.pack(expand=True, fill='both')
        
        series_buttons_frame = ttk.Frame(series_list_frame)
        series_buttons_frame.pack(fill='x', pady=5)
        ttk.Button(series_buttons_frame, text="Editar", command=self.editar_serie).pack(side=tk.LEFT, padx=5)
        ttk.Button(series_buttons_frame, text="Eliminar", command=self.eliminar_serie).pack(side=tk.LEFT, padx=5)
        
        fechas_list_frame = ttk.LabelFrame(lists_frame, text="Semanas", padding=(10, 10))
        fechas_list_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.fechas_listbox = tk.Listbox(fechas_list_frame, width=40, height=10, activestyle='none', highlightthickness=1, selectbackground="#5a9")
        self.fechas_listbox.pack(expand=True, fill='both')
        
        fechas_buttons_frame = ttk.Frame(fechas_list_frame)
        fechas_buttons_frame.pack(fill='x', pady=5)
        ttk.Button(fechas_buttons_frame, text="Editar", command=self.editar_fecha).pack(side=tk.LEFT, padx=5)
        ttk.Button(fechas_buttons_frame, text="Eliminar", command=self.eliminar_fecha).pack(side=tk.LEFT, padx=5)
        
        # Botones de exportar e importar
        ttk.Button(frame, text="Exportar Datos", command=self.data_manager.exportar_datos).grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="Importar Datos", command=self.data_manager.importar_datos).grid(row=3, column=1, pady=10)

        # Botones de deshacer y rehacer
        ttk.Button(frame, text="Deshacer", command=self.data_manager.deshacer).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Rehacer", command=self.data_manager.rehacer).grid(row=4, column=1, pady=10)

        print("Vista de creación inicializada.")  # Depuración

    def crear_vista_asignacion(self):
        print("Inicializando vista de asignación...")  # Depuración
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Asignar Capítulos")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=5)

        ttk.Label(search_frame, text="Buscar Serie:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_series)

        self.leyenda_frame = ttk.Frame(frame)
        self.leyenda_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)

        self.tabla_frame = ttk.Frame(frame)
        self.tabla_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
        self.tabla_frame.columnconfigure(0, weight=1)
        self.tabla_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.tabla_frame, background='#f0f0f0', borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.btn_finalizado = ttk.Button(frame, text="Marcar como Finalizado", command=self.toggle_modo_finalizado)
        self.btn_finalizado.grid(row=2, column=0, pady=10)

        self.root.bind('<Configure>', self.on_window_resize)

        print("Vista de asignación inicializada.")  # Depuración

    def actualizar_listas(self):
        print("Actualizando listas de series y fechas...")  # Depuración
        self.series_listbox.delete(0, tk.END)
        for serie, num_capitulos in self.data_manager.series.items():
            self.series_listbox.insert(tk.END, f"{serie}: {num_capitulos} capítulos")

        self.fechas_listbox.delete(0, tk.END)
        for fecha, color in self.data_manager.fechas.items():
            self.fechas_listbox.insert(tk.END, fecha)
            index = self.fechas_listbox.size() - 1
            self.fechas_listbox.itemconfig(index, {'bg': color})

        self.actualizar_vista_asignacion()

    def actualizar_vista_asignacion(self):
        if self.actualizando_vista:
            return
        self.actualizando_vista = True
        print("Actualizando vista de asignación...")  # Depuración
        # Limpiar leyenda y tabla
        for widget in self.leyenda_frame.winfo_children():
            widget.destroy()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Actualizar leyenda de fechas
        for fecha, color in self.data_manager.fechas.items():
            btn = tk.Button(self.leyenda_frame, text=fecha, bg=color, command=lambda f=fecha: self.seleccionar_fecha_asignacion(f))
            btn.pack(side=tk.LEFT, padx=5)

        # Configurar columnas del scrollable_frame
        self.scrollable_frame.columnconfigure(0, weight=3)  # Serie
        self.scrollable_frame.columnconfigure(1, weight=5)  # Capítulos
        self.scrollable_frame.columnconfigure(2, weight=3)  # Director
        self.scrollable_frame.columnconfigure(3, weight=2)  # Acción

        # Actualizar tabla de series y capítulos
        ttk.Label(self.scrollable_frame, text="Serie", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Label(self.scrollable_frame, text="Capítulos", font=('Arial', 12, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(self.scrollable_frame, text="Director", font=('Arial', 12, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        ttk.Label(self.scrollable_frame, text="Acción", font=('Arial', 12, 'bold')).grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        for i, (serie, num_capitulos) in enumerate(self.data_manager.series.items(), start=1):
            ttk.Label(self.scrollable_frame, text=serie).grid(row=i, column=0, padx=5, pady=2, sticky='ew')
            capitulos_frame = ttk.Frame(self.scrollable_frame)
            capitulos_frame.grid(row=i, column=1, padx=5, pady=2, sticky='ew')

            capitulos_por_fila = self.calcular_capitulos_por_fila()
            filas = (num_capitulos + capitulos_por_fila - 1) // capitulos_por_fila

            for j in range(1, num_capitulos + 1):
                fila = (j - 1) // capitulos_por_fila
                columna = (j - 1) % capitulos_por_fila

                cap_label = tk.Label(capitulos_frame, text=str(j), width=3, relief="ridge", borderwidth=1, background='#ffffff', font=('Arial', 10))
                if f"{serie}_{j}" in self.data_manager.capitulos_finalizados:
                    cap_label.config(bg="black", fg="white")
                elif f"{serie}_{j}" in self.data_manager.capitulos_coloreados:
                    cap_label.config(bg=self.data_manager.capitulos_coloreados[f"{serie}_{j}"])
                cap_label.grid(row=fila, column=columna, padx=1, pady=1)
                cap_label.bind("<Button-1>", self.iniciar_arrastre)
                cap_label.bind("<B1-Motion>", self.arrastrar)
                cap_label.bind("<ButtonRelease-1>", self.finalizar_arrastre)

            # Campo de texto para el director
            director_entry = ttk.Entry(self.scrollable_frame, width=20)
            director_entry.insert(0, self.data_manager.directores.get(serie, ""))
            director_entry.grid(row=i, column=2, padx=5, pady=2, sticky='ew')
            director_entry.bind("<FocusOut>", lambda e, s=serie, de=director_entry: self.guardar_director(s, de))

            # Botones de acción
            action_frame = ttk.Frame(self.scrollable_frame)
            action_frame.grid(row=i, column=3, padx=5, pady=2, sticky='ew')
            ttk.Button(action_frame, text="Editar", command=lambda s=serie: self.editar_serie_asignacion(s)).pack(side=tk.LEFT, padx=2)
            ttk.Button(action_frame, text="Eliminar", command=lambda s=serie: self.eliminar_serie_asignacion(s)).pack(side=tk.LEFT, padx=2)

        self.ajustar_ancho_canvas()
        self.actualizando_vista = False

    def calcular_capitulos_por_fila(self):
        # Obtener el ancho de la ventana
        ancho_ventana = self.root.winfo_width()
        
        # Definir el ancho mínimo de cada capítulo y el margen
        ancho_capitulo_min = 50
        margen_min = 10
        
        # Calcular el ancho disponible para los capítulos (restando un margen a ambos lados)
        ancho_disponible = ancho_ventana - 10 * margen_min
        
        # Calcular el número de capítulos por fila
        capitulos_por_fila = max(1, ancho_disponible // ancho_capitulo_min)
        
        return capitulos_por_fila

    def on_window_resize(self, event):
        if not self.actualizando_vista:
            print("Ventana redimensionada...")  # Depuración
            self.actualizar_vista_asignacion()

    def ajustar_ancho_canvas(self):
        self.canvas.update_idletasks()
        self.canvas.config(width=self.tabla_frame.winfo_width() - self.scrollbar.winfo_width())

    def guardar_director(self, serie, director_entry):
        director = director_entry.get()
        self.data_manager.directores[serie] = director
        self.data_manager.guardar_datos()

    def agregar_serie(self):
        nombre = self.serie_entry.get().strip()
        director = self.director_entry.get().strip()
        try:
            capitulos = int(self.capitulos_entry.get())
            if not nombre:
                messagebox.showerror("Error", "El nombre de la serie no puede estar vacío.")
                return
            if capitulos <= 0:
                messagebox.showerror("Error", "Por favor, ingrese un número positivo de capítulos.")
                return
            
            self.data_manager.series[nombre] = capitulos
            self.data_manager.directores[nombre] = director
            self.series_listbox.insert(tk.END, f"{nombre}: {capitulos} capítulos")
            self.serie_entry.delete(0, tk.END)
            self.capitulos_entry.delete(0, tk.END)
            self.director_entry.delete(0, tk.END)
            self.data_manager.guardar_datos()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número válido de capítulos.")

    def editar_serie_asignacion(self, serie):
        nuevo_nombre = simpledialog.askstring("Editar Serie", f"Nuevo nombre para {serie}:", initialvalue=serie)
        if nuevo_nombre:
            nuevo_capitulos = simpledialog.askinteger("Editar Serie", f"Nuevo número de capítulos para {nuevo_nombre}:", initialvalue=self.data_manager.series[serie])
            if nuevo_capitulos is not None:
                del self.data_manager.series[serie]
                self.data_manager.series[nuevo_nombre] = nuevo_capitulos
                self.actualizar_listas()
                self.actualizar_vista_asignacion()
                self.data_manager.guardar_datos()

    def eliminar_serie_asignacion(self, serie):
        if messagebox.askyesno("Eliminar Serie", f"¿Estás seguro de que quieres eliminar la serie {serie}?"):
            del self.data_manager.series[serie]
            self.actualizar_listas()
            self.actualizar_vista_asignacion()
            self.data_manager.guardar_datos()

    def editar_serie(self):
        seleccion = self.series_listbox.curselection()
        if seleccion:
            serie = self.series_listbox.get(seleccion[0]).split(":")[0]
            nuevo_nombre = simpledialog.askstring("Editar Serie", f"Nuevo nombre para {serie}:", initialvalue=serie)
            if nuevo_nombre:
                nuevo_capitulos = simpledialog.askinteger("Editar Serie", f"Nuevo número de capítulos para {nuevo_nombre}:", initialvalue=self.data_manager.series[serie])
                if nuevo_capitulos is not None:
                    del self.data_manager.series[serie]
                    self.data_manager.series[nuevo_nombre] = nuevo_capitulos
                    self.actualizar_listas()
                    self.data_manager.guardar_datos()

    def eliminar_serie(self):
        seleccion = self.series_listbox.curselection()
        if seleccion:
            serie = self.series_listbox.get(seleccion[0]).split(":")[0]
            if messagebox.askyesno("Eliminar Serie", f"¿Estás seguro de que quieres eliminar la serie {serie}?"):
                del self.data_manager.series[serie]
                self.actualizar_listas()
                self.data_manager.guardar_datos()

    def editar_fecha(self):
        seleccion = self.fechas_listbox.curselection()
        if seleccion:
            fecha = self.fechas_listbox.get(seleccion[0]).split(":")[0]
            nueva_fecha = simpledialog.askstring("Editar Fecha", f"Nueva fecha para {fecha}:", initialvalue=fecha)
            if nueva_fecha:
                color = colorchooser.askcolor(title="Elegir nuevo color", color=self.data_manager.fechas[fecha])[1]
                if color:
                    del self.data_manager.fechas[fecha]
                    self.data_manager.fechas[nueva_fecha] = color
                    self.actualizar_listas()
                    self.data_manager.guardar_datos()

    def eliminar_fecha(self):
        seleccion = self.fechas_listbox.curselection()
        if seleccion:
            fecha = self.fechas_listbox.get(seleccion[0]).split(":")[0]
            if messagebox.askyesno("Eliminar Fecha", f"¿Estás seguro de que quieres eliminar la fecha {fecha}?"):
                del self.data_manager.fechas[fecha]
                self.actualizar_listas()
                self.data_manager.guardar_datos()

    def search_series(self, event):
        search_term = self.search_entry.get().lower()
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Label) and widget.grid_info()['column'] == 0:
                if search_term in widget.cget('text').lower():
                    widget.grid()
                    widget.master.grid()
                else:
                    widget.grid_remove()
                    widget.master.grid_remove()
    
    def elegir_color(self):
        color = colorchooser.askcolor(title="Elegir color para la semana")
        if color[1]:
            self.color_label.config(background=color[1])
            self.color_label.config(text=color[1])
    
    def abrir_calendario(self):
        top = tk.Toplevel(self.root)
        cal = Calendar(top, selectmode='day', year=self.data_manager.ultima_fecha.year, month=self.data_manager.ultima_fecha.month, day=self.data_manager.ultima_fecha.day)
        cal.pack(pady=20)
        ttk.Button(top, text="OK", command=lambda: self.seleccionar_fecha(cal, top)).pack()

    def seleccionar_fecha(self, cal, top):
        fecha = cal.selection_get()
        self.data_manager.ultima_fecha = fecha
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=4)
        self.fecha_entry.config(state='normal')
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, f"{inicio_semana.strftime('%d/%m')} - {fin_semana.strftime('%d/%m')}")
        self.fecha_entry.config(state='readonly')
        top.destroy()
    
    def agregar_fecha(self):
        fecha = self.fecha_entry.get()
        color = self.color_label.cget("background")
        if fecha and color != "white":
            if messagebox.askyesno("Confirmar", f"¿Desea agregar la semana '{fecha}' con el color seleccionado?"):
                self.data_manager.fechas[fecha] = color
                self.actualizar_listas()
                self.fecha_entry.config(state='normal')
                self.fecha_entry.delete(0, tk.END)
                self.fecha_entry.config(state='readonly')
                self.color_label.config(background="white", text="       ")
                self.data_manager.guardar_datos()
        else:
            messagebox.showerror("Error", "Por favor, seleccione una semana válida y elija un color.")

    def iniciar_arrastre(self, event):
        if self.fecha_seleccionada or self.modo_finalizado:
            self.arrastrando = True
            self.pintar_capitulo(event.widget)
    
    def arrastrar(self, event):
        if self.arrastrando:
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if isinstance(widget, tk.Label) and widget.master == event.widget.master:
                self.pintar_capitulo(widget)
    
    def finalizar_arrastre(self, event):
        self.arrastrando = False
        self.data_manager.guardar_datos()
    
    def pintar_capitulo(self, widget):
        serie_nombre = self.scrollable_frame.grid_slaves(row=widget.master.grid_info()['row'], column=0)[0].cget('text')
        capitulo = f"{serie_nombre}_{widget.cget('text')}"
        
        if self.modo_finalizado:
            if capitulo not in self.data_manager.capitulos_finalizados:
                self.data_manager.capitulos_finalizados.add(capitulo)
                widget.config(bg='black', fg='white')
        elif self.fecha_seleccionada:
            color = self.data_manager.fechas[self.fecha_seleccionada]
            widget.config(bg=color)
            self.data_manager.capitulos_coloreados[capitulo] = color
            if capitulo in self.data_manager.capitulos_finalizados:
                self.data_manager.capitulos_finalizados.remove(capitulo)

    def seleccionar_fecha_asignacion(self, fecha):
        self.fecha_seleccionada = fecha
        self.modo_finalizado = False
        self.btn_finalizado.config(text="Marcar como Finalizado")
    
    def toggle_modo_finalizado(self):
        self.modo_finalizado = not self.modo_finalizado
        if self.modo_finalizado:
            self.fecha_seleccionada = None
            self.btn_finalizado.config(text="Desactivar Modo Finalizado")
        else:
            self.btn_finalizado.config(text="Marcar como Finalizado")

if __name__ == "__main__":
    print("Iniciando aplicación...")  # Depuración
    root = tk.Tk()
    app = GestorSeries(root)
    root.mainloop()
