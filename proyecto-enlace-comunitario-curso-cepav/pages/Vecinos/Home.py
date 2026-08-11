import streamlit as st

st.title(f"Bienvenido a la plataforma de Enlace Comunitario")
st.divider()

st.markdown(
    """
    <div style="position: fixed; bottom: 16px; right: 16px; z-index: 100;
                background-color: rgba(240, 242, 246, 0.85); color: #666;
                padding: 8px 12px; border-radius: 8px; font-size: 12px;
                max-width: 280px; box-shadow: 0 1px 3px rgba(0,0,0,0.15);">
        Nota: si haces cambios en tu perfil, tendrás que solicitar una carta nueva.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("Esta plataforma está diseñada para facilitar la gestión de cartas de residencia y el registro de habitantes en la comunidad. A continuación, se presentan algunas de las funcionalidades disponibles:")
st.write("- **Gestión de cartas de residencia:** Los administradores pueden revisar, aprobar o rechazar solicitudes de cartas de residencia.")
