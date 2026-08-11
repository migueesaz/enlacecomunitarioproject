import streamlit as st
from datetime import date
import pandas as pd
from controllers.habitantes_controller import HabitantesController as HC
from models.user_model import UserModel, validar_password

hclass = HC()
uclass = UserModel()
roles = hclass.get_roles() or []
opciones_rol = {r["nombre"]: r["id"] for r in roles}


@st.dialog("Registrar Habitante", width="large")
def dialog_registro():
    with st.form("form_registro_habitante"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre *", key="reg_nombre")
            apellido = st.text_input("Apellido *", key="reg_apellido")
            cedula = st.text_input("Cédula *", key="reg_cedula")
            sexo = st.selectbox("Sexo", ["M", "F"], key="reg_sexo")
        with c2:
            email = st.text_input("Email", key="reg_email")
            telefono = st.text_input("Teléfono", key="reg_telefono")
            fecha_nac = st.date_input(
                "Fecha de Nacimiento",
                value=date.today(),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                key="reg_fecha_nac",
            )
            rol = st.selectbox("Rol", list(opciones_rol.keys()), key="reg_rol")
        direccion = st.text_input("Dirección", key="reg_direccion")
        c1, c2 = st.columns(2)
        with c1:
            estado_civil = st.selectbox(
                "Estado civil",
                ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"],
                key="reg_estado_civil",
            )
        with c2:
            profesion = st.text_input("Profesión u oficio", key="reg_profesion")

        if st.form_submit_button("Registrar", type="primary"):
            if not nombre or not apellido or not cedula:
                st.error("Los campos nombre, apellido y cédula son obligatorios.")
            else:
                data = {
                    "nombre": nombre,
                    "apellido": apellido,
                    "cedula": cedula,
                    "genero": sexo,
                    "telefono1": telefono,
                    "direccion_1": direccion,
                    "email": email,
                    "fecha_nac": str(fecha_nac),
                    "rol_id": opciones_rol.get(rol),
                    "estado_civil": estado_civil,
                    "profesion": profesion,
                }
                hclass.create_habitante(data)
                st.session_state.registro_exito = f"{nombre} {apellido} registrado exitosamente."
                st.session_state.abrir_registro = False
                st.rerun()


with st.container(border=False):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Población Registrada")
    with col2:
        if st.button("Registrar Nuevo", type="primary"):
            st.session_state.abrir_registro = True

if st.session_state.get("abrir_registro"):
    dialog_registro()

exito = st.session_state.pop("registro_exito", None)
if exito:
    st.success(exito)

habitantes = hclass.get_habitantes()
busqueda = st.text_input("Buscar por nombre o cédula")

with st.expander("Ver población en el mapa", expanded=False):
    con_coordenadas = [
        h for h in (habitantes or [])
        if h.get("latitud") is not None and h.get("longitud") is not None
    ]
    if not con_coordenadas:
        st.info("Ningún habitante ha registrado su ubicación todavía. Se registra desde el perfil del vecino.")
    else:
        st.caption(f"{len(con_coordenadas)} habitante(s) con ubicación registrada.")
        mapa_df = pd.DataFrame(
            [
                {
                    "latitud": h["latitud"],
                    "longitud": h["longitud"],
                    "habitante": h["nombre_completo"],
                    "cedula": h["cedula"],
                }
                for h in con_coordenadas
            ]
        )
        st.map(mapa_df, latitude="latitud", longitude="longitud")
        with st.expander("Ver coordenadas"):
            st.dataframe(
                mapa_df[["habitante", "cedula", "latitud", "longitud"]],
                width="stretch",
                hide_index=True,
            )

if habitantes is None:
    st.warning("No hay habitantes registrados.")
    st.stop()

if busqueda:
    resultados = hclass.buscar_habitantes(busqueda)
else:
    resultados = hclass.get_habitantes()

if not resultados:
    st.info("No se encontraron habitantes.")
else:
    for h in resultados:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"**{h['nombre']} {h['apellido']}** — C.I. {h['cedula']}")
                categoria = h.get("categoria", "N/A")
                rol_nombre = h.get("rol_nombre") or "—"
                st.caption(f"Sexo: {h['genero']} · Rol: {rol_nombre} · Tel: {h.get('telefono_1', 'N/A')} · Dir: {h.get('direccion_1', 'N/A')} · Estado civil: {h.get('estado_civil') or '—'} · Profesión: {h.get('profesion') or '—'} · {categoria}")
            with col2:
                if st.button("Editar", key=f"edit_{h['cedula']}"):
                    st.session_state.pop(f"acceso_{h['cedula']}", None)
                    st.session_state.editando = h["cedula"]
            with col3:
                if st.button("Eliminar", key=f"del_{h['cedula']}", type="secondary"):
                    hclass.delete_habitante(h["id"])
                    st.success("Habitante eliminado correctamente.")
                    st.rerun()

            if st.session_state.get("editando") == h["cedula"]:
                usuario_acceso = uclass.obtener_usuario_por_habitante(h["id"])
                tiene_acceso = usuario_acceso is not None and bool(usuario_acceso.get("activo"))
                switch_acceso = st.toggle(
                    "Acceso al sistema",
                    value=tiene_acceso,
                    key=f"acceso_{h['cedula']}",
                    help="Activa el acceso para que el vecino pueda iniciar sesión.",
                )
                with st.form(f"form_edit_{h['cedula']}"):
                    lista_roles = list(opciones_rol.keys())
                    indice_rol = lista_roles.index(h["rol_nombre"]) if h.get("rol_nombre") in lista_roles else 0
                    c1, c2 = st.columns(2)
                    with c1:
                        e_nombre = st.text_input("Nombre", value=h["nombre"], key=f"e_nombre_{h['cedula']}")
                        e_apellido = st.text_input("Apellido", value=h["apellido"], key=f"e_apellido_{h['cedula']}")
                        e_sexo = st.selectbox("Sexo", ["M", "F"], index=0 if h["genero"] == "M" else 1, key=f"e_sexo_{h['cedula']}")
                        e_email = st.text_input("Email", value=h.get("email") or "", key=f"e_email_{h['cedula']}")
                        opciones_estado = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"]
                        indice_estado = opciones_estado.index(h.get("estado_civil")) if h.get("estado_civil") in opciones_estado else 0
                        e_estado_civil = st.selectbox("Estado civil", opciones_estado, index=indice_estado, key=f"e_estado_civil_{h['cedula']}")
                    with c2:
                        e_rol = st.selectbox("Rol", lista_roles, index=indice_rol, key=f"e_rol_{h['cedula']}")
                        e_tel = st.text_input("Teléfono", value=h.get("telefono_1") or "", key=f"e_tel_{h['cedula']}")
                        e_dir = st.text_input("Dirección", value=h.get("direccion_1") or "", key=f"e_dir_{h['cedula']}")
                        e_profesion = st.text_input("Profesión u oficio", value=h.get("profesion") or "", key=f"e_profesion_{h['cedula']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        e_latitud = st.number_input(
                            "Latitud",
                            value=h.get("latitud"),
                            format="%.6f",
                            step=0.000001,
                            min_value=-90.0,
                            max_value=90.0,
                            key=f"e_lat_{h['cedula']}",
                        )
                    with c2:
                        e_longitud = st.number_input(
                            "Longitud",
                            value=h.get("longitud"),
                            format="%.6f",
                            step=0.000001,
                            min_value=-180.0,
                            max_value=180.0,
                            key=f"e_lon_{h['cedula']}",
                        )
                    if switch_acceso:
                        if not tiene_acceso:
                            e_password = st.text_input(
                                "Contraseña *",
                                type="password",
                                key=f"e_pass_{h['cedula']}",
                                help="El vecino deberá cambiarla en su primer inicio de sesión.",
                            )
                        else:
                            e_password = st.text_input(
                                "Nueva contraseña (déjala en blanco para no cambiarla)",
                                type="password",
                                key=f"e_pass_{h['cedula']}",
                            )
                        st.caption("Requisitos: mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("Guardar"):
                            datos = {
                                "nombre": e_nombre,
                                "apellido": e_apellido,
                                "genero": e_sexo,
                                "email": e_email,
                                "fecha_nac": h.get("Fecha_nacimiento", str(date.today())),
                                "cedula": h["cedula"],
                                "telefono1": e_tel,
                                "direccion_1": e_dir,
                                "rol_id": opciones_rol.get(e_rol),
                                "estado_civil": e_estado_civil,
                                "profesion": e_profesion,
                                "latitud": e_latitud,
                                "longitud": e_longitud,
                            }

                            errores = []
                            if switch_acceso:
                                if not tiene_acceso and not e_password:
                                    errores.append("Establece una contraseña para habilitar el acceso.")
                                if e_password:
                                    pendientes = validar_password(e_password)
                                    if pendientes:
                                        errores.append(
                                            "La contraseña no cumple los requisitos: "
                                            + ", ".join(pendientes).lower()
                                        )
                                    elif tiene_acceso and uclass.password_coincide(usuario_acceso["id"], e_password):
                                        errores.append("La nueva contraseña debe ser distinta a la anterior.")

                            if errores:
                                for error in errores:
                                    st.error(error)
                            else:
                                hclass.update_habitante(h["id"], datos)

                                if switch_acceso:
                                    if usuario_acceso is None:
                                        uclass.crear_usuario(h["id"], e_password, rol_id=opciones_rol.get(e_rol))
                                    else:
                                        if e_password:
                                            uclass.cambiar_password(usuario_acceso["id"], e_password, forzar_cambio=True)
                                        uclass.actualizar_estado(usuario_acceso["id"], activo=True)
                                elif usuario_acceso is not None:
                                    uclass.actualizar_estado(usuario_acceso["id"], activo=False)

                                st.session_state.editando = None
                                st.session_state.registro_exito = "Registro actualizado"
                                st.rerun()
                    with c2:
                        if st.form_submit_button("Cancelar"):
                            st.session_state.editando = None
                            st.rerun()
