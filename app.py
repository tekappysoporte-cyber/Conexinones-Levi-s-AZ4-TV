import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Gestor de Conexiones Levi's", layout="wide", page_icon="👖")

# ==========================================
# CONFIGURACIÓN DE CONTRASEÑA
# ==========================================
# Cambia 'Levis2024' por la contraseña que quieras compartir con tus compañeros
CLAVE_ACCESO = "Zamvoo_Soporte"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso Restringido")
    st.info("Ingresa la contraseña para acceder al sistema.")
    
    clave_ingresada = st.text_input("Contraseña:", type="password")
    if st.button("Ingresar", type="primary"):
        if clave_ingresada == CLAVE_ACCESO:
            st.session_state.autenticado = True
            st.success("¡Acceso concedido!")
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    
    # Detiene la ejecución para que nadie vea los datos sin la contraseña
    st.stop()

# ==========================================
# CÓDIGO DE LA APLICACIÓN (Si la contraseña es correcta)
# ==========================================

# Botón para cerrar sesión en la barra lateral
with st.sidebar:
    st.write("👤 **Sesión Activa**")
    if st.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

ARCHIVO_DATOS = "conexiones_datos.json"

DATOS_INICIALES = [
    {"tienda": "Levis Arauco Maipu", "conexion": "PCLO4000011101O", "caja": "C1"},
    {"tienda": "Levis Arauco Maipu", "conexion": "PCLO4000011102O", "caja": "C2"},
    {"tienda": "Levis Alto Las Condes", "conexion": "PCLO4000012501O", "caja": "MAIN"},
    {"tienda": "Levis Alto Las Condes", "conexion": "PCLO4000012502O", "caja": "C1"}
]

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        guardar_datos(DATOS_INICIALES)
        return DATOS_INICIALES

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

if "conexiones" not in st.session_state:
    st.session_state.conexiones = cargar_datos()

st.title("👖 Gestor de Conexiones Levi's")

tab1, tab2, tab3 = st.tabs(["🔎 Buscador de Tienda", "📝 Modificar / Eliminar", "➕ Crear Nueva Conexión"])

# PESTAÑA 1: BUSCADOR
with tab1:
    st.session_state.conexiones = cargar_datos()
    df_base = pd.DataFrame(st.session_state.conexiones)
    tiendas_unicas = sorted(df_base["tienda"].unique().tolist()) if not df_base.empty else []

    tienda_seleccionada = st.selectbox(
        "🔎 Selecciona o escribe el nombre de la tienda:",
        options=[""] + tiendas_unicas,
        index=0,
        placeholder="Ejemplo: Levis Costanera Center"
    )

    if tienda_seleccionada:
        df_tienda = df_base[df_base["tienda"] == tienda_seleccionada].copy()

        df_tienda["prioridad"] = 3
        caja_upper = df_tienda["caja"].str.upper()
        df_tienda.loc[caja_upper == "MAIN", "prioridad"] = 1
        df_tienda.loc[caja_upper == "C1", "prioridad"] = 2

        df_tienda = df_tienda.sort_values(by="prioridad")
        principal = df_tienda.iloc[0]

        st.markdown("---")
        st.subheader("⭐ Conexión Principal")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Tienda", value=principal["tienda"])
        with col2:
            st.metric(label="Código de Conexión", value=principal["conexion"])
        with col3:
            st.metric(label="Tipo de Caja", value=f"Caja {principal['caja']}")

        df_demas = df_tienda.iloc[1:].copy()
        st.markdown("---")
        if not df_demas.empty:
            st.subheader("📦 Otras Conexiones Disponibles")
            df_demas_mostrar = df_demas[["caja", "conexion"]].rename(
                columns={"caja": "Caja", "conexion": "Código de Conexión"}
            )
            st.dataframe(df_demas_mostrar, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Esta tienda no posee conexiones adicionales registradas.")
    else:
        st.info("👆 Por favor selecciona una tienda para consultar sus conexiones.")

# PESTAÑA 2: MODIFICAR / ELIMINAR
with tab2:
    st.header("Gestión de Registros Existentes")
    st.info("💡 Edita las celdas directamente o borra filas. Luego haz clic en 'Guardar Cambios'.")

    df_actual = pd.DataFrame(st.session_state.conexiones)
    df_editado = st.data_editor(
        df_actual,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_tabla"
    )

    if st.button("💾 Guardar Cambios en la Tabla", type="primary"):
        nuevos_datos = df_editado.to_dict("records")
        guardar_datos(nuevos_datos)
        st.session_state.conexiones = nuevos_datos
        st.success("¡Base de datos guardada con éxito!")
        st.rerun()

# PESTAÑA 3: CREAR NUEVA CONEXIÓN
with tab3:
    st.header("Agregar Nueva Conexión")
    with st.form("form_agregar"):
        col1, col2, col3 = st.columns(3)
        with col1:
            n_tienda = st.text_input("Nombre de la Tienda")
        with col2:
            n_conexion = st.text_input("Código de Conexión Base", placeholder="Ej: PCLO4000019901O")
        with col3:
            n_caja = st.text_input("Tipo/Nombre de Caja", placeholder="Ej: MAIN, C1, C2...")

        submit = st.form_submit_button("➕ Agregar Registro")

        if submit:
            if n_tienda and n_conexion and n_caja:
                lista_actual = cargar_datos()
                lista_actual.append({
                    "tienda": n_tienda.strip(),
                    "conexion": n_conexion.strip(),
                    "caja": n_caja.strip()
                })
                guardar_datos(lista_actual)
                st.session_state.conexiones = lista_actual
                st.success(f"¡Se agregó correctamente '{n_tienda}' ({n_caja})!")
                st.rerun()
            else:
                st.error("Por favor, completa todos los campos del formulario.")
