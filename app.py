import json
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Conexiones Levi's", page_icon="👖", layout="wide")

# Clave de acceso
PASSWORD = "Zamvoo_Soporte"


# Cargar datos desde JSON local
@st.cache_data
def cargar_datos():
    try:
        with open("conexiones_datos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return []


# Función para guardar cambios en el JSON local
def guardar_datos(datos):
    try:
        with open("conexiones_datos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        st.cache_data.clear()  # Limpia la memoria caché
        st.success("✅ Cambios guardados correctamente.")
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")


# Manejo de autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


# Función callback para limpiar el buscador
def limpiar_busqueda():
    st.session_state["box_tienda"] = None


# FUNCIÓN AG NÓSTICA DE CLAVES ULTRA ROBUSTA
def obtener_valor_flexible(diccionario, clave_objetivo):
    """Busca un valor en el diccionario ignorando mayúsculas, minúsculas, espacios y guiones bajos."""
    if not diccionario or not isinstance(diccionario, dict):
        return ""

    objetivo_norm = clave_objetivo.lower().replace("_", "").replace(" ", "")

    for k, v in diccionario.items():
        k_norm = str(k).lower().replace("_", "").replace(" ", "")
        if k_norm == objetivo_norm:
            if v is not None:
                val_str = str(v).strip()
                if val_str != "":
                    return val_str
    return ""


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
    # --- CABECERA Y BOTÓN CERRAR SESIÓN ---
    col_titulo, col_logout = st.columns([5, 1])
    with col_titulo:
        st.title("👖 Buscador de Conexiones Levi's")
    with col_logout:
        st.write("")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            if "box_tienda" in st.session_state:
                st.session_state["box_tienda"] = None
            st.rerun()

    datos = cargar_datos()

    if datos:
        # Extraer tiendas de forma limpia
        tiendas = sorted(
            list(
                set(
                    obtener_valor_flexible(d, "tienda")
                    for d in datos
                    if obtener_valor_flexible(d, "tienda")
                )
            )
        )

        # --- BUSCADOR Y BOTÓN LIMPIAR ---
        col_busqueda, col_limpiar = st.columns([4, 1])

        with col_busqueda:
            tienda_seleccionada = st.selectbox(
                "🔎 Selecciona o escribe el nombre de la tienda:",
                tiendas,
                index=None,
                placeholder="Selecciona una tienda...",
                key="box_tienda",
            )

        with col_limpiar:
            st.write("")
            st.write("")
            st.button("🧹 Limpiar Búsqueda", on_click=limpiar_busqueda)

        if tienda_seleccionada:
            registros = [
                d
                for d in datos
                if obtener_valor_flexible(d, "tienda") == tienda_seleccionada
            ]

            # Selección de Conexión Principal
            principal = next(
                (
                    d
                    for d in registros
                    if obtener_valor_flexible(d, "caja").upper() in ["MAIN", "MAIN1"]
                ),
                registros[0],
            )
            secundarias = [d for d in registros if d != principal]

            # Búsqueda de StoreNo y Controlador entre TODOS los registros de esta tienda
            store_no_val = None
            controlador_val = None

            for reg in registros:
                s = obtener_valor_flexible(reg, "storeno")
                c = obtener_valor_flexible(reg, "controlador")
                if s and not store_no_val:
                    store_no_val = s
                if c and not controlador_val:
                    controlador_val = c

            # Si después de recorrer sigue sin valor, se asigna "N/A"
            final_store_no = store_no_val if store_no_val else "N/A"
            final_controlador = controlador_val if controlador_val else "N/A"

            # --- CONEXIÓN PRINCIPAL ---
            st.markdown("---")
            st.subheader("⭐ Conexión Principal")

            col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1.2, 1, 1.2])

            nombre_tienda = obtener_valor_flexible(principal, "tienda")
            conexion_tv = obtener_valor_flexible(principal, "conexion")
            caja_val = obtener_valor_flexible(principal, "caja")

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

            # --- OTRAS CONEXIONES DISPONIBLES ---
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
                    caja_sec = obtener_valor_flexible(item, "caja")
                    conexion_sec = obtener_valor_flexible(item, "conexion")

                    col_a, col_b = st.columns([1, 4])
                    with col_a:
                        st.markdown(f"**{caja_sec}**")
                    with col_b:
                        st.code(conexion_sec, language="")

        # --- PANEL DE ADMINISTRACIÓN ---
        st.markdown("---")
        with st.expander(
            "🛠️ Panel de Gestión (Crear, Modificar, Eliminar Conexión)"
        ):
            tab1, tab2, tab3 = st.tabs(
                ["➕ Crear Nueva", "✏️ Modificar Existente", "🗑️ Eliminar Conexión"]
            )

            # TAB 1: CREAR
            with tab1:
                st.subheader("Agregar una nueva conexión")
                nueva_tienda = st.text_input("Nombre de la Tienda:", key="add_tienda")
                nuevo_store_no = st.text_input(
                    "Número de Tienda (StoreNo):", key="add_store_no"
                )
                nuevo_controlador = st.text_input(
                    "Controlador:", key="add_controlador"
                )
                nueva_conexion = st.text_input(
                    "Código de Conexión (ej: PCLO...):", key="add_conexion"
                )
                nueva_caja = st.text_input("Caja (ej: MAIN, C1, C2):", key="add_caja")

                if st.button("Guardar Nueva Conexión", key="btn_add"):
                    if nueva_tienda and nueva_conexion and nueva_caja:
                        nuevo_registro = {
                            "Tienda": nueva_tienda.strip(),
                            "StoreNo": nuevo_store_no.strip(),
                            "Controlador": nuevo_controlador.strip(),
                            "Conexion": nueva_conexion.strip(),
                            "Caja": nueva_caja.strip(),
                        }
                        datos.append(nuevo_registro)
                        guardar_datos(datos)
                        st.rerun()
                    else:
                        st.warning(
                            "Por favor completa los campos requeridos (Tienda, Conexión y Caja)."
                        )

            # TAB 2: MODIFICAR
            with tab2:
                st.subheader("Modificar una conexión existente")
                if "registros" in locals() and registros:
                    opciones_mod = [
                        f"{obtener_valor_flexible(r, 'caja')} - {obtener_valor_flexible(r, 'conexion')}"
                        for r in registros
                    ]
                    seleccion_mod = st.selectbox(
                        "Selecciona la caja a modificar de la tienda actual:",
                        opciones_mod,
                        key="mod_sel_box",
                    )

                    registro_actual = registros[opciones_mod.index(seleccion_mod)]

                    mod_tienda = st.text_input(
                        "Tienda:",
                        value=obtener_valor_flexible(registro_actual, "tienda"),
                        key="mod_tienda",
                    )
                    mod_store_no = st.text_input(
                        "StoreNo:",
                        value=obtener_valor_flexible(registro_actual, "storeno"),
                        key="mod_store_no",
                    )
                    mod_controlador = st.text_input(
                        "Controlador:",
                        value=obtener_valor_flexible(registro_actual, "controlador"),
                        key="mod_controlador",
                    )
                    mod_conexion = st.text_input(
                        "Conexión:",
                        value=obtener_valor_flexible(registro_actual, "conexion"),
                        key="mod_conexion",
                    )
                    mod_caja = st.text_input(
                        "Caja:",
                        value=obtener_valor_flexible(registro_actual, "caja"),
                        key="mod_caja",
                    )

                    if st.button("Actualizar Conexión", key="btn_mod"):
                        idx = datos.index(registro_actual)
                        datos[idx] = {
                            "Tienda": mod_tienda.strip(),
                            "StoreNo": mod_store_no.strip(),
                            "Controlador": mod_controlador.strip(),
                            "Conexion": mod_conexion.strip(),
                            "Caja": mod_caja.strip(),
                        }
                        guardar_datos(datos)
                        st.rerun()

            # TAB 3: ELIMINAR
            with tab3:
                st.subheader("Eliminar una conexión")
                if "registros" in locals() and registros:
                    opciones_del = [
                        f"{obtener_valor_flexible(r, 'caja')} - {obtener_valor_flexible(r, 'conexion')}"
                        for r in registros
                    ]
                    seleccion_del = st.selectbox(
                        "Selecciona la caja a eliminar de la tienda actual:",
                        opciones_del,
                        key="del_sel_box",
                    )

                    registro_a_eliminar = registros[opciones_del.index(seleccion_del)]

                    if st.button(
                        "❌ Eliminar Conexión Definitivamente",
                        type="primary",
                        key="btn_del",
                    ):
                        datos.remove(registro_a_eliminar)
                        guardar_datos(datos)
                        st.rerun()
