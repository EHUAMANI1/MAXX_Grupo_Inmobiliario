import requests
import pandas as pd
import time
from pathlib import Path

# ==============================
# RUTA DE SALIDA
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
SALIDA_LISTA = BASE_DIR / "Flujo" / "Output" / "Base_Remax.xlsx"
SALIDA_LISTA.parent.mkdir(parents=True, exist_ok=True)

agentes = []
page = 1

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0"
}

while True:
    url = f"https://www.remax.pe/web/agents/?&page={page}"
    print(f"Procesando página {page}")

    response = session.get(url, headers=headers)

    # ==============================
    # DETECTAR BLOQUEO O ERROR
    # ==============================
    if response.status_code != 200:
        print("Bloqueado o error. Fin.")
        break

    html = response.text

    # ==============================
    # DETECTAR SI YA NO HAY DATOS
    # ==============================
    if "agent" not in html.lower() and "@" not in html:
        print("No hay más datos. Fin.")
        break

    # ==============================
    # EXTRAER DE FORMA SIMPLE (fallback)
    # ==============================
    # Nota: sin API real, solo extracción básica del HTML
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    cards = soup.find_all("div")

    nuevos = 0

    for c in cards:
        text = c.get_text(" ", strip=True)

        if "@" in text or "+" in text:
            parts = text.split()

            nombre = parts[0] if len(parts) > 0 else ""
            oficina = parts[1] if len(parts) > 1 else ""

            telefono = ""
            email = ""

            for p in parts:
                if "@" in p:
                    email = p
                if "+" in p:
                    telefono = p

            agentes.append([nombre, oficina, telefono, email])
            nuevos += 1

    if nuevos == 0:
        print("Página sin datos reales. Fin.")
        break

    page += 1
    time.sleep(3)  # evitar bloqueos

# ==============================
# GUARDAR
# ==============================
df = pd.DataFrame(agentes, columns=["Nombre", "Oficina", "Teléfono", "Email"])
df.drop_duplicates(inplace=True)

df.to_excel(SALIDA_LISTA, index=False)

print("===================================")
print("Base generada")
print(f"Total registros: {len(df)}")
print(f"Archivo: {SALIDA_LISTA}")
print("===================================")