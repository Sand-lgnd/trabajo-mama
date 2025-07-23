import mysql.connector
from typing import List, Tuple, Any, Optional
# Variables globales para la información de conexión (modificables si es necesario)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Pata2021."
DB_NAME = "BD_mama"
class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos."""
    pass
def conexion_BD():
    """Establece la conexión con la base de datos."""
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME)
        return conexion
    except mysql.connector.Error as err:
        # En lugar de imprimir, lanzamos una excepción que la GUI puede capturar
        raise DatabaseError(f"Conexión con la BD fallida: {err}")

def ejecutar_query(query_string: str, params: Optional[tuple] = None) -> Optional[List[Tuple[Any, ...]]]:
    """Ejecuta una consulta SQL y devuelve los resultados.
    Lanza DatabaseError en caso de problemas."""
    conexion = None
    try:
        conexion = conexion_BD()
        cursor = conexion.cursor()
        cursor.execute(query_string, params)
        results = cursor.fetchall()
        # Para operaciones que no devuelven resultados (INSERT, UPDATE, DELETE),
        # fetchall() devuelve una lista vacía.
        # Si es una operación como COMMIT o ROLLBACK, puede no haber resultados.
        # Para SELECT, devuelve las filas.
        # Si la query es de modificación (INSERT, UPDATE, DELETE), necesitamos hacer commit.
        # Esto es una simplificación; idealmente, se manejaría de forma más explícita.
        if query_string.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            conexion.commit()
            # Para estas operaciones, podríamos querer devolver el número de filas afectadas.
            return cursor.rowcount
        return results
        
    except mysql.connector.Error as err:
        # En lugar de imprimir, lanzamos una excepción
        raise DatabaseError(f"Error al ejecutar el query: {err}\nQuery: {query_string}\nParams: {params}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_detalles_producto(product_id: str):
    query = "SELECT * FROM producto WHERE id_prod = %s;"
    resultado = ejecutar_query(query, (product_id,))
    if resultado and len(resultado) > 0:
        return resultado[0] 
    return None

def producto_existe(id_prod: str) -> bool:
    """Verifica si un producto existe en la base de datos."""
    return obtener_detalles_producto(id_prod) is not None

def insertar_movimiento(tipo_mov, fecha, id_prod, cantidad):
    if not producto_existe(id_prod):
        raise DatabaseError(f"El producto con ID '{id_prod}' no existe.")

    cantidad_int = int(cantidad)
    if tipo_mov == 'S':
        stock_actual = obtener_stock(id_prod)
        if stock_actual < cantidad_int:
            raise DatabaseError(f"Stock insuficiente para el producto ID '{id_prod}'. Stock actual: {stock_actual}, Salida solicitada: {cantidad}.")

    query= "INSERT INTO movimiento (tipo_mov, fecha_mov, id_prod, cantidad) VALUES (%s, %s, %s, %s)"
    return ejecutar_query(query, (tipo_mov, fecha, id_prod, cantidad_int))

def obtener_stock (id_prod):
    query = """
    SELECT SUM(CASE tipo_mov
                  WHEN 'E' THEN cantidad 
                  WHEN 'S' THEN -cantidad 
               END) as stock_actual
    FROM movimiento 
    WHERE id_prod = %s;
    """
    resultado = ejecutar_query(query, (id_prod,))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def obtener_detalles_entradas_en_un_dia(specific_date: str) -> List[Tuple[Any, ...]]:
    query = """
    SELECT p.producto, m.tipo_mov, m.id_prod, m.cantidad 
    FROM movimiento m
    JOIN producto p on m.id_prod = p.id_prod
    WHERE m.tipo_mov = 'E' AND m.fecha_mov = %s;
    """
    resultados = ejecutar_query(query, (specific_date,))
    if resultados:
        return resultados
    return []

def obtener_stock_todos_los_productos():
    """
    Obtiene el stock actual y los detalles de todos los productos.
    """
    query = """
    SELECT
        p.id_prod,
        p.producto,
        COALESCE(SUM(CASE m.tipo_mov
            WHEN 'E' THEN m.cantidad
            WHEN 'S' THEN -m.cantidad
        END), 0) AS stock_actual,
        p.peso,
        (COALESCE(SUM(CASE m.tipo_mov
            WHEN 'E' THEN m.cantidad
            WHEN 'S' THEN -m.cantidad
        END), 0) * p.peso) AS peso_total_actual
    FROM producto p
    LEFT JOIN movimiento m ON p.id_prod = m.id_prod
    GROUP BY p.id_prod, p.producto, p.peso
    ORDER BY p.producto;
    """
    return ejecutar_query(query)

def añadir_producto(id_prod: str, nombre: str, peso: float):
    """
    Añade un nuevo producto a la base de datos.
    """
    query = "INSERT INTO producto (id_prod, producto, peso) VALUES (%s, %s, %s);"
    params = (id_prod, nombre, peso)
    return ejecutar_query(query, params)

def eliminar_producto(id_prod: str):
    """
    Elimina un producto de la base de datos.
    """
    query = "DELETE FROM producto WHERE id_prod = %s;"
    params = (id_prod,)
    return ejecutar_query(query, params)

def insertar_movimientos_multiples(movimientos: List[Tuple[str, str, str, int]]):
    """
    Inserta una lista de movimientos en la base de datos usando una transacción.
    Valida la existencia del producto y el stock antes de insertar.
    """
    conexion = None
    try:
        conexion = conexion_BD()
        cursor = conexion.cursor()

        # Validar todos los movimientos antes de intentar insertar
        for tipo_mov, _, id_prod, cantidad in movimientos:
            if not producto_existe(id_prod):
                raise DatabaseError(f"El producto con ID '{id_prod}' no existe. Operación cancelada.")
            if tipo_mov == 'S':
                stock_actual = obtener_stock(id_prod)
                if stock_actual < cantidad:
                    raise DatabaseError(f"Stock insuficiente para '{id_prod}'. Stock: {stock_actual}, Solicitado: {cantidad}. Operación cancelada.")

        query = "INSERT INTO movimiento (tipo_mov, fecha_mov, id_prod, cantidad) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, movimientos)

        conexion.commit()
        return cursor.rowcount

    except mysql.connector.Error as err:
        if conexion:
            conexion.rollback()
        raise DatabaseError(f"Error al insertar múltiples movimientos: {err}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_detalles_salidas_en_un_dia(specific_date: str) -> List[Tuple[Any, ...]]:
    query = """
    SELECT p.producto, m.tipo_mov, m.id_prod, m.cantidad 
    FROM movimiento m
    JOIN producto p on m.id_prod = p.id_prod
    WHERE m.tipo_mov = 'S' AND m.fecha_mov = %s;
    """
    resultados = ejecutar_query(query, (specific_date,))
    if resultados:
        return resultados
    return []

def obtener_peso_total(id_prod):
    query = """
    SELECT 
        p.peso,
        COALESCE(SUM(CASE m.tipo_mov
            WHEN 'E' THEN m.cantidad
            WHEN 'S' THEN -m.cantidad
        END), 0) AS stock_actual,
        COALESCE(SUM(CASE m.tipo_mov
            WHEN 'E' THEN m.cantidad
            WHEN 'S' THEN -m.cantidad
        END), 0) * p.peso AS peso_total_actual
    FROM producto p
    LEFT JOIN movimiento m ON p.id_prod = m.id_prod
    WHERE p.id_prod = %s;
    """
    resultado = ejecutar_query(query, (id_prod,))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return float(resultado[0][0])
    return

def obtener_detalles_movimientos_en_un_dia(specific_date: str) -> List[Tuple[Any, ...]]:
    """
    Obtiene todos los movimientos (entradas y salidas) para una fecha específica.
    """
    query = """
    SELECT p.producto, m.tipo_mov, m.id_prod, m.cantidad 
    FROM movimiento m
    JOIN producto p on m.id_prod = p.id_prod
    WHERE m.fecha_mov = %s;
    """
    resultados = ejecutar_query(query, (specific_date,))
    if resultados:
        return resultados
    return []

def buscar_producto_por_nombre(search_term: str) -> List[Tuple[Any, ...]]:
    """
    Busca productos por su nombre utilizando un término de búsqueda.
    """
    query = "SELECT id_prod, producto, peso FROM producto WHERE producto LIKE %s;"
    # Añadimos los comodines '%' para la búsqueda LIKE
    params = (f"%{search_term}%",)
    resultados = ejecutar_query(query, params)
    if resultados:
        return resultados
    return []