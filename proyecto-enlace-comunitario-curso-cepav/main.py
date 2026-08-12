import streamlit as st
from pathlib import Path
from controllers.login_controller import Login
from migrations.migrador import ejecutar_migraciones

st.set_page_config(
    page_title="Enlace Comunitario",
    page_icon=":material/groups:",
    layout="wide",
)

LOGO = Path(__file__).resolve().parent / "templates" / "Enlace.png"

if "migraciones_ok" not in st.session_state:
    try:
        ejecutar_migraciones()
        st.session_state.migraciones_ok = True
    except Exception as e:
        st.error(f"No se pudo inicializar la base de datos: {e}")
        st.stop()

login = Login()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False 
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "rol" not in st.session_state:
    st.session_state.rol = None
if "cambiar_password" not in st.session_state:
    st.session_state.cambiar_password = False


login_page = st.Page("pages/login.py", title="Iniciar Sesión", icon=":material/login:")
cambiar_page = st.Page("pages/cambiar_password.py", title="Cambiar Contraseña", icon=":material/password:")

if st.session_state.logged_in:
    st.sidebar.image(str(LOGO), width=180)
    st.sidebar.markdown(
        f"### Bienvenido, {st.session_state.usuario['nombre']}"
    )
    st.sidebar.caption(
        "Administrador" if st.session_state.rol != "vecino" else "Vecino"
    )
    st.sidebar.divider()
    if st.session_state.cambiar_password:
        pg = st.navigation([cambiar_page], position="hidden")
        st.sidebar.page_link(cambiar_page)
    else:
        paginas = login.paginas_disponibles()
        pg = st.navigation(paginas, position="hidden")
        for pagina in paginas:
            st.sidebar.page_link(pagina)
else:
    pg = st.navigation([login_page], position="hidden")
    st.html(
        """
        <style>
        [data-testid="stSidebar"] { display: none; }
        </style>
        """
    )

pg.run()
