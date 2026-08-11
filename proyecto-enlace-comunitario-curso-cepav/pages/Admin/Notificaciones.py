import streamlit as st
from datetime import date, datetime
from controllers.notificaciones_controller import NotificacionesController

controller = NotificacionesController()

st.title("Notificaciones")
st.divider()

with st.form("agregar_notificacion"):
    titulo = st.text_input("Título")
    mensaje = st.text_area("Mensaje")
    publicar = st.form_submit_button("Publicar")


    if publicar:
        if titulo == "" or mensaje == "":
            st.warning("Por favor, complete todos los campos.")
        else:
            controller.agregar_notificacion(
                titulo, mensaje, str(date.today()))
            st.success("Notificación agregada con éxito.")
            st.rerun()
st.divider()
st.subheader("Notificaciones publicadas")
notificaciones = controller.obtener_notificaciones()
if not notificaciones:
    st.info("No hay notificaciones publicadas.")
else:
    for n in notificaciones:
        with st.container(border=True):
            st.markdown(f"**{n['titulo']}**")
            st.write(f"{n['mensaje']}")
            st.caption(
                f"Publicado el: {n['fecha']} · "
                f"Vistas: {n.get('vistas', 0)}"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                editar = st.button("Editar", key=f"editar_{n['id']}")
            with col2:
                eliminar = st.button("Eliminar", key=f"eliminar_{n['id']}")
                if eliminar:
                    controller.eliminar_notificacion(n['id'])
                    st.success("Notificación eliminada con éxito.")
                    st.rerun()
            with st.expander(f"Ver quién la vio ({n.get('vistas', 0)})"):
                vistas = controller.obtener_vistas_detalle(n['id'])
                if not vistas:
                    st.write("Aún nadie ha visto esta notificación.")
                else:
                    for v in vistas:
                        persona = (
                            f"{v.get('nombre') or ''} {v.get('apellido') or ''}".strip()
                            or v.get("usuario")
                            or "Desconocido"
                        )
                        cedula = v.get("cedula") or v.get("usuario") or "—"
                        st.write(f"• {persona} (C.I. {cedula}) — {v['fecha_vista']}")
            if editar or st.session_state.get(f"editando_{n['id']}", False):
                st.session_state[f"editando_{n['id']}"] = True
                nuevo_titulo = st.text_input(
                    "Título", value=n['titulo'], key=f"titulo_{n['id']}"
                )
                nuevo_mensaje = st.text_area(
                    "Mensaje", value=n['mensaje'], key=f"mensaje_{n['id']}"
                )
                if st.button("Guardar cambios", key=f"guardar_{n['id']}"):
                    if nuevo_titulo == "" or nuevo_mensaje == "":
                        st.warning("Por favor, complete todos los campos.")
                    else:
                        controller.actualizar_notificacion(
                            n['id'], nuevo_titulo, nuevo_mensaje
                        )
                        st.success("Notificación actualizada con éxito.")
                        st.session_state[f"editando_{n['id']}"] = False
                        st.rerun()