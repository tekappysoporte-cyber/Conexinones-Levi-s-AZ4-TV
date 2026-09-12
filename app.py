import json
import os
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Conexiones LV AZ4", page_icon="👖", layout="wide"
)

RUTA_JSON = "conexiones_datos.json"


# Cargar datos SIEMPRE FRESCOS
def cargar_datos():
    if os.path.exists(RUTA_JSON):
        try:
            with open(RUTA_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error al cargar la base de datos: {e}")
            return []
    return []


# Inicializar datos en session_state para mantener persistencia visual inmediata
if "datos" not in st.session_state:
    st.session_state["datos"] = cargar_datos()


def limpiar_busqueda():
    st.session_state["box_tienda"] = None
    st.session_state["box_storeno"] = None
    st.session_state["box_conexion"] = None


# Callbacks para limpiar los otros campos cuando se usa uno específico
def cambiar_tienda():
    st.session_state["box_storeno"] = None
    st.session_state["box_conexion"] = None


def cambiar_storeno():
    st.session_state["box_tienda"] = None
    st.session_state["box_conexion"] = None


def cambiar_conexion():
    st.session_state["box_tienda"] = None
    st.session_state["box_storeno"] = None


# EXTRAER CUALQUIER VALOR SIN IMPORTAR MAYÚSCULAS/MINÚSCULAS
def get_val(reg, campo_objetivo):
    if not isinstance(reg, dict):
        return ""
    campo_norm = campo_objetivo.lower().strip()
    for k, v in reg.items():
        if str(k).lower().strip() == campo_norm:
            if v is not None:
                txt = str(v).strip()
                if txt and txt.lower() != "null":
                    return txt
    return ""


# Función para ordenar registros por tipo de caja de forma lógica
def ordenar_registros(registros):
    def clave_orden(reg):
        caja = get_val(reg, "caja").upper()
        if caja in ["MAIN", "MAIN1"]:
            return (0, caja)
        return (1, caja)

    return sorted(registros, key=clave_orden)


# --- CABECERA ---
st.title("👖 Buscador de Conexiones Levi's")

# Sincronizamos con st.session_state
datos = st.session_state["datos"]

if datos:
    # Extraer listas únicas para los selectores
    tiendas = sorted(
        list(set(get_val(d, "tienda") for d in datos if get_val(d, "tienda")))
    )
    storenos = sorted(
        list(set(get_val(d, "storeno") for d in datos if get_val(d, "storeno")))
    )
    conexiones = sorted(
        list(set(get_val(d, "conexion") for d in datos if get_val(d, "conexion")))
    )

    # --- BUSCADORES ---
    col_busqueda, col_limpiar = st.columns([4, 1])

    with col_busqueda:
        tienda_seleccionada = st.selectbox(
            "🔎 Selecciona o escribe el nombre de la tienda:",
            tiendas,
            index=None,
            placeholder="Selecciona una tienda...",
            key="box_tienda",
            on_change=cambiar_tienda,
        )

    with col_limpiar:
        st.write("")
        st.write("")
        st.button("🧹 Limpiar Búsqueda", on_click=limpiar_busqueda)

    # BUSCADORES ADICIONALES (StoreNo y Conexión) en dos columnas
    col_filtro1, col_filtro2 = st.columns(2)

    with col_filtro1:
        storeno_seleccionado = st.selectbox(
            "🔢 O busca por número de tienda (StoreNo):",
            storenos,
            index=None,
            placeholder="Selecciona StoreNo...",
            key="box_storeno",
            on_change=cambiar_storeno,
        )

    with col_filtro2:
        conexion_seleccionada = st.selectbox(
            "🔌 O busca por código de conexión:",
            conexiones,
            index=None,
            placeholder="Selecciona conexión...",
            key="box_conexion",
            on_change=cambiar_conexion,
        )

    # Determinar qué tienda mostrar basada en cualquiera de los 3 filtros activos
    tienda_a_mostrar = None
    if st.session_state.get("box_tienda"):
        tienda_a_mostrar = st.session_state["box_tienda"]
    elif st.session_state.get("box_storeno"):
        reg_temp = next((d for d in datos if get_val(d, "storeno") == st.session_state["box_storeno"]), None)
        if reg_temp:
            tienda_a_mostrar = get_val(reg_temp, "tienda")
    elif st.session_state.get("box_conexion"):
        reg_temp = next((d for d in datos if get_val(d, "conexion") == st.session_state["box_conexion"]), None)
        if reg_temp:
            tienda_a_mostrar = get_val(reg_temp, "tienda")

    if tienda_a_mostrar:
        registros_raw = [
            d for d in datos if get_val(d, "tienda") == tienda_a_mostrar
        ]
        registros = ordenar_registros(registros_raw)

        # Selección de Conexión Principal
        principal = next(
            (
                d
                for d in registros
                if get_val(d, "caja").upper() in ["MAIN", "MAIN1"]
            ),
            registros[0] if registros else None,
        )
        
        if principal:
            secundarias = [d for d in registros if d != principal]

            # BÚSQUEDA DIRECTA DE STORENO Y CONTROLADOR
            store_no_val = ""
            controlador_val = ""

            for r in registros:
                s = get_val(r, "storeno")
                c = get_val(r, "controlador")
                if s and not store_no_val:
                    store_no_val = s
                if c and not controlador_val:
                    controlador_val = c

            final_store_no = store_no_val if store_no_val else "N/A"
            final_controlador = controlador_val if controlador_val else "N/A"

            # --- VISTA PRINCIPAL ---
            st.markdown("---")
            st.subheader("⭐ Conexión Principal")

            col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1.2, 1, 1.2])

            nombre_tienda = get_val(principal, "tienda")
            conexion_tv = get_val(principal, "conexion")
            caja_val = get_val(principal, "caja")

            with col1:
                st.caption("Tienda")
                st.markdown(f"## {nombre_tienda}")

            with col2:
                st.caption("Conexión TV")
                st.code(conexion_tv, language="")

            with col3:
                st.caption("Tipo de Caja")
                st.markdown(
                    f"## Caja {caja_val}"
                    if not caja_val.upper().startswith("CAJA")
                    else f"## {caja_val}"
                )

            with col4:
                st.caption("StoreNo")
                st.markdown(f"## {final_store_no}")

            with col5:
                st.caption("Controlador")
                st.markdown(f"## {final_controlador}")

            # --- OTRAS CONEXIONES ---
            if secundarias:
                st.markdown("---")
                st.subheader("📦 Otras Conexiones Disponibles")

                c_head1, c_head2 = st.columns([1, 4])
                with c_head1:
                    st.caption("**Caja**")
                with c_head2:
                    st.caption("**Conexión TV**")

                st.markdown(
                    "<hr style='margin: 0 0 10px 0; border: 0.5px solid #333;'>",
                    unsafe_allow_html=True,
                )

                for item in secundarias:
                    caja_sec = get_val(item, "caja")
                    conexion_sec = get_val(item, "conexion")

                    col_a, col_b = st.columns([1, 4])
                    with col_a:
                        st.markdown(f"**{caja_sec}**")
                    with col_b:
                        st.code(conexion_sec, language="")
