import streamlit as st
import pandas as pd
from io import BytesIO
import os
import unidecode  # type: ignore # Librería para eliminar tildes

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

         # 🚨 Reemplazos especiales
            df_filtrado["address"] = df_filtrado["address"].replace({
                "CUMARIBO 250": "CUMARIBO",
                "CUMARIBO 235": "CUMARIBO",
                "YUTAHO": "MAICAO",
                "GUAINIA INIRIDA": "GUAINIA",
                "GUAINIA PTO. COLOMBIA": "GUAINIA",
                "GUAINIA LA GUADALUPE": "GUAINIA",
                "GUAINIA MORICHAL": "GUAINIA",
                "GUAINIA SAN JOSE": "GUAINIA",
                "GUAINIA PTO. COLOMBIA": "GUAINIA",
                "PUERTO ASIS 44": "PUERTO ASIS",
                "PUERTO ASIS 45": "PUERTO ASIS",
                "PUERTO ASIS 65": "PUERTO ASIS"
            })

        # 🔁 Cambiar address si nui es 181503840
        if "nui" in df_filtrado.columns and "address" in df_filtrado.columns:
            df_filtrado.loc[df_filtrado["nui"] == "181503840", "address"] = "CARTAGENA DEL CHAIRA"

       # Contar registros a eliminar
        cantidad_eliminados = df_filtrado[df_filtrado["address"] == "SAN VICENTE DEL CAGUAN"].shape[0]
        # Eliminar registros con SAN VICENTE DEL CAGUAN
        df_filtrado = df_filtrado[df_filtrado["address"] != "SAN VICENTE DEL CAGUAN"]
        # Contar registros restantes
        cantidad_restantes = df_filtrado.shape[0]

        # Mostrar en Streamlit
        col1, col2 = st.columns(2)

        with col1:
            st.warning(f"🗑️ Registros eliminados con 'SAN VICENTE DEL CAGUAN': {cantidad_eliminados}")
        with col2:
            st.info(f"📊 Registros restantes después del filtrado: {cantidad_restantes}")
        
        valores_address = sorted(df_filtrado["address"].unique())
            
        # Mostrar valores únicos restantes en 'address' en tres columnas
        st.success("📍 Valores únicos restantes en 'address':")
        # Crear columnas
        col1, col2, col3 = st.columns(3)
        
        # Repartir los valores en 3 listas equilibradas
        valores_col1 = valores_address[::3]
        valores_col2 = valores_address[1::3]
        valores_col3 = valores_address[2::3]
        
        # Mostrar en cada columna
        with col1:
            for val in valores_col1:
                st.write(val)
        
        with col2:
            for val in valores_col2:
                st.write(val)
        
        with col3:
            for val in valores_col3:
                st.write(val)

         # Reemplazar valores vacíos en p_inicial, p_final y fechaemi con el valor anterior
        for col in ["p_inicial", "p_final", "fechaemi"]:
            if col in df_filtrado.columns:
                df_filtrado[col] = df_filtrado[col].replace("NA", pd.NA).fillna(method="ffill")

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
        df_filtrado = df[columnas_presentes].copy()

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
            
            # Separar mes y año
            df_mes_anio = df_filtrado["Mes de Cobro"].str.split(" ", expand=True).fillna("")
            
            if df_mes_anio.shape[1] == 2:  # Verifica si la separación se hizo correctamente
                df_mes_anio.columns = ["mes", "año"]
            else:
                df_mes_anio["mes"] = ""
                df_mes_anio["año"] = ""

            meses_dict = {
                "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
            }

            df_mes_anio["mes"] = df_mes_anio["mes"].str.lower().map(meses_dict)
            df_mes_anio["año"] = pd.to_numeric(df_mes_anio["año"], errors='coerce')

            # Eliminar "Mes de Cobro" y agregar "mes" y "año"
            df_filtrado = df_filtrado.drop(columns=["Mes de Cobro"]).reset_index(drop=True)
            df_filtrado = pd.concat([df_filtrado, df_mes_anio[["mes", "año"]]], axis=1)

        # Agregar el nombre del archivo
        df_filtrado.insert(0, "nombre_archivo", archivo.name)

        st.success("✅ Archivo procesado correctamente.")
        st.dataframe(df_filtrado)

        # Generar archivo para descargar
        @st.cache_data
        def generar_csv(df):
            return df.to_csv(index=False).encode("utf-8")

        @st.cache_data
        def generar_xlsx(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Cartera Procesada")
            processed_data = output.getvalue()
            return processed_data

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
