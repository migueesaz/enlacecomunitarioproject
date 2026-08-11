import streamlit as st
from controllers.notificaciones_controller import NotificacionesController

controller = NotificacionesController()

st.title("Mensajes")

notificaciones = controller.obtener_notificaciones()

usuario = st.session_state.get("usuario") or {}
usuario_habitante_id = usuario.get("habitante_id") if isinstance(usuario, dict) else None
leidas = controller.obtener_notificaciones_leidas(usuario_habitante_id)

for n in notificaciones:
    if n["id"] not in leidas:
        leidas.add(n["id"])
        controller.registrar_vista(n["id"], usuario_habitante_id)

if not notificaciones:
    st.info("No hay notificaciones publicadas.")
else:
    for n in notificaciones:
        with st.container(border=True):
            st.markdown(f"**{n['titulo']}**")
            st.write(n["mensaje"])
            st.caption(f"Publicado el: {n['fecha']}")
