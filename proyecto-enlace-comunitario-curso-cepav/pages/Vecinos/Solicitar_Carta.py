import streamlit as st
from controllers.solicitudes_controller import SolicitudesController

controller = SolicitudesController()
usuario = st.session_state.get("usuario") or {}
usuario_cedula = usuario.get("cedula", "")

st.title("Solicitar Carta")

tipos = controller.obtener_tipos()
opciones = {tipo["nombre"]: tipo["id"] for tipo in tipos}

tipo = st.selectbox("Seleccione tipo de solicitud", list(opciones.keys()))

if st.button("Solicitar"):
    if controller.tiene_solicitud_activa(usuario_cedula, opciones[tipo]):
        st.error("Ya tiene una solicitud activa de este tipo. Espere a que sea atendida.")
    else:
        controller.crear_solicitud(usuario_cedula, opciones[tipo], tipo)
        st.success("Solicitud enviada correctamente")
