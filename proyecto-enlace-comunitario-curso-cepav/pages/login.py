import streamlit as st
from pathlib import Path
from controllers.login_controller import Login

st.set_page_config(
    page_title="Enlace Comunitario",
    page_icon=":material/groups:",
    layout="wide",
)

login = Login()

LOGO = Path(__file__).resolve().parent.parent / "templates" / "Transparente.png"

st.html(
    """
    <style>
    .stMainBlockContainer {
        padding-top: 2.75rem !important;
        padding-bottom: 0 !important;
    }
    .st-key-logo {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """
)

st.title("Enlace Comunitario", text_alignment="center")
st.caption(
    "Conectando a los vecinos de CEPAV para construir una comunidad más fuerte.",
    text_alignment="center",
)

hero, form_col = st.columns([1, 1], gap="small", vertical_alignment="center")

with hero:
    with st.container(key="logo"):
        st.image(str(LOGO), width="stretch")

with form_col:
    with st.container(horizontal_alignment="center", border=True, width="stretch"):
        st.markdown(":material/handshake: Conecta con los vecinos de tu comunidad")
        st.markdown(":material/request_page: Gestiona solicitudes y trámites")
        st.markdown(":material/notifications: Recibe notificaciones importantes")
    st.space("small")
    with st.container(border=True, width="stretch"):
        st.header("Iniciar sesión", text_alignment="center")
        st.caption(
            "Ingresa con tu cuenta para continuar",
            text_alignment="center",
        )
        with st.form("login_form"):
            correo = st.text_input(
                "Correo electrónico",
                placeholder="nombre@correo.com",
                icon=":material/mail:",
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                icon=":material/lock:",
            )
            submit = st.form_submit_button(
                "Iniciar sesión",
                type="primary",
                icon=":material/login:",
                width="stretch",
            )

            if submit:
                if not correo or not password:
                    st.error(
                        "Ingresa tu correo y contraseña para continuar.",
                        icon=":material/error:",
                    )
                else:
                    login.iniciar_sesion(correo, password)

        st.caption(
            "¿Problemas para acceder? Contacta al administrador de la comunidad.",
            text_alignment="center",
        )
