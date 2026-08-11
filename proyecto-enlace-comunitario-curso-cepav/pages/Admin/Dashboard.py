import streamlit as st
from controllers.habitantes_controller import HabitantesController
from controllers.cartas_controller import CartasController
from controllers.notificaciones_controller import NotificacionesController

habitantes = HabitantesController().get_habitantes()
cartas = CartasController().listar()
notificaciones = NotificacionesController().obtener_notificaciones()

st.title("Dashboard")

adultos = sum(1 for h in habitantes if h.get("categoria") == "Adulto")
nna = sum(1 for h in habitantes if h.get("categoria") == "NNA")
cartas_pendientes = sum(1 for c in cartas if c.get("estado") == "Pendiente")
cartas_aprobadas = sum(1 for c in cartas if c.get("estado") == "Aprobada")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Habitantes", len(habitantes))
col2.metric("Adultos / NNA", f"{adultos} / {nna}")
col3.metric("Cartas Pendientes", cartas_pendientes)
col4.metric("Cartas Aprobadas", cartas_aprobadas)

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Últimas Notificaciones")
    if not notificaciones:
        st.info("No hay notificaciones publicadas.")
    for n in notificaciones[:3]:
        with st.container(border=True):
            st.markdown(f"**{n['titulo']}**")
            st.caption(f"{n['mensaje']} — {n['fecha']}")

with col_b:
    st.subheader("Cartas Recientes")
    if not cartas:
        st.info("No hay solicitudes de cartas.")
    for c in cartas[:3]:
        solicitante = c.get("habitante_nombre") or c.get("usuario", "N/A")
        with st.container(border=True):
            st.markdown(f"**{c.get('tipo_carta', 'N/A')}** — {solicitante}")
            st.caption(f"Fecha: {c.get('fecha_solicitud', 'N/A')}")
            st.badge(c.get("estado", "N/A"))

st.divider()

st.subheader("Actividades recientes")
actividades = []
for c in cartas[:3]:
    solicitante = c.get("habitante_nombre") or c.get("usuario", "N/A")
    actividades.append(f"{solicitante} solicitó una carta de {c.get('tipo_carta', 'N/A')}")
habitantes_recientes = sorted(
    habitantes, key=lambda h: h.get("created_at") or "", reverse=True
)
for h in habitantes_recientes[:3]:
    actividades.append(f"{h['nombre_completo']} fue registrado/a.")
if not actividades:
    st.info("Sin actividades recientes.")
else:
    for actividad in actividades:
        st.info(actividad)
