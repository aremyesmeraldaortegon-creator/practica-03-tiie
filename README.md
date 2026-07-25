# Práctica 03 · TIIE a 28 días (Banco de México)

Este es mi proyecto para la Práctica 03 de SPLAN. Construí un programa en Python que consulta la API pública del Banco de México (SIE) para obtener la TIIE a 28 días (serie SF43783), una de las tasas de interés más importantes de la economía mexicana, y la guarda en una base de datos local sin duplicar información, sin importar cuántas veces lo ejecute.

## ¿Qué hace este proyecto?

Mi script hace lo siguiente, en orden:

1. Se conecta a la API de Banxico usando un token de autenticación que guardo de forma segura
2. Descarga los datos históricos de la TIIE a 28 días, desde el 1 de enero de 2026 hasta hoy
3. Convierte las fechas del formato `dd/mm/yyyy` (como vienen de Banxico) a `yyyy-mm-dd` (el formato que usan las bases de datos)
4. Convierte los valores, que llegan como texto, a números decimales de verdad, para poder hacer cálculos con ellos después
5. Guarda todo en una base de datos SQLite (`data/tiie.db`), en una tabla llamada `tiie`
6. Es idempotente: puedo correrlo una y mil veces, y nunca va a duplicar los registros que ya tengo guardados

## ¿Qué se necesita para correrlo?

- Python 3
- Las librerías `requests` y `python-dotenv`, que instalé con:
```bash
  pip install requests python-dotenv
```
- Un token personal de la API de Banxico, que obtuve gratis en https://www.banxico.org.mx/SieAPIRest/service/v1/token

Antes de correr el proyecto, hay que crear un archivo `.env` en la raíz (yo uso `.env.example` como plantilla, que sí está en este repositorio) y poner ahí el token:
BANXICO_TOKEN=tu_token_aquí

Este archivo `.env` nunca se sube a GitHub — está protegido en mi `.gitignore` para que mi token no quede expuesto públicamente.

## ¿Cómo se corre?

```bash
python extraer.py
```

Cuando termina, me muestra el mensaje `Datos guardados correctamente.` y los datos quedan disponibles en `data/tiie.db`.

## Cómo entendí la estructura del JSON

Antes de guardar nada, me tomé el tiempo de observar bien qué me regresaba la API. El JSON tiene tres niveles de "cajas dentro de cajas": primero `bmx`, adentro `series`, y adentro de eso, `datos` — que es donde están las fechas y valores que realmente necesitaba.

Al revisar los datos, encontré dos cosas que tuve que resolver:

- **La fecha** venía como `24/07/2026` (día/mes/año), un formato distinto al que usan normalmente las bases de datos (`2026-07-24`, año-mes-día). Tuve que convertirla.
- **El valor** venía entre comillas, como `'6.7559'`, lo que significa que Python lo trataba como texto y no como número. Si lo hubiera dejado así, no habría podido hacer cálculos como promedios con esos datos. También tuve que convertirlo.

## El problema que descubrí

Antes de resolver nada, hice una prueba: corrí mi script dos veces seguidas, tal cual estaba, sin ningún control de duplicados. La primera vez guardé 141 registros. Después de correrlo una segunda vez, mi tabla tenía 282 registros — exactamente el doble.

Esto pasaba porque mi script no tenía forma de saber que esos datos ya existían: cada vez que lo corría, volvía a pedirle a Banxico la misma información y la volvía a insertar, sin revisar si ya estaba ahí. Si este programa corriera solo, automáticamente, todos los días, mi tabla se iría llenando de copias de los mismos datos una y otra vez, y cualquier cálculo que hiciera con ella (como un promedio) saldría mal, porque cada fecha pesaría de más.

## Cómo lo resolví

Pensé en qué combinación de columnas hace que un registro sea único de verdad. Como la TIIE es una tasa que Banxico publica una sola vez al día, llegué a la conclusión de que la combinación de `id_serie` y `fecha` es lo que identifica a cada registro sin ambigüedad — si esas dos coinciden, forzosamente es un duplicado.

Con esa idea, hice dos cambios en mi código:

1. Agregué una restricción `UNIQUE(id_serie, fecha)` al crear la tabla, para que la base de datos misma rechace cualquier combinación repetida
2. Cambié mi `INSERT` normal por `INSERT OR IGNORE`, para que, si intento insertar un registro que ya existe, simplemente se ignore en vez de duplicarse o marcar error

Para comprobar que funcionó, borré mi base de datos anterior (la que tenía los duplicados), corrí mi script de nuevo para que se creara limpia, y después lo ejecuté varias veces seguidas. El conteo se mantuvo en 141 en todo momento — mi script ya es idempotente.

## Lo más difícil y qué aprendí

Lo más difícil para mí fue la parte inicial: instalar Git, entender cómo funciona la terminal, y lograr conectar mi repositorio local con GitHub, porque era la primera vez que usaba estas herramientas. También me topé con un error de indentación en Python al modificar mi código, que tuve que revisar con calma para encontrar dónde estaba el espaciado mal alineado.

De esta práctica aprendí a consumir una API pública que requiere autenticación, a identificar y resolver un problema real de datos duplicados usando SQL, y sobre todo a proteger credenciales correctamente con `.env` y `.gitignore`, para que un token nunca quede expuesto en un repositorio público. También aprendí que las APIs no siempre entregan los datos exactamente como los necesito — limpiar y convertir la información es parte normal del trabajo.