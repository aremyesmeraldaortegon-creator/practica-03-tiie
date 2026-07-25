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
