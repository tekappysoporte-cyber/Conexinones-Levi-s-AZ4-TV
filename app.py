import json
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Conexiones LV AZ4", page_icon="🔒", layout="wide"
)

PASSWORD = "Zamvoo_Soporte"


# Cargar datos SIEMPRE FRESCOS
def cargar_datos():
    try:
        with open("conexiones_datos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return []


def guardar_datos(datos):
    try:
        with open("conexiones_datos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        st.success("✅ Cambios guardados correctamente.")
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")


# Manejo de autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


def limpiar_busqueda():
    st.session_state["box_tienda"] = None


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


# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🔒 Control de Acceso a Conexiones LV AZ4")
    clave = st.text_input("Ingresa la contraseña para acceder:", type="password")
    if st.button("Ingresar"):
        if clave == PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Inténtalo de nuevo.")
else:
    # --- CABECERA ---
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
        # Extraer tiendas únicas
        tiendas = sorted(
            list(set(get_val(d, "tienda") for d in datos if get_val(d, "tienda")))
        )

        # --- BUSCADOR ---
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
            registros_raw = [
                d for d in datos if get_val(d, "tienda") == tienda_seleccionada
            ]
            registros = ordenar_registros(registros_raw)

            # Selección de Conexión Principal
            principal = next(
                (
                    d
                    for d in registros
                    if get_val(d, "caja").upper() in ["MAIN", "MAIN1"]
                ),
                registros[0],
            )
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
                nueva_tienda = st.text_input(
                    "Nombre de la Tienda:", key="add_tienda"
                )
                nuevo_store_no = st.text_input(
                    "Número de Tienda (StoreNo):", key="add_store_no"
                )
                nuevo_controlador = st.text_input(
                    "Controlador:", key="add_controlador"
                )
                nueva_conexion = st.text_input(
                    "Código de Conexión (ej: PCLO...):", key="add_conexion"
                )
                nueva_caja = st.text_input(
                    "Caja (ej: MAIN, C1, C2):", key="add_caja"
                )

                if st.button("Guardar Nueva Conexión", key="btn_add"):
                    t_val = nueva_tienda.strip() if nueva_tienda else ""
                    c_val = nueva_conexion.strip() if nueva_conexion else ""
                    box_val = nueva_caja.strip() if nueva_caja else ""

                    if t_val and c_val and box_val:
                        nuevo_registro = {
                            "Controlador": (
                                nuevo_controlador.strip()
                                if nuevo_controlador
                                else ""
                            ),
                            "StoreNo": (
                                nuevo_store_no.strip() if nuevo_store_no else ""
                            ),
                            "Tienda": t_val,
                            "Conexion": c_val,
                            "Caja": box_val,
                        }
                        datos.append(nuevo_registro)
                        datos = ordenar_registros(datos)
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
                        f"{get_val(r, 'caja')} - {get_val(r, 'conexion')}"
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
                        value=get_val(registro_actual, "tienda"),
                        key="mod_tienda",
                    )
                    mod_store_no = st.text_input(
                        "StoreNo:",
                        value=get_val(registro_actual, "storeno"),
                        key="mod_store_no",
                    )
                    mod_controlador = st.text_input(
                        "Controlador:",
                        value=get_val(registro_actual, "controlador"),
                        key="mod_controlador",
                    )
                    mod_conexion = st.text_input(
                        "Conexión:",
                        value=get_val(registro_actual, "conexion"),
                        key="mod_conexion",
                    )
                    mod_caja = st.text_input(
                        "Caja:",
                        value=get_val(registro_actual, "caja"),
                        key="mod_caja",
                    )

                    if st.button("Actualizar Conexión", key="btn_mod"):
                        idx = datos.index(registro_actual)
                        datos[idx] = {
                            "Controlador": mod_controlador.strip(),
                            "StoreNo": mod_store_no.strip(),
                            "Tienda": mod_tienda.strip(),
                            "Conexion": mod_conexion.strip(),
                            "Caja": mod_caja.strip(),
                        }
                        datos = ordenar_registros(datos)
                        guardar_datos(datos)
                        st.rerun()
                else:
                    st.info(
                        "Selecciona una tienda arriba en el buscador para modificar sus conexiones."
                    )

            # TAB 3: ELIMINAR (Independiente de la selección superior)
            with tab3:
                st.subheader("Eliminar una conexión")
                tienda_del = st.selectbox(
                    "Selecciona la tienda:",
                    tiendas,
                    index=None,
                    placeholder="Elige una tienda para eliminar...",
                    key="del_tienda_sel",
                )

                if tienda_del:
                    regs_del = [
                        d for d in datos if get_val(d, "tienda") == tienda_del
                    ]
                    regs_del = ordenar_registros(regs_del)

                    opciones_del = [
                        f"Caja: {get_val(r, 'caja')} | Conexión: {get_val(r, 'conexion')}"
                        for r in regs_del
                    ]
                    seleccion_del = st.selectbox(
                        "Selecciona la caja/conexión específica a eliminar:",
                        opciones_del,
                        key="del_conexion_sel",
                    )

                    if seleccion_del:
                        idx_sel = opciones_del.index(seleccion_del)
                        registro_a_eliminar = regs_del[idx_sel]

                        if st.button(
                            "❌ Eliminar Conexión Definitivamente",
                            type="primary",
                            key="btn_del",
                        ):
                            datos.remove(registro_a_eliminar)
                            guardar_datos(datos)
                            st.rerun()
