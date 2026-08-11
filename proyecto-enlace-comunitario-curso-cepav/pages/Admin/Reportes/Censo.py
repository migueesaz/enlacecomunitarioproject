import streamlit as st
from datetime import date

import pandas as pd

from controllers.reportes_controller import (
    ESTADOS_SOLICITUD,
    ReportesController,
)

st.title("Informes y Reportes")
st.caption("Genera informes del consejo comunal y filtra por rango de fechas y otros criterios.")


def _rango_fechas(label, default_desde=None):
    hoy = date.today()
    desde_defecto = default_desde or date(2020, 1, 1)
    rango = st.date_input(
        label,
        value=(desde_defecto, hoy),
        min_value=date(2000, 1, 1),
        max_value=hoy,
    )
    if isinstance(rango, tuple):
        desde, hasta = rango
    else:
        desde, hasta = rango, rango
    return desde, hasta


def _rango_edad(edad):
    if edad is None:
        return "Sin dato"
    if edad < 18:
        return "0-17"
    if edad < 30:
        return "18-29"
    if edad < 45:
        return "30-44"
    if edad < 60:
        return "45-59"
    return "60+"


def _tabla(df, columnas):
    st.dataframe(df[columnas], width="stretch", hide_index=True)


def _reporte_censo(ctrl):
    st.subheader("Censo de Población")
    st.caption("Evolución y composición de la población registrada en la comunidad.")

    desde, hasta = _rango_fechas("Rango de fechas (fecha de registro)")
    filtro_sexo = st.selectbox("Sexo", ["Todos", "M", "F"])
    filtro_categoria = st.selectbox("Categoría", ["Todos", "Adulto", "NNA", "N/A"])

    df = pd.DataFrame(ctrl.censo(desde, hasta))
    if df.empty:
        st.info("No hay habitantes registrados en el período seleccionado.")
        return

    if filtro_sexo != "Todos":
        df = df[df["genero"] == filtro_sexo]
    if filtro_categoria != "Todos":
        df = df[df["categoria"] == filtro_categoria]

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("Adultos", int((df["categoria"] == "Adulto").sum()))
    c3.metric("NNA", int((df["categoria"] == "NNA").sum()))
    c4.metric("Hombres / Mujeres", f"{int((df['genero'] == 'M').sum())} / {int((df['genero'] == 'F').sum())}")

    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Por categoría**")
        cat = df["categoria"].value_counts().reindex(["Adulto", "NNA", "N/A"], fill_value=0)
        st.bar_chart(cat)
    with g2:
        st.markdown("**Por sexo**")
        st.bar_chart(df["genero"].value_counts())

    g3, g4 = st.columns(2)
    with g3:
        st.markdown("**Por rango de edad**")
        df["rango_edad"] = df["edad"].map(_rango_edad)
        orden_edad = ["0-17", "18-29", "30-44", "45-59", "60+", "Sin dato"]
        edades = df["rango_edad"].value_counts().reindex(orden_edad, fill_value=0)
        st.bar_chart(edades)
    with g4:
        st.markdown("**Por estado civil**")
        estado_civil = df["estado_civil"].fillna("Sin dato").value_counts()
        st.bar_chart(estado_civil)

    st.divider()
    st.markdown("**Profesiones más frecuentes**")
    profesiones = df["profesion"].dropna().replace("", "Sin dato").value_counts().head(10)
    if profesiones.empty:
        st.caption("Sin datos de profesión.")
    else:
        st.bar_chart(profesiones)

    st.divider()
    st.markdown("**Detalle del censo**")
    _tabla(
        df,
        ["cedula", "nombre", "apellido", "edad", "categoria", "genero", "estado_civil", "profesion", "direccion_1"],
    )


def _reporte_solicitudes(ctrl, solo_aprobadas=False):
    if solo_aprobadas:
        st.subheader("Cartas Aprobadas")
        st.caption("Cartas emitidas por el consejo comunal en el período seleccionado.")
    else:
        st.subheader("Solicitudes de Cartas")
        st.caption("Trámites solicitados por los vecinos según tipo y estado.")

    desde, hasta = _rango_fechas("Rango de fechas (fecha de solicitud)")
    tipos = ctrl.tipos_solicitud()
    opciones_tipo = ["Todos"] + [t["nombre"] for t in tipos]
    filtro_tipo = st.selectbox("Tipo de carta", opciones_tipo)

    if solo_aprobadas:
        filtro_estado = "Aprobada"
    else:
        filtro_estado = st.selectbox("Estado", ["Todos"] + list(ESTADOS_SOLICITUD))

    tipo_id = None
    if filtro_tipo != "Todos":
        tipo_id = next(t["id"] for t in tipos if t["nombre"] == filtro_tipo)

    df = pd.DataFrame(
        ctrl.solicitudes(
            desde,
            hasta,
            estado=None if filtro_estado == "Todos" else filtro_estado,
            tipo_id=tipo_id,
        )
    )
    if df.empty:
        st.info("No hay solicitudes en el período seleccionado.")
        return

    df["tipo_display"] = df["tipo_nombre"].fillna(df["tipo_carta"])

    st.divider()
    if solo_aprobadas:
        c1, c2 = st.columns(2)
        c1.metric("Cartas aprobadas", len(df))
        c2.metric("Solicitantes distintos", df["cedula"].nunique())
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c2.metric("Pendientes", int((df["estado"] == "Pendiente").sum()))
        c3.metric("En revisión", int((df["estado"] == "En revisión").sum()))
        c4.metric("Aprobadas", int((df["estado"] == "Aprobada").sum()))

    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Por tipo de carta**")
        st.bar_chart(df["tipo_display"].value_counts())
    with g2:
        if solo_aprobadas:
            st.markdown("**Aprobadas por mes**")
            df["mes"] = pd.to_datetime(df["fecha_solicitud"]).dt.to_period("M").astype(str)
            st.bar_chart(df["mes"].value_counts().sort_index())
        else:
            st.markdown("**Por estado**")
            estados = df["estado"].value_counts().reindex(ESTADOS_SOLICITUD, fill_value=0)
            st.bar_chart(estados)

    st.divider()
    st.markdown("**Evolución mensual de solicitudes**")
    df["mes"] = pd.to_datetime(df["fecha_solicitud"]).dt.to_period("M").astype(str)
    serie = df["mes"].value_counts().sort_index()
    if len(serie) > 1:
        st.line_chart(serie)
    else:
        st.caption("Solo hay datos para un mes en el período seleccionado.")

    st.divider()
    st.markdown("**Detalle de solicitudes**")
    _tabla(
        df,
        ["fecha_solicitud", "cedula", "nombre", "apellido", "tipo_display", "estado"],
    )


def _reporte_usuarios(ctrl):
    st.subheader("Usuarios y Accesos")
    st.caption("Cuentas de acceso al sistema creadas en el período seleccionado.")

    desde, hasta = _rango_fechas("Rango de fechas (fecha de creación de la cuenta)")
    filtro_rol = st.selectbox("Rol", ["Todos", "admin", "vecino"])

    df = pd.DataFrame(ctrl.usuarios(desde, hasta))
    if df.empty:
        st.info("No hay usuarios creados en el período seleccionado.")
        return

    if filtro_rol != "Todos":
        df = df[df["rol"] == filtro_rol]

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cuentas", len(df))
    c2.metric("Activas", int((df["activo"] == True).sum()))  # noqa: E712
    c3.metric("Bloqueadas", int((df["bloqueado"] == True).sum()))  # noqa: E712
    c4.metric("Han iniciado sesión", df["ultimo_ingreso"].notna().sum())

    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Cuentas por rol**")
        st.bar_chart(df["rol"].value_counts())
    with g2:
        st.markdown("**Cuentas creadas por mes**")
        fechas = df["fecha_creacion"]
        if isinstance(fechas.dtype, pd.DatetimeTZDtype):
            fechas = fechas.dt.tz_localize(None)
        df["mes"] = pd.to_datetime(fechas).dt.to_period("M").astype(str)
        st.bar_chart(df["mes"].value_counts().sort_index())

    st.divider()
    st.markdown("**Detalle de usuarios**")
    _tabla(
        df,
        ["cedula", "nombre", "apellido", "correo", "rol", "activo", "bloqueado", "ultimo_ingreso"],
    )


def _reporte_notificaciones(ctrl):
    st.subheader("Notificaciones y Alcance")
    st.caption("Publicaciones del consejo comunal y su alcance entre los vecinos.")

    desde, hasta = _rango_fechas("Rango de fechas (fecha de publicación)")

    df = pd.DataFrame(ctrl.notificaciones(desde, hasta))
    if df.empty:
        st.info("No hay notificaciones en el período seleccionado.")
        return

    total_vistas = int(df["vistas"].sum())
    n_vistas_detalle = sum(len(ctrl.vistas_detalle(n_id)) for n_id in df["id"])

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Publicadas", len(df))
    c2.metric("Vistas totales", total_vistas)
    c3.metric("Vistas registradas", n_vistas_detalle)

    st.divider()
    st.markdown("**Vistas por notificación**")
    vistas = df.set_index("titulo")["vistas"].sort_values(ascending=False)
    st.bar_chart(vistas)

    st.divider()
    st.markdown("**Detalle de notificaciones**")
    _tabla(df, ["fecha", "titulo", "vistas"])

    st.divider()
    st.markdown("**¿Quién vio cada notificación?**")
    for _, n in df.iterrows():
        with st.expander(f"{n['fecha']} — {n['titulo']} ({n['vistas']} vistas)"):
            detalle = ctrl.vistas_detalle(n["id"])
            if not detalle:
                st.caption("Sin vistas registradas.")
            else:
                det_df = pd.DataFrame(detalle)
                _tabla(det_df, ["notificacion", "cedula", "nombre", "apellido", "fecha_vista"])


opciones = [
    "Censo de Población",
    "Solicitudes de Cartas",
    "Cartas Aprobadas",
    "Usuarios y Accesos",
    "Notificaciones y Alcance",
]

reporte = st.segmented_control(
    "Tipo de informe",
    options=opciones,
    default="Censo de Población",
    selection_mode="single",
    label_visibility="collapsed",
)

ctrl = ReportesController()

if reporte == "Censo de Población":
    _reporte_censo(ctrl)
elif reporte == "Solicitudes de Cartas":
    _reporte_solicitudes(ctrl)
elif reporte == "Cartas Aprobadas":
    _reporte_solicitudes(ctrl, solo_aprobadas=True)
elif reporte == "Usuarios y Accesos":
    _reporte_usuarios(ctrl)
elif reporte == "Notificaciones y Alcance":
    _reporte_notificaciones(ctrl)
