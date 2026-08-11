import streamlit as st
import secrets
import string

from models.user_model import UserModel

uclass = UserModel()

st.title("Reset de Contraseña")

st.markdown(
    "Usuarios con acceso al sistema. Busque por nombre, cédula o correo para "
    "generar una nueva contraseña temporal."
)

busqueda = st.text_input(
    "Buscar usuario por nombre, cédula o correo",
    placeholder="Escriba para filtrar la lista...",
)

if busqueda:
    usuarios = uclass.buscar_usuarios(busqueda)
else:
    usuarios = uclass.obtener_usuarios_con_acceso()

if not usuarios:
    if busqueda:
        st.info("No se encontraron usuarios con esos criterios.")
    else:
        st.warning("No hay usuarios con acceso al sistema.")
else:
    st.caption(
        f"{len(usuarios)} usuario(s) con acceso"
        + (f" · filtrado por \"{busqueda}\"" if busqueda else "")
    )

    for u in usuarios:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1], vertical_alignment="center")
            with col1:
                st.markdown(f"**{u['nombre']} {u['apellido']}** — C.I. {u['cedula']}")
                st.caption(
                    f"Correo: {u.get('correo') or '—'} · Rol: {u['rol']}"
                    + (" · Bloqueado" if u.get("bloqueado") else "")
                )
            with col2:
                if st.button("Resetear contraseña", key=f"reset_{u['id']}", type="primary"):
                    alphabet = string.ascii_letters + string.digits
                    nueva_pass = ''.join(secrets.choice(alphabet) for _ in range(10))
                    uclass.cambiar_password(u["id"], nueva_pass, forzar_cambio=True)
                    st.session_state.nueva_password = {
                        "usuario_id": u["id"],
                        "password": nueva_pass,
                        "nombre": f"{u['nombre']} {u['apellido']}".strip(),
                    }
                    st.rerun()

            if (
                st.session_state.get("nueva_password")
                and st.session_state.nueva_password["usuario_id"] == u["id"]
            ):
                st.warning(
                    f"Nueva contraseña temporal para **{st.session_state.nueva_password['nombre']}**: "
                    f"`{st.session_state.nueva_password['password']}`"
                )
                st.caption(
                    "Comuníquele esta contraseña al usuario. Deberá cambiarla en su primer inicio de sesión."
                )
