import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import trabajo_mama as fn_mime
import re # Para validación de fecha
from datetime import datetime # Para validación de fecha
from PIL import Image, ImageTk
from openpyxl import Workbook

# Constantes para nombres de columnas
COLUMN_NAMES_PRODUCTO = ["Código del Producto", "Nombre", "Peso"]
COLUMN_NAMES_MOVIMIENTOS = ["Nombre","Tipo de Movimiento", "Código del Producto", "Cantidad"]

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Entradas y Salidas")
        self.root.geometry("900x700") # Tamaño inicial

        # Aplicar un tema de ttk 
        style = ttk.Style()
        style.theme_use("vista")

        # --- Menú Superior ---
        self.crear_menu_superior()

        # --- Frames Principales ---
        # Frame para el área principal (entradas y resultados)
        main_area_frame = ttk.Frame(self.root, padding="10")
        main_area_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Frame para entradas de parámetros (arriba en main_area_frame)
        self.input_frame = ttk.LabelFrame(main_area_frame, text="Parámetros de Consulta")
        self.input_frame.pack(fill=tk.X, pady=(0,10))

        # Frame para resultados (abajo en main_area_frame)
        marco_resultados = ttk.LabelFrame(main_area_frame, text="Resultados")
        marco_resultados.pack(expand=True, fill=tk.BOTH)

        self.texto_resultados = scrolledtext.ScrolledText(marco_resultados, wrap=tk.WORD, state=tk.DISABLED, height=10) 
        self.texto_resultados.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        boton_limpiar_resultados = ttk.Button(marco_resultados, text="Limpiar Resultados", command=self.limpiar_area_resultados)
        boton_limpiar_resultados.pack(pady=5)
    
    def _clear_input_frame(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

    def _mostrar_resultados_texto(self, contenido: str):
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, contenido)
        self.texto_resultados.config(state=tk.DISABLED)

    def limpiar_area_resultados(self):
        self._mostrar_resultados_texto("")

    def _manejar_llamada_bd(self, funcion_db, *args):
        # No limpiar la imagen aquí, solo el texto. La limpieza de imagen es más selectiva.
        try:
            return funcion_db(*args)
        except fn_mime.DatabaseError as e:
            messagebox.showerror("Error de Base de Datos", str(e))
            self._mostrar_resultados_texto(f"Error de Base de Datos:\n{e}")
            return None
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e}")
            self._mostrar_resultados_texto(f"Error Inesperado:\n{e}")
            return None

    def _validate_date_format(self, date_string: str) -> bool:
        """Valida que el string de fecha esté en formato YYYY-MM-DD."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_string):
            return False
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def mostrar_entradas_op1(self): 
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Tipo de movimiento (E o S):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_tipo_mov = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_tipo_mov.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op1_tipo_mov.bind("<Return>", lambda event: self.ejecutar_op1())
        ttk.Label(self.input_frame, text="Fecha del movimiento(YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_fecha_mov = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_fecha_mov.grid(row=1, column=1, padx=5, pady=5)
        self.entrada_op1_fecha_mov.bind("<Return>", lambda event: self.ejecutar_op1())
        ttk.Label(self.input_frame, text="Código del producto:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_id_prod = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_id_prod.grid(row=2, column=1, padx=5, pady=5)
        self.entrada_op1_id_prod.bind("<Return>", lambda event: self.ejecutar_op1())
        ttk.Label(self.input_frame, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_cantidad = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_cantidad.grid(row=3, column=1, padx=5, pady=5)
        self.entrada_op1_cantidad.bind("<Return>", lambda event: self.ejecutar_op1())
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op1).grid(row=4, column=0, columnspan=2, pady=10)

    def ejecutar_op1(self):
        tipo_mov= self.entrada_op1_tipo_mov.get()
        fecha_mov = self.entrada_op1_fecha_mov.get()
        id_producto = self.entrada_op1_id_prod.get()
        cantidad = self.entrada_op1_cantidad.get() 
        if not id_producto or not tipo_mov or not fecha_mov or not cantidad:
            messagebox.showwarning("Entrada Inválida", "Por favor, asegúrese que todos los campos estén llenos.")
            return
        
        self.limpiar_area_resultados()
        try:
            movimiento_nuevo = self._manejar_llamada_bd(fn_mime.insertar_movimiento, tipo_mov, fecha_mov, id_producto, cantidad)
            if movimiento_nuevo is not None:
                self._mostrar_resultados_texto("Nuevo movimiento añadido con éxito.")
        except fn_mime.DatabaseError as e:
            messagebox.showerror("Error al Guardar", str(e))

    def mostrar_entradas_op2(self):
        self._clear_input_frame()

        # Obtener todos los productos para el Combobox
        productos = self._manejar_llamada_bd(fn_mime.obtener_stock_todos_los_productos)
        self.productos_map = {f"{p[1]} (ID: {p[0]})": p[0] for p in productos} if productos else {}

        ttk.Label(self.input_frame, text="Seleccionar Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_productos = ttk.Combobox(self.input_frame, values=list(self.productos_map.keys()), width=40)
        self.combo_productos.grid(row=0, column=1, padx=5, pady=5)
        self.combo_productos.bind("<<ComboboxSelected>>", self.seleccionar_producto_combo)

        ttk.Label(self.input_frame, text="O buscar por ID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op2_id_prod = ttk.Entry(self.input_frame, width=30)
        self.entrada_op2_id_prod.grid(row=1, column=1, padx=5, pady=5)
        self.entrada_op2_id_prod.bind("<Return>", lambda event: self.ejecutar_op2())

        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op2).grid(row=2, column=0, columnspan=2, pady=10)

    def seleccionar_producto_combo(self, event):
        seleccion = self.combo_productos.get()
        if seleccion in self.productos_map:
            self.entrada_op2_id_prod.delete(0, tk.END)
            self.entrada_op2_id_prod.insert(0, self.productos_map[seleccion])

    def ejecutar_op2(self): 
        id_producto = self.entrada_op2_id_prod.get()
        if not id_producto:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un ID de Producto.")
            return
        
        self.limpiar_area_resultados()
        producto_existe = self._manejar_llamada_bd(fn_mime.obtener_detalles_producto, id_producto)

        if producto_existe is None and not self.texto_resultados.get(1.0, tk.END).strip():
             self._mostrar_resultados_texto(f"Producto con ID '{id_producto}' no encontrado.")
             return
        elif producto_existe is None: 
            return

        stock = self._manejar_llamada_bd(fn_mime.obtener_stock, id_producto)
        if stock is not None: 
            self._mostrar_resultados_texto(f"Stock general actual del producto {producto_existe[1]}: {stock} ")

    def mostrar_entradas_op3(self): 
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Fecha(YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op3_fecha = ttk.Entry(self.input_frame, width=30)
        self.entrada_op3_fecha.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op3_fecha.bind("<Return>", lambda event: self.ejecutar_op3())
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op3).grid(row=1, column=0, columnspan=2, pady=10)

    def ejecutar_op3(self): 
        fecha = self.entrada_op3_fecha.get()
        if not fecha:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una fecha.")
            return
        if not self._validate_date_format(fecha):
            messagebox.showwarning("Formato Inválido", "El formato de fecha debe ser YYYY-MM-DD.")

        self.limpiar_area_resultados()
        detalles_entradas = self._manejar_llamada_bd(fn_mime.obtener_detalles_entradas_en_un_dia, fecha)
        if detalles_entradas:
            texto_resultado = f"--- Detalles de Entradas en {fecha} ---\n"
            for entrada in detalles_entradas:
                for i, nombre_columna in enumerate(COLUMN_NAMES_MOVIMIENTOS):
                    texto_resultado += f"  {nombre_columna}: {entrada[i]}\n"
                texto_resultado += "-" * 20 + "\n"
            self._mostrar_resultados_texto(texto_resultado)
        elif isinstance(detalles_entradas, list) and not detalles_entradas:
            self._mostrar_resultados_texto(f"No se encontraron entradas para la fecha {fecha}.")

    def mostrar_entradas_op4(self): 
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Fecha(YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op4_fecha = ttk.Entry(self.input_frame, width=30)
        self.entrada_op4_fecha.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op4_fecha.bind("<Return>", lambda event: self.ejecutar_op4())
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op4).grid(row=1, column=0, columnspan=2, pady=10)

    def ejecutar_op4(self): 
        fecha = self.entrada_op4_fecha.get() 
        if not fecha:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una fecha.")
            return
        if not self._validate_date_format(fecha):
            messagebox.showwarning("Formato Inválido", "El formato de fecha debe ser YYYY-MM-DD.")
            return

        self.limpiar_area_resultados()
        detalles_salidas = self._manejar_llamada_bd(fn_mime.obtener_detalles_salidas_en_un_dia, fecha)
        if detalles_salidas:
            texto_resultado = f"--- Detalles de Salidas en {fecha} ---\n"
            for salida in detalles_salidas:
                for i, nombre_columna in enumerate(COLUMN_NAMES_MOVIMIENTOS):
                     texto_resultado += f"  {nombre_columna}: {salida[i]}\n"
                texto_resultado += "-" * 20 + "\n"
            self._mostrar_resultados_texto(texto_resultado)
        elif isinstance(detalles_salidas, list) and not detalles_salidas:
            self._mostrar_resultados_texto(f"No se encontraron salidas para la fecha {fecha}.")

    def mostrar_entradas_op5(self): 
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op5_id_prod = ttk.Entry(self.input_frame, width=30) 
        self.entrada_op5_id_prod.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op5_id_prod.bind("<Return>", lambda event: self.ejecutar_op5())
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op5).grid(row=1, column=0, columnspan=2, pady=10)

    def ejecutar_op5(self): 
        id_producto = self.entrada_op5_id_prod.get()
        if not id_producto:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un Código.")
            return
        
        self.limpiar_area_resultados()
        producto_existe = self._manejar_llamada_bd(fn_mime.obtener_detalles_producto, id_producto)

        if producto_existe is None and not self.texto_resultados.get(1.0, tk.END).strip():
             self._mostrar_resultados_texto(f"Producto con código'{id_producto}' no encontrado.")
             return
        elif producto_existe is None: 
            return

        stock = self._manejar_llamada_bd(fn_mime.obtener_peso_total, id_producto)
        if stock is not None: 
            self._mostrar_resultados_texto(f"Peso total en existencia del producto:{producto_existe[1]}: {stock} ")

    def mostrar_entradas_op6(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op6_fecha = ttk.Entry(self.input_frame, width=30)
        self.entrada_op6_fecha.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op6_fecha.bind("<Return>", lambda event: self.ejecutar_op6())
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op6).grid(row=1, column=0, columnspan=2, pady=10)

    def ejecutar_op6(self):
        fecha = self.entrada_op6_fecha.get()
        if not fecha:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una fecha.")
            return
        if not self._validate_date_format(fecha):
            messagebox.showwarning("Formato Inválido", "El formato de fecha debe ser YYYY-MM-DD.")
            return

        self.limpiar_area_resultados()
        detalles_movimientos = self._manejar_llamada_bd(fn_mime.obtener_detalles_movimientos_en_un_dia, fecha)

        # Limpiar resultados anteriores y preparar para paginación
        self._clear_input_frame() # Limpia el frame de parámetros para mostrar los resultados paginados
        self.mostrar_resultados_paginados(detalles_movimientos, f"Detalles de Movimientos en {fecha}")

    def mostrar_resultados_paginados(self, resultados, titulo, page_size=10):
        self.limpiar_area_resultados()
        self.input_frame.config(text=titulo) # Reutilizamos el input_frame para mostrar el título

        if not resultados:
            self._mostrar_resultados_texto(f"No se encontraron resultados.")
            return

        self.current_page = 0
        self.resultados = resultados
        self.page_size = page_size
        self.total_pages = (len(self.resultados) + self.page_size - 1) // self.page_size

        # Frame para los controles de paginación
        pagination_controls = ttk.Frame(self.input_frame)
        pagination_controls.pack(pady=5)

        self.prev_button = ttk.Button(pagination_controls, text="<< Anterior", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = ttk.Label(pagination_controls, text=f"Página {self.current_page + 1} de {self.total_pages}")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(pagination_controls, text="Siguiente >>", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.show_page()

    def show_page(self):
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size
        page_resultados = self.resultados[start_index:end_index]

        texto_resultado = ""
        # Adaptamos la visualización dependiendo de los datos que recibimos
        if len(page_resultados[0]) == len(COLUMN_NAMES_MOVIMIENTOS): # Es una lista de movimientos
            for item in page_resultados:
                for i, nombre_columna in enumerate(COLUMN_NAMES_MOVIMIENTOS):
                    texto_resultado += f"  {nombre_columna}: {item[i]}\n"
                texto_resultado += "-" * 20 + "\n"
        else: # Es una lista de stock de productos
            cabeceras = ["ID", "Nombre", "Stock", "Peso Unit.", "Peso Total"]
            for item in page_resultados:
                for i, cabecera in enumerate(cabeceras):
                    texto_resultado += f"  {cabecera}: {item[i]}\n"
                texto_resultado += "-" * 20 + "\n"
        self._mostrar_resultados_texto(texto_resultado)

        # Actualizar estado de los botones
        self.page_label.config(text=f"Página {self.current_page + 1} de {self.total_pages}")
        self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()

    def mostrar_entradas_op7(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Nombre del Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op7_nombre = ttk.Entry(self.input_frame, width=40)
        self.entrada_op7_nombre.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op7_nombre.bind("<KeyRelease>", self.actualizar_sugerencias_productos)

        self.sugerencias_listbox = tk.Listbox(self.input_frame, width=40, height=5, selectbackground="#cce5ff")
        self.sugerencias_listbox.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.sugerencias_listbox.bind("<<ListboxSelect>>", self.seleccionar_sugerencia_producto)
        self.sugerencias_listbox.bind("<Motion>", self.resaltar_sugerencia)

        ttk.Button(self.input_frame, text="Buscar Stock", command=self.ejecutar_op7).grid(row=2, column=0, columnspan=2, pady=10)
        self.producto_seleccionado = None

    def actualizar_sugerencias_productos(self, event):
        termino_busqueda = self.entrada_op7_nombre.get()
        if len(termino_busqueda) < 2:
            self.sugerencias_listbox.delete(0, tk.END)
            return

        productos = self._manejar_llamada_bd(fn_mime.buscar_producto_por_nombre, termino_busqueda)
        self.sugerencias_listbox.delete(0, tk.END)
        if productos:
            self.productos_sugeridos = {p[1]: p for p in productos} # Mapear nombre a tupla de producto
            for nombre_producto in self.productos_sugeridos.keys():
                self.sugerencias_listbox.insert(tk.END, nombre_producto)

    def seleccionar_sugerencia_producto(self, event):
        seleccion = self.sugerencias_listbox.curselection()
        if seleccion:
            nombre_producto = self.sugerencias_listbox.get(seleccion[0])
            self.entrada_op7_nombre.delete(0, tk.END)
            self.entrada_op7_nombre.insert(0, nombre_producto)
            self.producto_seleccionado = self.productos_sugeridos[nombre_producto]
            self.sugerencias_listbox.delete(0, tk.END) # Ocultar lista

    def resaltar_sugerencia(self, event):
        index = self.sugerencias_listbox.index(f"@{event.x},{event.y}")
        if index != self.sugerencias_listbox.curselection():
            self.sugerencias_listbox.selection_clear(0, tk.END)
            self.sugerencias_listbox.selection_set(index)
            self.sugerencias_listbox.activate(index)

    def mostrar_stock_total(self):
        self._clear_input_frame()
        self.limpiar_area_resultados()

        stock_total = self._manejar_llamada_bd(fn_mime.obtener_stock_todos_los_productos)

        if stock_total:
            # Reutilizamos la función de paginación
            self.mostrar_resultados_paginados(stock_total, "Stock de Todos los Productos")
        else:
            self._mostrar_resultados_texto("No hay productos en el inventario.")

    def ejecutar_op7(self):
        if not self.producto_seleccionado:
            messagebox.showwarning("Entrada Inválida", "Por favor, seleccione un producto de la lista.")
            return

        id_producto = self.producto_seleccionado[0]
        nombre_producto = self.producto_seleccionado[1]
        self.limpiar_area_resultados()

        stock = self._manejar_llamada_bd(fn_mime.obtener_stock, id_producto)
        if stock is not None:
            self._mostrar_resultados_texto(f"Stock actual de '{nombre_producto}' (ID: {id_producto}): {stock}")
        else:
            self._mostrar_resultados_texto(f"No se pudo obtener el stock para '{nombre_producto}'.")

    def mostrar_entradas_op8(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op8_id = ttk.Entry(self.input_frame, width=30)
        self.entrada_op8_id.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op8_id.bind("<Return>", lambda event: self.ejecutar_op8())

        ttk.Label(self.input_frame, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op8_nombre = ttk.Entry(self.input_frame, width=30)
        self.entrada_op8_nombre.grid(row=1, column=1, padx=5, pady=5)
        self.entrada_op8_nombre.bind("<Return>", lambda event: self.ejecutar_op8())

        ttk.Label(self.input_frame, text="Peso:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op8_peso = ttk.Entry(self.input_frame, width=30)
        self.entrada_op8_peso.grid(row=2, column=1, padx=5, pady=5)
        self.entrada_op8_peso.bind("<Return>", lambda event: self.ejecutar_op8())

        ttk.Button(self.input_frame, text="Añadir", command=self.ejecutar_op8).grid(row=3, column=0, columnspan=2, pady=10)

    def ejecutar_op8(self):
        id_prod = self.entrada_op8_id.get()
        nombre = self.entrada_op8_nombre.get()
        peso_str = self.entrada_op8_peso.get()

        if not id_prod or not nombre or not peso_str:
            messagebox.showwarning("Entrada Inválida", "Todos los campos son obligatorios.")
            return

        try:
            peso = float(peso_str)
        except ValueError:
            messagebox.showwarning("Entrada Inválida", "El peso debe ser un número.")
            return

        resultado = self._manejar_llamada_bd(fn_mime.añadir_producto, id_prod, nombre, peso)
        if resultado is not None:
            self._mostrar_resultados_texto(f"Producto '{nombre}' añadido con éxito.")

    def mostrar_entradas_op9(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto a Eliminar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op9_id = ttk.Entry(self.input_frame, width=30)
        self.entrada_op9_id.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op9_id.bind("<Return>", lambda event: self.ejecutar_op9())
        ttk.Button(self.input_frame, text="Eliminar", command=self.ejecutar_op9).grid(row=1, column=0, columnspan=2, pady=10)

    def ejecutar_op9(self):
        id_prod = self.entrada_op9_id.get()
        if not id_prod:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un ID de producto.")
            return

        if not messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar el producto con ID '{id_prod}'? Esta acción no se puede deshacer."):
            return

        resultado = self._manejar_llamada_bd(fn_mime.eliminar_producto, id_prod)
        if resultado is not None:
            if resultado > 0:
                self._mostrar_resultados_texto(f"Producto con ID '{id_prod}' eliminado con éxito.")
            else:
                self._mostrar_resultados_texto(f"No se encontró ningún producto con el ID '{id_prod}'.")


    def mostrar_entradas_op10(self):
        self._clear_input_frame()
        self.movimientos_entries = []

        # Fecha unificada para todos los movimientos
        ttk.Label(self.input_frame, text="Fecha para todos los movimientos (YYYY-MM-DD):").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.fecha_multi_mov = ttk.Entry(self.input_frame, width=30)
        self.fecha_multi_mov.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

        # Frame para las filas de movimientos
        self.movimientos_frame = ttk.Frame(self.input_frame)
        self.movimientos_frame.grid(row=1, column=0, columnspan=5, pady=10)

        # Botones de control
        controles_frame = ttk.Frame(self.input_frame)
        controles_frame.grid(row=2, column=0, columnspan=5)
        ttk.Button(controles_frame, text="Añadir Movimiento", command=self.añadir_fila_movimiento).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="Guardar Todo", command=self.ejecutar_op10).pack(side=tk.LEFT, padx=5)

        self.añadir_fila_movimiento() # Añadir la primera fila por defecto

    def añadir_fila_movimiento(self):
        row_index = len(self.movimientos_entries)
        fila_frame = ttk.Frame(self.movimientos_frame)
        fila_frame.pack(pady=2, fill=tk.X)

        # Widgets para una fila de movimiento
        ttk.Label(fila_frame, text="Tipo (E/S):").pack(side=tk.LEFT, padx=5)
        tipo_mov = ttk.Combobox(fila_frame, values=["E", "S"], width=5)
        tipo_mov.pack(side=tk.LEFT, padx=5)

        ttk.Label(fila_frame, text="ID Producto:").pack(side=tk.LEFT, padx=5)
        id_prod = ttk.Entry(fila_frame, width=15)
        id_prod.pack(side=tk.LEFT, padx=5)

        ttk.Label(fila_frame, text="Cantidad:").pack(side=tk.LEFT, padx=5)
        cantidad = ttk.Entry(fila_frame, width=10)
        cantidad.pack(side=tk.LEFT, padx=5)

        btn_eliminar = ttk.Button(fila_frame, text="X", width=3, command=lambda f=fila_frame: self.eliminar_fila_movimiento(f))
        btn_eliminar.pack(side=tk.RIGHT, padx=5)

        # Guardar las entradas para poder leer sus valores después
        self.movimientos_entries.append((fila_frame, tipo_mov, id_prod, cantidad))

    def eliminar_fila_movimiento(self, frame_a_eliminar):
        # Encontrar el frame y los widgets asociados para eliminarlos
        for i, (frame, _, _, _) in enumerate(self.movimientos_entries):
            if frame == frame_a_eliminar:
                frame.destroy()
                self.movimientos_entries.pop(i)
                break

    def ejecutar_op10(self):
        fecha = self.fecha_multi_mov.get()
        if not self._validate_date_format(fecha):
            messagebox.showwarning("Fecha Inválida", "Por favor, ingrese una fecha válida (YYYY-MM-DD) para todos los movimientos.")
            return

        movimientos_para_db = []
        for _, tipo_mov_entry, id_prod_entry, cantidad_entry in self.movimientos_entries:
            tipo_mov = tipo_mov_entry.get()
            id_prod = id_prod_entry.get()
            cantidad_str = cantidad_entry.get()

            if not all([tipo_mov, id_prod, cantidad_str]):
                continue # Ignorar filas vacías

            if tipo_mov not in ["E", "S"]:
                messagebox.showwarning("Dato Inválido", f"El tipo de movimiento '{tipo_mov}' no es válido. Use 'E' o 'S'.")
                return

            try:
                cantidad = int(cantidad_str)
            except ValueError:
                messagebox.showwarning("Dato Inválido", f"La cantidad '{cantidad_str}' debe ser un número entero.")
                return

            movimientos_para_db.append((tipo_mov, fecha, id_prod, cantidad))

        if not movimientos_para_db:
            messagebox.showinfo("Nada que Guardar", "No hay movimientos para guardar.")
            return

        if not messagebox.askyesno("Confirmar Inserción", f"¿Está seguro de que desea insertar {len(movimientos_para_db)} movimientos con fecha {fecha}?"):
            return

        try:
            resultado = self._manejar_llamada_bd(fn_mime.insertar_movimientos_multiples, movimientos_para_db)
            if resultado is not None:
                self._mostrar_resultados_texto(f"Se han insertado {resultado} movimientos con éxito.")
                self.mostrar_entradas_op10()
        except fn_mime.DatabaseError as e:
            messagebox.showerror("Error al Guardar", str(e))


    def crear_menu_superior(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Exportar Stock a Excel", command=self.exportar_stock_excel)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)

        # Menú Editar
        editar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=editar_menu)
        editar_menu.add_command(label="Añadir Producto", command=self.mostrar_entradas_op8)
        editar_menu.add_command(label="Eliminar Producto", command=self.mostrar_entradas_op9)

        # Menú Movimientos
        movimientos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Movimientos", menu=movimientos_menu)
        movimientos_menu.add_command(label="Insertar Movimiento Único", command=self.mostrar_entradas_op1)
        movimientos_menu.add_command(label="Insertar Múltiples Movimientos", command=self.mostrar_entradas_op10)

        # Menú Consultas
        consultas_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Consultas", menu=consultas_menu)
        consultas_menu.add_command(label="Stock Actual por ID", command=self.mostrar_entradas_op2)
        consultas_menu.add_command(label="Stock por Nombre de Producto", command=self.mostrar_entradas_op7)
        consultas_menu.add_command(label="Ver Stock de Todos los Productos", command=self.mostrar_stock_total)
        consultas_menu.add_command(label="Peso Total Restante", command=self.mostrar_entradas_op5)
        consultas_menu.add_separator()
        consultas_menu.add_command(label="Detalles de Entradas en un Día", command=self.mostrar_entradas_op3)
        consultas_menu.add_command(label="Detalles de Salidas en un Día", command=self.mostrar_entradas_op4)
        consultas_menu.add_command(label="Todos los Movimientos en un Día", command=self.mostrar_entradas_op6)

    def exportar_stock_excel(self):
        """
        Obtiene el stock de todos los productos y lo exporta a un archivo Excel.
        """
        productos = self._manejar_llamada_bd(fn_mime.obtener_stock_todos_los_productos)

        if not productos:
            messagebox.showinfo("Nada que Exportar", "No hay productos en la base de datos para exportar.")
            return

        # Pedir al usuario que elija la ubicación del archivo
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar Reporte de Stock"
        )

        if not filepath:
            # El usuario canceló el diálogo
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Reporte de Stock"

            # Escribir las cabeceras
            cabeceras = ["ID Producto", "Nombre", "Stock Actual", "Peso Unitario (kg)", "Peso Total (kg)"]
            ws.append(cabeceras)

            # Escribir los datos de los productos
            for producto in productos:
                ws.append(producto)

            wb.save(filepath)
            messagebox.showinfo("Exportación Exitosa", f"El reporte de stock ha sido guardado en:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error al Exportar", f"Ocurrió un error al guardar el archivo de Excel:\n{e}")


if __name__ == "__main__":
    try:
        conn_test = fn_mime.mysql.connector.connect(
            host=fn_mime.DB_HOST,
            user=fn_mime.DB_USER,
            password=fn_mime.DB_PASSWORD,
            database=fn_mime.DB_NAME,
            connection_timeout=5
        )
        conn_test.close()

        app_root = tk.Tk()
        app = InventarioApp(app_root)
        app_root.mainloop()

    except fn_mime.mysql.connector.Error as err:
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Error Crítico de Conexión",
                             f"No se pudo conectar a la base de datos '{fn_mime.DB_NAME}' en {fn_mime.DB_HOST}.\n"
                             f"Verifique que el servidor MySQL esté en ejecución y las credenciales sean correctas.\n\n"
                             f"Detalle: {err}")
        error_root.destroy()
    except Exception as e:
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Error Inesperado al Iniciar",
                             f"Ocurrió un error inesperado al iniciar la aplicación: {e}")
        error_root.destroy()





