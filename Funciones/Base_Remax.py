<<<<<<< HEAD
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import re

BASE_DIR = Path(__file__).resolve().parent.parent
ENTRADA_LISTA_PRECIOS = BASE_DIR / "Flujo" / "Input"
SALIDA_LISTA = BASE_DIR / "Flujo" / "Output" / "Base_agentes_re_max.xlsx"

datos = []

def limpiar(texto):
    return re.sub(r"\s+", " ", texto).strip() if texto else ""

for archivo in ENTRADA_LISTA_PRECIOS.glob("*.html"):

    html = archivo.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    telefonos = soup.select("a[href^='tel:']")

    for tel in telefonos:
        telefono = tel.get("href", "").replace("tel:", "").strip()
        telefono = re.sub(r"\D", "", telefono)

        # subimos al contenedor del agente
        card = tel
        for _ in range(10):
            if card.parent:
                card = card.parent

            texto = limpiar(card.get_text(" "))

            # cuando el bloque ya tiene suficiente info, paramos
            if telefono in texto and len(texto) > 50:
                break

        texto = limpiar(card.get_text(" "))

        correo_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", texto)
        correo = correo_match.group(0) if correo_match else ""

        # buscar nombre en etiquetas comunes
        nombre = ""
        for tag in card.find_all(["h1", "h2", "h3", "h4", "h5", "strong", "b", "span", "p"]):
            t = limpiar(tag.get_text())
            if (
                t
                and not re.search(r"\d|@|RE/MAX|REMAX|AGENTE|ASESOR|CONTACTAR|VER", t, re.I)
                and len(t.split()) >= 2
            ):
                nombre = t
                break

        grupo = ""
        grupo_match = re.search(r"(RE/MAX\s+[A-Za-zÁÉÍÓÚÑáéíóúñ0-9\s]+)", texto, re.I)
        if grupo_match:
            grupo = limpiar(grupo_match.group(1))

        datos.append({
            "Archivo": archivo.name,
            "Nombre": nombre,
            "Correo": correo,
            "Telefono": telefono,
            "Grupo": grupo,
            "Texto extraido": texto
        })

df = pd.DataFrame(datos).drop_duplicates(subset=["Telefono"])

SALIDA_LISTA.parent.mkdir(parents=True, exist_ok=True)
df.to_excel(SALIDA_LISTA, index=False)

print("Registros encontrados:", len(df))
print("Excel generado:", SALIDA_LISTA)
print(df.head())
=======
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
SALIDA = BASE_DIR / "Flujo" / "Output" / "Base_REMAX_alternativa.xlsx"
SALIDA.parent.mkdir(parents=True, exist_ok=True)

urls = [
    "https://www.remax.pe/web/agents/",
    "https://www.remax.pe/v1/office/remax-family/agents/",
    "https://remaxaccion.com.pe/",
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

agentes = []

for url in urls:
    print("Procesando:", url)

    try:
        r = requests.get(url, headers=headers, timeout=30)
    except Exception as e:
        print("Error:", e)
        continue

    soup = BeautifulSoup(r.text, "html.parser")
    texto = soup.get_text("\n")

    bloques = re.split(r"VER PROPIEDADES|Ver Propiedades|Ver propiedades|Ver Oficina", texto)

    for bloque in bloques:
        lineas = [x.strip() for x in bloque.split("\n") if x.strip()]

        email = ""
        telefono = ""
        oficina = ""
        nombre = ""

        texto_bloque = " ".join(lineas)

        emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", texto_bloque)
        telefonos = re.findall(r"\b9\d{8}\b", re.sub(r"\s+", "", texto_bloque))

        if emails:
            email = emails[0]

        if telefonos:
            telefono = telefonos[0]

        for i, linea in enumerate(lineas):
            if "RE/MAX" in linea.upper() or "REMAX" in linea.upper():
                oficina = linea

                if i > 0:
                    nombre = lineas[i - 1]
                elif i + 1 < len(lineas):
                    nombre = lineas[i + 1]

        if nombre and (email or telefono):
            agentes.append([nombre, oficina, telefono, email, url])

df = pd.DataFrame(
    agentes,
    columns=["Nombre", "Oficina", "Teléfono", "Email", "Fuente"]
)

df.drop_duplicates(inplace=True)
df.to_excel(SALIDA, index=False)

print("===================================")
print("Base generada")
print(f"Total registros: {len(df)}")
print(f"Archivo: {SALIDA}")
print("===================================")
>>>>>>> fa7eb78 (Otro cambio)
