import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Configuración de conexión (Usando Secrets de Streamlit)
# Asegúrate de cargar tus credenciales en los 'Settings > Secrets' de tu app en Streamlit Cloud
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Catálogo de Juegos Pro", layout="wide")

# 2. Lógica de Autenticación
def show_auth():
    st.sidebar.title("👤 Acceso")
    if 'user' not in st.session_state:
        menu = st.sidebar.radio("Acción", ["Entrar", "Registrar"])
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Contraseña", type="password")
        
        if st.sidebar.button("Enviar"):
            try:
                if menu == "Registrar":
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.sidebar.success("Cuenta creada. Verifica tu correo.")
                else:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['user'] = res.user
                    st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.write(f"Logueado como: {st.session_state['user'].email}")
        if st.sidebar.button("Cerrar sesión"):
            supabase.auth.sign_out()
            del st.session_state['user']
            st.rerun()

show_auth()

# 3. Interfaz Principal
st.title("🎮 Catálogo de Juegos Pro")

if 'user' not in st.session_state:
    st.info("Inicia sesión en la barra lateral para registrar juegos.")
else:
    # Formulario para registrar datos
    with st.form("agregar_juego"):
        st.subheader("Registrar nuevo juego")
        nombre = st.text_input("Nombre del Juego")
        consola = st.selectbox("Consola", ["PS5", "Xbox", "Switch", "PC"])
        precio = st.number_input("Precio", min_value=0.0)
        url_img = st.text_input("URL de la imagen")
        
        if st.form_submit_button("Guardar Juego"):
            data = {
                "nombre_juego": nombre,
                "consola": consola,
                "precio": precio,
                "imagen_url": url_img,
                "registrado_por": st.session_state['user'].email
            }
            supabase.table("catalogo_juegos").insert(data).execute()
            st.success("Juego guardado!")

    # Área de Análisis
    st.divider()
    st.subheader("📊 Área de Análisis")
    
    # Botón para actualizar manualmente los datos del job de Databricks
    if st.button("Actualizar Análisis"):
        st.cache_data.clear()

    @st.cache_data
    def get_data():
        response = supabase.table("catalogo_juegos").select("*").execute()
        return pd.DataFrame(response.data)

    df = get_data()
    
    if not df.empty:
        st.write(f"**Última actualización:** {pd.Timestamp.now()}")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df)
        with col2:
            st.line_chart(df.set_index('nombre_juego')['precio'])
    else:
        st.write("No hay juegos registrados.")