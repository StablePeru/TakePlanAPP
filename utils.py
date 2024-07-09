import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import timedelta

def abrir_calendario(parent, ultima_fecha):
    top = tk.Toplevel(parent)
    cal = Calendar(top, selectmode='day', year=ultima_fecha.year, month=ultima_fecha.month, day=ultima_fecha.day)
    cal.pack(pady=20)
    ttk.Button(top, text="OK", command=lambda: seleccionar_fecha(cal, top, parent)).pack()

def seleccionar_fecha(cal, top, parent):
    fecha = cal.selection_get()
    parent.ultima_fecha = fecha
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=4)  # Lunes a Viernes
    parent.fecha_entry.config(state='normal')
    parent.fecha_entry.delete(0, tk.END)
    parent.fecha_entry.insert(0, f"{inicio_semana.strftime('%d/%m')} - {fin_semana.strftime('%d/%m')}")
    parent.fecha_entry.config(state='readonly')
    top.destroy()