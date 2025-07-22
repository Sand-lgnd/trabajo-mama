import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import trabajo_mama as fn_mime
import re # Para validación de fecha
from datetime import datetime # Para validación de fecha
from PIL import Image, ImageTk

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

        # --- Frames Principales ---
        # Frame para los botones de opciones (izquierda)
        options_outer_frame = ttk.Frame(self.root, padding="10")
        options_outer_frame.pack(side=tk.LEFT, fill=tk.Y)

        options_frame = ttk.LabelFrame(options_outer_frame, text="Menú de Opciones")
        options_frame.pack(expand=True, fill=tk.BOTH)

        # Frame para el área principal (entradas y resultados) (derecha)
        main_area_frame = ttk.Frame(self.root, padding="10")
        main_area_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Frame para entradas de parámetros (arriba en main_area_frame)
        self.input_frame = ttk.LabelFrame(main_area_frame, text="Parámetros de Consulta")
        self.input_frame.pack(fill=tk.X, pady=(0,10))

        # Frame para resultados (abajo en main_area_frame)
        marco_resultados = ttk.LabelFrame(main_area_frame, text="Resultados")
        marco_resultados.pack(expand=True, fill=tk.BOTH)

        self.texto_resultados = scrolledtext.ScrolledText(marco_resultados, wrap=tk.WORD, state=tk.DISABLED, height=10) 
        self.texto_resultados.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        boton_limpiar_resultados = ttk.Button(marco_resultados, text="Limpiar Resultados e Imagen", command=self.limpiar_area_resultados)
        boton_limpiar_resultados.pack(pady=5)

                # --- Botones de Opciones ---
        opciones = [
            (" Insertar nuevo movimiento", self.mostrar_entradas_op1),
            (" Obtener stock actual de un producto", self.mostrar_entradas_op2),
            (" Obtener detalles de entradas en un día", self.mostrar_entradas_op3),
            (" Obtener detalles de salidas en un día", self.mostrar_entradas_op4),
            (" Obtener el peso total que queda", self.mostrar_entradas_op5),
            (" Obtener detalles de movimientos en un día", self.mostrar_entradas_op6),
            (" Buscar stock por nombre de producto", self.mostrar_entradas_op7)
        ]
        for texto, comando in opciones:
            btn = ttk.Button(options_frame, text=texto, command=comando, width=40)
            btn.pack(pady=3, padx=5, fill=tk.X)
        
        # Botón de Salir
        btn_salir = ttk.Button(options_frame, text="Salir", command=self.root.quit)
        btn_salir.pack(pady=10, padx=5, fill=tk.X, side=tk.BOTTOM)
    
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
        ttk.Label(self.input_frame, text="Fecha del movimiento(YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_fecha_mov = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_fecha_mov.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.input_frame, text="Código del producto:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_id_prod = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_id_prod.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(self.input_frame, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op1_cantidad = ttk.Entry(self.input_frame, width=30)
        self.entrada_op1_cantidad.grid(row=3, column=1, padx=5, pady=5)
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
        verificar_prod = self._manejar_llamada_bd(fn_mime.obtener_detalles_producto, id_producto)
        if verificar_prod is None and not self.texto_resultados.get(1.0, tk.END).strip():
             self._mostrar_resultados_texto(f"Producto con ID '{id_producto}' no encontrado.")
             return
        elif verificar_prod is None:
            return
        
        movimiento_nuevo = self._manejar_llamada_bd(fn_mime.insertar_movimiento, tipo_mov, fecha_mov, id_producto, cantidad)
        if movimiento_nuevo is not None:
            self._mostrar_resultados_texto("Nuevo movimiento añadido")

    def mostrar_entradas_op2(self): 
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op2_id_prod = ttk.Entry(self.input_frame, width=30) 
        self.entrada_op2_id_prod.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op2).grid(row=1, column=0, columnspan=2, pady=10)

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
        if detalles_movimientos:
            texto_resultado = f"--- Detalles de Movimientos en {fecha} ---\n"
            for movimiento in detalles_movimientos:
                for i, nombre_columna in enumerate(COLUMN_NAMES_MOVIMIENTOS):
                    texto_resultado += f"  {nombre_columna}: {movimiento[i]}\n"
                texto_resultado += "-" * 20 + "\n"
            self._mostrar_resultados_texto(texto_resultado)
        elif isinstance(detalles_movimientos, list) and not detalles_movimientos:
            self._mostrar_resultados_texto(f"No se encontraron movimientos para la fecha {fecha}.")

    def mostrar_entradas_op7(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Nombre del Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_op7_nombre = ttk.Entry(self.input_frame, width=40)
        self.entrada_op7_nombre.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_op7_nombre.bind("<KeyRelease>", self.actualizar_sugerencias_productos)

        self.sugerencias_listbox = tk.Listbox(self.input_frame, width=40, height=5)
        self.sugerencias_listbox.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.sugerencias_listbox.bind("<<ListboxSelect>>", self.seleccionar_sugerencia_producto)

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





