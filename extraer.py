import requests
from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv("BANXICO_TOKEN")
url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43783/datos/2026-01-01/2026-07-24"
headers = {
    "Bmx-Token": token
}
respuesta = requests.get(url, headers=headers)
print(respuesta.json())
import requests
from dotenv import load_dotenv
import os
import sqlite3

# --- Parte que ya tenías: pedir los datos a Banxico ---
load_dotenv()
token = os.getenv("BANXICO_TOKEN")
url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43783/datos/2026-01-01/2026-07-24"
headers = {"Bmx-Token": token}
respuesta = requests.get(url, headers=headers)
datos_json = respuesta.json()

# --- Parte nueva: conectar y preparar la base de datos ---
conexion = sqlite3.connect("data/tiie.db")
cursor = conexion.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tiie (
        id_serie TEXT,
        fecha TEXT,
        valor REAL
    )
""")

# --- Parte nueva: recorrer cada dato y convertirlo ---
lista_datos = datos_json["bmx"]["series"][0]["datos"]

for item in lista_datos:
    fecha_original = item["fecha"]          # ejemplo: "24/07/2026"
    dia, mes, anio = fecha_original.split("/")
    fecha_convertida = f"{anio}-{mes}-{dia}"  # ejemplo: "2026-07-24"

    valor_convertido = float(item["dato"])   # de texto a número

    cursor.execute(
        "INSERT INTO tiie (id_serie, fecha, valor) VALUES (?, ?, ?)",
        ("SF43783", fecha_convertida, valor_convertido)
    )

conexion.commit()
conexion.close()

print("Datos guardados correctamente.")
