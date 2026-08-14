import streamlit as st
import json

# Configuración de página
st.set_page_config(page_title="Conexiones Levi's", page_icon="👖", layout="wide")

# Clave de acceso
PASSWORD = "Levis2024"

# Cargar datos desde JSON local
@st.cache_data
def cargar_datos():
    try:
        with open("conexiones_datos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return []

# Manejo de autenticación
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
        # Obtener lista de tiendas únicas
        tiendas = sorted(list(set(d["tienda"] for d in datos)))
        
        # Selector de tienda
        tienda_seleccionada = st.selectbox("🔎 Selecciona o escribe el nombre de la tienda:", tiendas)

        if tienda_seleccionada:
            # Filtrar registros de la tienda
            registros = [d for d in datos if d["tienda"] == tienda_seleccionada]
            
            # Identificar conexión principal (MAIN o Main)
            principal = next((d for d in registros if d["caja"].upper() in ["MAIN", "MAIN1"]), registros[0])
            secundarias = [d for d in registros if d != principal]

            # --- VISTA PRINCIPAL ---
            st.markdown("---")
            st.subheader("⭐ Conexión Principal")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.caption("Tienda")
                st.markdown(f"### {principal['tienda']}")
            with col2:
                st.caption("Código de Conexión (haz clic a la derecha para copiar)")
                # st.code agrega automáticamente el botón de copiar a la derecha
                st.code(principal['conexion'], language="")
            with col3:
                st.caption("Tipo de Caja")
                st.markdown(f"### {principal['caja']}")

            # --- OTRAS CONEXIONES ---
            if secundarias:
                st.markdown("---")
                st.subheader("📦 Otras Conexiones Disponibles")
                
                for idx, item in enumerate(secundarias):
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1:
                        st.markdown(f"**Caja:** {item['caja']}")
                    with c2:
                        # Botón de copiar nativo por cada código secundario
                        st.code(item['conexion'], language="")
                    with c3:
                        st.write("")
