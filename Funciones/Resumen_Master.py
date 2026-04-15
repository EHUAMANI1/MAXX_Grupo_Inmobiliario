import os
import pandas as pd
from pathlib import Path

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent.parent
ENTRADA_DATOS = BASE_DIR / "Flujo" / "Input" / "01 Proyeccion de Ventas - Maxx_v2.01 (1).xlsx"
SALIDA_DATOS = BASE_DIR / "Flujo" / "Output" / "Master.csv"

# --- 2. VARIABLES A CAMBIAR ---
COLUMNA_BUSQUEDA = "D"          
NOMBRE_COL_INICIO = "Categoria"
NOMBRE_COL_FIN = "Cuota Inicial"
HOJA_EXCEL = "Ventas Dptos"     # <--- ¡AQUÍ ESTÁ EL CAMBIO CLAVE!

def transformar_excel_a_csv():
    try:
        print(f"Escaneando el archivo: {ENTRADA_DATOS.name} en la hoja '{HOJA_EXCEL}'...")
        
        # Leer el Excel sin encabezados
        df_crudo = pd.read_excel(ENTRADA_DATOS, sheet_name=HOJA_EXCEL, header=None)
        
        # Convertir letra a índice numérico
        indice_columna = ord(COLUMNA_BUSQUEDA.upper()) - 65 
        
        # Escanear la columna
        columna_escaneada = df_crudo[indice_columna].astype(str).str.strip()
        filas_encontradas = df_crudo[columna_escaneada == NOMBRE_COL_INICIO].index
        
        if len(filas_encontradas) > 0:
            fila_encabezado = filas_encontradas[0] 
            print(f"🎯 ¡Encontrado! '{NOMBRE_COL_INICIO}' está en la fila de Excel: {fila_encabezado + 1}")
            
            # Extraemos todos los nombres de esa fila como una lista limpia
            nombres_fila = df_crudo.iloc[fila_encabezado].astype(str).str.strip().tolist()
            
            # --- LÓGICA: Buscar por POSICIÓN NUMÉRICA ---
            try:
                # Buscamos en qué número de columna están los encabezados que queremos
                idx_inicio = nombres_fila.index(NOMBRE_COL_INICIO)
                idx_fin = nombres_fila.index(NOMBRE_COL_FIN)
                
                # Descartamos la "basura" de arriba y asignamos los nombres
                df_datos = df_crudo.iloc[fila_encabezado + 1:].reset_index(drop=True)
                df_datos.columns = nombres_fila
                
                # Cortamos usando la posición numérica (.iloc) en lugar del nombre
                df_resultado = df_datos.iloc[:, idx_inicio : idx_fin + 1]
                
                # Guardar en CSV
                SALIDA_DATOS.parent.mkdir(parents=True, exist_ok=True)
                df_resultado.to_csv(SALIDA_DATOS, index=False, encoding='utf-8-sig')
                
                print(f"✅ ¡Proceso completado con éxito! Archivo guardado en: {SALIDA_DATOS.name}")
                
            except ValueError:
                print(f"❌ ERROR: Se encontró la fila, pero no pude hallar '{NOMBRE_COL_FIN}'")
                
        else:
            print(f"❌ ERROR: No encontró la palabra '{NOMBRE_COL_INICIO}' en la columna {COLUMNA_BUSQUEDA}.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    transformar_excel_a_csv()