import streamlit as st
from controllers.solicitudes_controller import SolicitudesController
from services import carta_pdf

controller = SolicitudesController()
usuario = st.session_state.get("usuario") or {}
usuario_cedula = usuario.get("cedula", "")

st.title("Mis Solicitudes")

if st.session_state.pop("solicitud_creada", False):
    st.success("Solicitud enviada correctamente.")

if st.button("+ Nueva Solicitud", type="primary"):
    st.session_state.mostrar_formulario = True

if st.session_state.get("mostrar_formulario"):
    tipos = controller.obtener_tipos()
    opciones = {tipo["nombre"]: tipo["id"] for tipo in tipos}
    with st.form("nueva_solicitud"):
        st.subheader("Crear Nueva Solicitud")
        tipo = st.selectbox("Tipo de solicitud", list(opciones.keys()))
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Enviar")
        with col2:
            cancel = st.form_submit_button("Cancelar")

        if submitted:
            if not usuario_cedula:
                st.error("No se pudo identificar tu cédula. Cierra sesión y vuelve a entrar.")
            elif controller.tiene_solicitud_activa(usuario_cedula, opciones[tipo]):
                st.error("Ya tiene una solicitud activa de este tipo. Espere a que sea atendida.")
            else:
                try:
                    controller.crear_solicitud(usuario_cedula, opciones[tipo], tipo)
                except Exception as e:
                    if "idx_solicitudes_activas_unicas" in str(e):
                        st.error(
                            "Ya tiene una solicitud activa de este tipo. "
                            "Espere a que sea atendida."
                        )
                    else:
                        print(f"[solicitudes] Error al crear solicitud: {e}", flush=True)
                        st.error(f"No se pudo registrar la solicitud: {e}")
                else:
                    st.session_state.mostrar_formulario = False
                    st.session_state.solicitud_creada = True
                    st.rerun()

        if cancel:
            st.session_state.mostrar_formulario = False
            st.rerun()

st.divider()

solicitudes = controller.obtener_solicitudes_usuario(usuario_cedula)

if not solicitudes:
    st.info("No tienes solicitudes registradas.")
else:
    for sol in solicitudes:
        fecha = sol["fecha_solicitud"].strftime("%d/%m/%Y")
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{sol['tipo_nombre'] or sol['tipo_carta']}**")
                st.caption(f"Solicitada el {fecha}")
            with col2:
                st.badge(sol["estado"])
            with col3:
                if sol["estado"] == "Aprobada":
                    datos_vecino = {
                        "nombre": usuario.get("nombre") or "",
                        "apellido": usuario.get("apellido") or "",
                        "cedula": usuario_cedula,
                        "direccion": usuario.get("direccion") or "",
                        "estado_civil": usuario.get("estado_civil") or "",
                        "profesion": usuario.get("profesion") or "",
                    }
                    try:
                        pdf = carta_pdf.generar_carta(
                            sol.get("tipo_nombre") or sol.get("tipo_carta"), datos_vecino
                        )
                    except ValueError as e:
                        st.error(str(e))
                    else:
                        st.download_button(
                            "Descargar",
                            data=pdf,
                            file_name=carta_pdf.nombre_archivo(
                                sol.get("tipo_nombre") or sol.get("tipo_carta"), datos_vecino
                            ),
                            mime="application/pdf",
                            key=f"dl_pdf_{sol['id']}",
                            use_container_width=True,
                        )
