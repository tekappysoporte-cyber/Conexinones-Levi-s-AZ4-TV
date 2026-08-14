import json
import pandas as pd
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

# Inicializar estado de tienda seleccionada si no existe
if "tienda_sel" not in st.session_state:
    st.session_state["tienda_sel"] = None

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
            st.session_state["tienda_sel"] = None
            st.rerun()

    datos = cargar_datos()

    if datos:
        tiendas = sorted(list(set(d["tienda"] for d in datos)))

        # --- BUSCADOR Y BOTÓN LIMPIAR ---
        col_busqueda, col_limpiar = st.columns([4, 1])

        # Determinar índice actual para el selectbox
        idx_tienda = None
        if (
            st.session_state["tienda_sel"]
            and st.session_state["tienda_sel"] in tiendas
        ):
            idx_tienda = tiendas.index(st.session_state["tienda_sel"])

        with col_busqueda:
            tienda_seleccionada = st.selectbox(
                "🔎 Selecciona o escribe el nombre de la tienda:",
                tiendas,
                index=idx_tienda,
                placeholder="Selecciona una tienda...",
                key="box_tienda",
            )
            # Guardar selección en el session state
            st.session_state["tienda_sel"] = tienda_seleccionada

        with col_limpiar:
            st.write("")
            st.write("")  # Alineación con el input
            if st.button("🧹 Limpiar Búsqueda"):
                st.session_state["tienda_sel"] = None
                if "box_tienda" in st.session_state:
                    del st.session_state["box_tienda"]
                st.rerun()

        if tienda_seleccionada:
            registros = [
                d for d in datos if d["tienda"] == tienda_seleccionada
            ]
            principal = next(
                (
                    d
                    for d in registros
                    if d["caja"].upper() in ["MAIN", "MAIN1"]
                ),
                registros[0],
            )
            secundarias = [d for d in registros if d != principal]

            # --- CONEXIÓN PRINCIPAL ---
            st.markdown("---")
            st.subheader("⭐ Conexión Principal")

            col1, col2, col3 = st.columns([1.5, 2, 1.2])

            with col1:
                st.caption("Tienda")
                st.markdown(f"## {principal['tienda']}")

            with col2:
                # 🏷️ CAMBIO REALIZADO: Ahora dice "Conexión TV"
                st.caption("Conexión TV")
                st.code(principal["conexion"], language="")

            with col3:
                st.caption("Tipo de Caja")
                st.markdown(f"## Caja {principal['caja']}")

            # --- OTRAS CONEXIONES DISPONIBLES ---
            if secundarias:
                st.markdown("---")
                st.subheader("📦 Otras Conexiones Disponibles")

                df_secundarias = pd.DataFrame(secundarias)[["caja", "conexion"]]
                df_secundarias.columns = ["Caja", "Conexión TV"]

                # 📋 TABLA IDÉNTICA + BOTÓN PARA COPIAR AL PASAR EL CURSOR
                st.dataframe(
                    df_secundarias,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Conexión TV": st.column_config.TextColumn(
                            "Conexión TV",
                            help="Haz clic en el icono para copiar el código",
                            copy_to_clipboard=True,  # Habilita el botón nativo de copiar en la tabla
                        )
                    },
                )

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
                nueva_tienda = st.text_input("Nombre de la Tienda:")
                nueva_conexion = st.text_input(
                    "Código de Conexión (ej: PCLO...):"
                )
                nueva_caja = st.text_input("Caja (ej: MAIN, C1, C2):")

                if st.button("Guardar Nueva Conexión"):
                    if nueva_tienda and nueva_conexion and nueva_caja:
                        nuevo_registro = {
                            "tienda": nueva_tienda.strip(),
                            "conexion": nueva_conexion.strip(),
                            "caja": nueva_caja.strip(),
                        }
                        datos.append(nuevo_registro)
                        guardar_datos(datos)
                        st.rerun()
                    else:
                        st.warning("Por favor completa todos los campos.")

            # TAB 2: MODIFICAR
            with tab2:
                st.subheader("Modificar una conexión existente")
                if "registros" in locals() and registros:
                    opciones_mod = [
                        f"{r['caja']} - {r['conexion']}" for r in registros
                    ]
                    seleccion_mod = st.selectbox(
                        "Selecciona la caja a modificar de la tienda actual:",
                        opciones_mod,
                    )

                    registro_actual = registros[
                        opciones_mod.index(seleccion_mod)
                    ]

                    mod_tienda = st.text_input(
                        "Tienda:", value=registro_actual["tienda"]
                    )
                    mod_conexion = st.text_input(
                        "Conexión:", value=registro_actual["conexion"]
                    )
                    mod_caja = st.text_input(
                        "Caja:", value=registro_actual["caja"]
                    )

                    if st.button("Actualizar Conexión"):
                        idx = datos.index(registro_actual)
                        datos[idx] = {
                            "tienda": mod_tienda.strip(),
                            "conexion": mod_conexion.strip(),
                            "caja": mod_caja.strip(),
                        }
                        guardar_datos(datos)
                        st.rerun()

            # TAB 3: ELIMINAR
            with tab3:
                st.subheader("Eliminar una conexión")
                if "registros" in locals() and registros:
                    opciones_del = [
                        f"{r['caja']} - {r['conexion']}" for r in registros
                    ]
                    seleccion_del = st.selectbox(
                        "Selecciona la caja a eliminar de la tienda actual:",
                        opciones_del,
                        key="del_sel",
                    )

                    registro_a_eliminar = registros[
                        opciones_del.index(seleccion_del)
                    ]

                    if st.button(
                        "❌ Eliminar Conexión Definitivamente", type="primary"
                    ):
                        datos.remove(registro_a_eliminar)
                        guardar_datos(datos)
                        st.rerun()
