# Instrucciones para crear el ejecutable

Este proyecto utiliza Python y Tkinter para la interfaz gráfica, y se conecta a una base de datos MySQL. Sigue estos pasos para generar el archivo ejecutable.

## Requisitos previos

1.  **Python instalado**: Asegúrate de tener Python 3.x instalado en tu sistema.
2.  **MySQL Server**: Debes tener un servidor MySQL funcionando con la base de datos y tablas configuradas según el archivo `tablas.sql`.
3.  **Credenciales de Base de Datos**: Verifica las credenciales (host, usuario, contraseña) en el archivo `trabajo_mama.py`.

## Pasos para crear el ejecutable

### 1. Instalar las dependencias

Abre una terminal en la carpeta del proyecto y ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install -r requirements.txt
```

### 2. Generar el ejecutable con PyInstaller

Para crear un único archivo ejecutable que no abra una ventana de consola al iniciarse, ejecuta el siguiente comando:

```bash
pyinstaller --onefile --windowed GUI_mama.py
```

### 3. Localizar el archivo ejecutable

Una vez que el proceso finalice correctamente:

*   Encontrarás el archivo ejecutable en la carpeta llamada **`dist`**.
*   Puedes mover ese archivo a cualquier otra ubicación, pero recuerda que el programa necesita conexión al servidor MySQL para funcionar.

## Notas adicionales

*   **Configuración de DB**: Si el programa falla al iniciar, asegúrate de que el servidor MySQL esté activo y que los datos de conexión en `trabajo_mama.py` sean correctos antes de generar el ejecutable.
*   **Plataforma**: El ejecutable generado solo funcionará en el sistema operativo donde lo creaste (si lo creas en Windows, obtendrás un `.exe`; si lo creas en Linux, un binario de Linux).
