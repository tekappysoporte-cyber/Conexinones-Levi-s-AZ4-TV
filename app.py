import streamlit as st
import json

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
        st.cache_data.clear() # Limpia la memoria caché
        st.success("✅ Cambios guardados correctamente.")
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")

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
        # Selector de Tienda
        tiendas = sorted(list(set(d["tienda"] for d in datos)))
        tienda_seleccionada = st.selectbox("🔎 Selecciona o escribe el nombre de la tienda:", tiendas)

        if tienda_seleccionada:
            registros = [d for d in datos if d["tienda"] == tienda_seleccionada]
            principal = next((d for d in registros if d["caja"].upper() in ["MAIN", "MAIN1"]), registros[0])
            secundarias = [d for d in registros if d != principal]

            # --- CONEXIÓN PRINCIPAL ---
            st.markdown("---")
            st.subheader("⭐ Conexión Principal")
            
            col1, col2, col3 = st.columns([1.5, 2, 1.2])
            
            with col1:
                st.caption("Tienda")
                st.markdown(f"## {principal['tienda']}")
            
            with col2:
                st.caption("Código de Conexión")
                st.code(principal['conexion'], language="")
            
            with col3:
                st.caption("Tipo de Caja")
                st.markdown(f"## Caja {principal['caja']}")

            # --- OTRAS CONEXIONES DISPONIBLES (Formato Limpio + Botón Copiar) ---
            if secundarias:
                st.markdown("---")
                st.subheader("📦 Otras Conexiones Disponibles")
                
                # Encabezados de la tabla
                c_head1, c_head2 = st.columns([1, 4])
                with c_head1:
                    st.caption("**Caja**")
                with c_head2:
                    st.caption("**Código de Conexión**")
                
                st.markdown("<hr style='margin: 0 0 10px 0; border: 0.5px solid #333;'>", unsafe_allow_html=True)

                # Filas de la tabla con botón de copia
                for item in secundarias:
                    col_a, col_b = st.columns([1, 4])
                    with col_a:
                        st.markdown(f"**{item['caja']}**")
                    with col_b:
                        # Cuadro interactivo con icono de copiar integrado
                        st.code(item['conexion'], language="")

        # --- PANEL DE ADMINISTRACIÓN ---
        st.markdown("---")
        with st.expander("🛠️ Panel de Gestión (Crear, Modificar, Eliminar Conexión)"):
            tab1, tab2, tab3 = st.tabs(["➕ Crear Nueva", "✏️ Modificar Existente", "🗑️ Eliminar Conexión"])

            # TAB 1: CREAR
            with tab1:
                st.subheader("Agregar una nueva conexión")
                nueva_tienda = st.text_input("Nombre de la Tienda:")
                nueva_conexion = st.text_input("Código de Conexión (ej: PCLO...):")
                nueva_caja = st.text_input("Caja (ej: MAIN, C1, C2):")

                if st.button("Guardar Nueva Conexión"):
                    if nueva_tienda and nueva_conexion and nueva_caja:
                        nuevo_registro = {
                            "tienda": nueva_tienda.strip(),
                            "conexion": nueva_conexion.strip(),
                            "caja": nueva_caja.strip()
                        }
                        datos.append(nuevo_registro)
                        guardar_datos(datos)
                        st.rerun()
                    else:
                        st.warning("Por favor completa todos los campos.")

            # TAB 2: MODIFICAR
            with tab2:
                st.subheader("Modificar una conexión existente")
                if 'registros' in locals() and registros:
                    opciones_mod = [f"{r['caja']} - {r['conexion']}" for r in registros]
                    seleccion_mod = st.selectbox("Selecciona la caja a modificar de la tienda actual:", opciones_mod)
                    
                    registro_actual = registros[opciones_mod.index(seleccion_mod)]

                    mod_tienda = st.text_input("Tienda:", value=registro_actual["tienda"])
                    mod_conexion = st.text_input("Conexión:", value=registro_actual["conexion"])
                    mod_caja = st.text_input("Caja:", value=registro_actual["caja"])

                    if st.button("Actualizar Conexión"):
                        idx = datos.index(registro_actual)
                        datos[idx] = {
                            "tienda": mod_tienda.strip(),
                            "conexion": mod_conexion.strip(),
                            "caja": mod_caja.strip()
                        }
                        guardar_datos(datos)
                        st.rerun()

            # TAB 3: ELIMINAR
            with tab3:
                st.subheader("Eliminar una conexión")
                if 'registros' in locals() and registros:
                    opciones_del = [f"{r['caja']} - {r['conexion']}" for r in registros]
                    seleccion_del = st.selectbox("Selecciona la caja a eliminar de la tienda actual:", opciones_del, key="del_sel")
                    
                    registro_a_eliminar = registros[opciones_del.index(seleccion_del)]

                    if st.button("❌ Eliminar Conexión Definitivamente", type="primary"):
                        datos.remove(registro_a_eliminar)
                        guardar_datos(datos)
                        st.rerun()
