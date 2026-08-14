import streamlit as st
import json

# Configuración de la página
st.set_page_config(page_title="Conexiones Levi's", page_icon="👖", layout="wide")

# Clave de acceso
PASSWORD = "Zamvoo_Soporte"

# Cargar datos desde el archivo JSON
@st.cache_data
def cargar_datos():
    try:
        with open("conexiones_datos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return []

# Autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Control de Acceso")
    clave = st.text_input("Ingresa la contraseña para acceder:", type="password")
    if st.button("Ingresar"):
        if clave == PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Inténtalo de nuevo.")
else:
    # --- APLICACIÓN PRINCIPAL ---
    st.title("👖 Buscador de Conexiones Levi's")

    datos = cargar_datos()

    if datos:
        tiendas = sorted(list(set(d["tienda"] for d in datos)))
        tienda_seleccionada = st.selectbox("🔎 Selecciona o escribe el nombre de la tienda:", tiendas)

        if tienda_seleccionada:
            registros = [d for d in datos if d["tienda"] == tienda_seleccionada]
            principal = next((d for d in registros if d["caja"].upper() in ["MAIN", "MAIN1"]), registros[0])
            secundarias = [d for d in registros if d != principal]

            st.markdown("---")
            st.subheader("⭐ Conexión Principal")
            
            # Formato en columnas como el de la imagen
            col1, col2, col3 = st.columns([1.5, 2, 1.2])
            
            with col1:
                st.caption("Tienda")
                st.markdown(f"## {principal['tienda']}")
            
            with col2:
                st.caption("Código de Conexión (pasa el cursor para copiar 📋)")
                # st.code le da la caja destacada con el botón copiar
                st.code(principal['conexion'], language="")
            
            with col3:
                st.caption("Tipo de Caja")
                st.markdown(f"## Caja {principal['caja']}")

            # Lista de otras conexiones disponibles
            if secundarias:
                st.markdown("---")
                st.subheader("📦 Otras Conexiones Disponibles")
                
                # Encabezados de tabla limpia
                c1, c2, c3 = st.columns([1, 2, 2])
                with c1:
                    st.caption("Caja")
                with c2:
                    st.caption("Código de Conexión")
                
                for item in secundarias:
                    col_a, col_b, col_c = st.columns([1, 2, 2])
                    with col_a:
                        st.write(f"**{item['caja']}**")
                    with col_b:
                        st.code(item['conexion'], language="")
