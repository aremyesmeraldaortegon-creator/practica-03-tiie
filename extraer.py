import requests
from dotenv import load_dotenv
import os
import sqlite3

# --- Pedir los datos a Banxico ---
load_dotenv()
token = os.getenv("BANXICO_TOKEN")
url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43783/datos/2026-01-01/2026-07-24"
headers = {"Bmx-Token": token}
respuesta = requests.get(url, headers=headers)
datos_json = respuesta.json()

# --- Conectar y preparar la base de datos ---
conexion = sqlite3.connect("data/tiie.db")
cursor = conexion.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tiie (
        id_serie TEXT,
        fecha TEXT,
        valor REAL,
        UNIQUE(id_serie, fecha)
    )
""")

# --- Recorrer cada dato, convertirlo e insertarlo ---
lista_datos = datos_json["bmx"]["series"][0]["datos"]

for item in lista_datos:
    fecha_original = item["fecha"]
    dia, mes, anio = fecha_original.split("/")
    fecha_convertida = f"{anio}-{mes}-{dia}"

    valor_convertido = float(item["dato"])

    cursor.execute(
        "INSERT OR IGNORE INTO tiie (id_serie, fecha, valor) VALUES (?, ?, ?)",
        ("SF43783", fecha_convertida, valor_convertido)
    )

conexion.commit()
conexion.close()

print("Datos guardados correctamente.")