import streamlit as st
from datetime import date
from controllers.cartas_controller import CartasController
from services import carta_pdf


controller = CartasController()
cartas = controller.listar()
st.title("Gestión de Cartas")
busqueda_de_cartas = st.text_input(
    "Buscar solicitudes de cartas"
)

if busqueda_de_cartas:
    cartas = controller.buscar_solicitud(busqueda_de_cartas)
else:
    cartas = controller.listar() 

st.metric(
    "Solicitudes registradas",
    len(cartas)
)

if not cartas:
    st.info("No hay solicitudes de cartas")
else:
    hoy = date.today()
    for carta in cartas:
        fecha_solicitud = carta.get("fecha_solicitud")
        es_nueva = (
            fecha_solicitud is not None
            and (hoy - fecha_solicitud).days <= 2
        )
        if es_nueva:
            st.markdown(
                '<div style="background-color:#d1f2e0;color:#145a32;font-weight:700;'
                'padding:4px 12px;border-radius:6px;margin-bottom:4px;">'
                "NUEVA SOLICITUD</div>",
                unsafe_allow_html=True,
            )
        with st.container(border=True):
            col_info, col_accion, col_pdf = st.columns([4, 1, 1])
            with col_info:
                st.markdown(f"**ID {carta['id']}** — {carta.get('tipo_carta', 'N/A')}")
                habitante = carta.get("habitante_nombre") or ""
                if habitante:
                    nombre_mostrar = f"{habitante} {carta.get('habitante_apellido', '')}".strip()
                else:
                    nombre_mostrar = carta.get("usuario", "N/A")
                st.caption(
                    f"Usuario: {nombre_mostrar} · "
                    f"Estado: {carta.get('estado', 'N/A')} · "
                    f"Fecha: {carta.get('fecha_solicitud', 'N/A')}"
                )
            with col_accion:
                estado_actual = carta.get("estado", "Pendiente")
                if estado_actual in ("Aprobada", "Rechazada", "Requiere actualización"):
                    st.caption("Registro")
                else:
                    opciones = ["Pendiente", "Aprobar", "Rechazar", "En revisión"]
                    indices = {"Pendiente": 0, "Aprobada": 1, "Rechazada": 2, "En revisión": 3}
                    seleccion = st.selectbox(
                        "Gestión",
                        opciones,
                        index=indices.get(estado_actual, 0),
                        key=f"estado_{carta['id']}_{estado_actual}",
                    )
                    if seleccion == "Aprobar" and estado_actual != "Aprobada":
                        controller.aprobar(carta["id"])
                        st.success(f"Solicitud {carta['id']} aprobada")
                        st.rerun()
                    elif seleccion == "Rechazar" and estado_actual != "Rechazada":
                        controller.rechazar(carta["id"])
                        st.success(f"Solicitud {carta['id']} rechazada")
                        st.rerun()
                    elif seleccion == "En revisión" and estado_actual != "En revisión":
                        controller.en_revision(carta["id"])
                        st.success(f"Solicitud {carta['id']} en revisión")
                        st.rerun()
            with col_pdf:
                if estado_actual == "Aprobada":
                    datos_vecino = {
                        "nombre": carta.get("habitante_nombre") or "",
                        "apellido": carta.get("habitante_apellido") or "",
                        "cedula": carta.get("usuario") or "",
                        "direccion": carta.get("habitante_direccion") or "",
                        "estado_civil": carta.get("habitante_estado_civil") or "",
                        "profesion": carta.get("habitante_profesion") or "",
                    }
                    try:
                        pdf = carta_pdf.generar_carta(
                            carta.get("tipo_carta"), datos_vecino
                        )
                    except ValueError as e:
                        st.error(str(e))
                    else:
                        st.download_button(
                            "Descargar",
                            data=pdf,
                            file_name=carta_pdf.nombre_archivo(
                                carta.get("tipo_carta"), datos_vecino
                            ),
                            mime="application/pdf",
                            key=f"dl_pdf_{carta['id']}",
                            use_container_width=True,
                        )