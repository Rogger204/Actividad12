import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Configuración de conexión (Lee de los Secrets de Streamlit Cloud)
# Asegúrate de tener SUPABASE_URL y SUPABASE_KEY en los Settings de tu App
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

st.set_page_config(page_title="Catálogo de Juegos", layout="wide")

# 2. Función de Auth (Adaptada para Supabase)
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
        st.sidebar.write(f"Logueado: {st.session_state['user'].email}")
        if st.sidebar.button("Cerrar sesión"):
            supabase.auth.sign_out()
            del st.session_state['user']
            st.rerun()

show_auth()

# 3. Interfaz Principal
st.title("🎮 Catálogo de Juegos")

if 'user' not in st.session_state:
    st.info("Inicia sesión en la barra lateral.")
else:
    # Formulario para registrar datos en Supabase
    with st.form("agregar_juego"):
        nombre = st.text_input("Nombre del Juego")
        consola = st.selectbox("Consola", ["PS5", "Xbox", "Switch", "PC"])
        precio = st.number_input("Precio", min_value=0.0)
        url_img = st.text_input("URL de la imagen")
        
        if st.form_submit_button("Guardar"):
            data = {
                "nombre_juego": nombre,
                "consola": consola,
                "precio": float(precio),
                "imagen_url": url_img,
                "registrado_por": st.session_state['user'].email
            }
            # ESTA ES LA FORMA CORRECTA PARA SUPABASE
            supabase.table("catalogo_juegos").insert(data).execute()
            st.success("Juego guardado!")

    # Área de análisis (Gráficos y tablas)
    st.divider()
    if st.button("Actualizar Análisis"):
        st.cache_data.clear()

    @st.cache_data
    def get_data():
        # ESTA ES LA FORMA CORRECTA PARA SUPABASE
        response = supabase.table("catalogo_juegos").select("*").execute()
        return pd.DataFrame(response.data)

    df = get_data()
    st.write(f"Última actualización: {pd.Timestamp.now()}")
    
    if not df.empty:
        st.dataframe(df)
        st.line_chart(df.set_index('nombre_juego')['precio'])
