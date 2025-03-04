import streamlit as st
import pandas as pd
from io import BytesIO
import os
import unidecode  # Librería para eliminar tildes

# Configuración inicial de la app
st.set_page_config(page_title="Captura de Datos", page_icon="📊", layout="centered")

# Título principal
st.title("📊 Captura de Datos")

# Menú de selección
opcion = st.sidebar.selectbox("Selecciona una opción:", ["Inicio", "Facturación", "Cartera"])

# ------------------- FUNCIONES GENERALES -------------------
def generar_xlsx(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output

def generar_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# ------------------- SECCIÓN DE FACTURACIÓN -------------------
if opcion == "Facturación":
    st.subheader("📄 Procesamiento de Facturación")

    archivo = st.file_uploader("📂 Cargar archivo Excel", type=["xlsx"])

    if archivo is not None:
        df = pd.read_excel(archivo)

        # Obtener el nombre del archivo
        nombre_archivo = archivo.name  

        # Definir las columnas a filtrar
        columnas_deseadas = ["nfacturasiigo", "nui", "identificacion", "address", "cantidad", "p_inicial", "p_final", "fechaemi", "mes", "ano"]
        columnas_presentes = [col for col in columnas_deseadas if col in df.columns]

        # Filtrar columnas
        df_filtrado = df[columnas_presentes]

        # Agregar el nombre del archivo como una nueva columna
        df_filtrado.insert(0, "nombre_archivo", nombre_archivo)

        # Reemplazar valores vacíos o NaN con "NA"
        df_filtrado.fillna("NA", inplace=True)

        # Limpieza de datos
        if "nfacturasiigo" in df_filtrado.columns:
            df_filtrado["nfacturasiigo"] = df_filtrado["nfacturasiigo"].astype(str).str.replace("-", "", regex=True)
        if "nui" in df_filtrado.columns:
            df_filtrado["nui"] = df_filtrado["nui"].astype(str).str.replace("-", "", regex=True)

        if "fechaemi" in df_filtrado.columns:
            df_filtrado["fechaemi"] = pd.to_datetime(df_filtrado["fechaemi"], errors='coerce').dt.strftime('%Y-%m-%d').fillna("NA")
        if "p_inicial" in df_filtrado.columns:
            df_filtrado["p_inicial"] = pd.to_datetime(df_filtrado["p_inicial"], errors='coerce').dt.strftime('%Y-%m-%d').fillna("NA")
        if "p_final" in df_filtrado.columns:
            df_filtrado["p_final"] = pd.to_datetime(df_filtrado["p_final"], errors='coerce').dt.strftime('%Y-%m-%d').fillna("NA")

        if "address" in df_filtrado.columns:
            df_filtrado["address"] = df_filtrado["address"].astype(str).str.upper()  # Convertir a mayúsculas
            df_filtrado["address"] = df_filtrado["address"].apply(lambda x: unidecode.unidecode(x))  # Eliminar tildes

        st.success("✅ Archivo procesado correctamente.")
        st.dataframe(df_filtrado)

        # Botones de descarga
        xlsx = generar_xlsx(df_filtrado)
        st.download_button(label="📥 Descargar Excel", data=xlsx, file_name="facturacion_procesada.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        csv = generar_csv(df_filtrado)
        st.download_button(label="📥 Descargar CSV", data=csv, file_name="facturacion_procesada.csv", mime="text/csv")

# ------------------- SECCIÓN DE FACTURACIÓN -------------------

# ------------------- SECCIÓN DE CARTERA -------------------
elif opcion == "Cartera":
    st.subheader("💰 Procesamiento de Cartera")

    archivo = st.file_uploader("📂 Cargar archivo Excel", type=["xlsx"])

    if archivo is not None:
        df = pd.read_excel(archivo)
        columnas_deseadas = ["Identificación", "NUI", "Factura", "PROYECTO", "Saldo Factura", "Mes de Cobro"]

        # Filtrar columnas disponibles
        columnas_presentes = [col for col in columnas_deseadas if col in df.columns]
        df_filtrado = df[columnas_presentes]

        # Limpieza de datos
        if "NUI" in df_filtrado.columns:
            df_filtrado["NUI"] = df_filtrado["NUI"].astype(str).str.replace("-", "", regex=True)
        if "Factura" in df_filtrado.columns:
            df_filtrado["Factura"] = df_filtrado["Factura"].astype(str).str.replace("-", "", regex=True)

        if "PROYECTO" in df_filtrado.columns:
            df_filtrado["PROYECTO"] = df_filtrado["PROYECTO"].astype(str).str.upper()
            df_filtrado["PROYECTO"] = df_filtrado["PROYECTO"].apply(lambda x: unidecode.unidecode(x))  # Eliminar tildes

        df_filtrado.fillna("NA", inplace=True)

        if "Factura" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["Factura"] != "NA"]

        # Procesamiento del "Mes de Cobro"
        if "Mes de Cobro" in df_filtrado.columns:
            df_filtrado["Mes de Cobro"] = df_filtrado["Mes de Cobro"].astype(str)
            df_filtrado[["mes", "año"]] = df_filtrado["Mes de Cobro"].str.split(" ", expand=True).fillna("")

            meses_dict = {
                "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
            }

            df_filtrado["mes"] = df_filtrado["mes"].str.lower().map(meses_dict)
            df_filtrado["año"] = pd.to_numeric(df_filtrado["año"], errors='coerce')

        # Agregar el nombre del archivo
        df_filtrado.insert(0, "nombre_archivo", archivo.name)

        st.success("✅ Archivo procesado correctamente.")
        st.dataframe(df_filtrado)

        # Botones de descarga
        xlsx = generar_xlsx(df_filtrado)
        st.download_button(label="📥 Descargar Excel", data=xlsx, file_name="cartera_procesada.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        csv = generar_csv(df_filtrado)
        st.download_button(label="📥 Descargar CSV", data=csv, file_name="cartera_procesada.csv", mime="text/csv")

# ------------------- PANTALLA INICIO -------------------
else:
    st.write("👈 Usa el menú de la izquierda para seleccionar una opción.")
    st.markdown("""
        ### 📌 Instrucciones:
        - Selecciona una opción en el menú lateral.
        - Sube un archivo **Excel** con los datos requeridos.
        - Descarga los resultados en **Excel** o **CSV**.
    """)