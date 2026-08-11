import streamlit as st
from models.user_model import UserModel
from controllers.notificaciones_controller import NotificacionesController


def _pagina_actual_url():
    """Devuelve el url_path de la página actual (None si no se puede determinar)."""
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import (
            get_script_run_ctx,
        )

        ctx = get_script_run_ctx()
        if ctx is None:
            return None
        return ctx.pages_manager.intended_page_name or None
    except Exception:
        return None


def _marcar_mensajes_leidos():
    """Marca todas las notificaciones como vistas por el usuario actual."""
    usuario = st.session_state.get("usuario") or {}
    habitante_id = usuario.get("habitante_id") if isinstance(usuario, dict) else None
    controller = NotificacionesController()
    notificaciones = controller.obtener_notificaciones()
    leidas = controller.obtener_notificaciones_leidas(habitante_id)
    for n in notificaciones:
        if n["id"] not in leidas:
            leidas.add(n["id"])
            controller.registrar_vista(n["id"], habitante_id)

class Login():

    def __init__(self):
        self.user_model = UserModel()

    def iniciar_sesion(self, correo: str, password: str):
        usuario = self.user_model.verificar_usuario(correo, password)
        if not usuario:
            st.error("Correo o contraseña incorrectos")
            return
        if usuario.get("bloqueado"):
            st.error("Tu cuenta está bloqueada. Contacta al administrador.")
            return
        if not usuario.get("activo"):
            st.error("Tu cuenta está inactiva. Contacta al administrador.")
            return
        st.session_state.logged_in = True
        st.session_state.usuario = usuario
        st.session_state.rol = usuario["rol"]
        if usuario.get("ultimo_ingreso") is None:
            st.session_state.cambiar_password = True
            st.warning("Debes cambiar tu contraseña antes de continuar.")
        else:
            self.user_model.registrar_ultimo_ingreso(usuario["id"])
        st.success("Inicio de sesión exitoso")
        st.rerun()

    def cerrar_sesion(self):
        st.session_state.logged_in = False
        st.session_state.usuario = None
        st.session_state.rol = None
        st.session_state.cambiar_password = False
        st.rerun()

    def paginas_disponibles(self):
        rol = st.session_state.get("rol")

        logout = st.Page(
            "pages/logout.py", title="Salir", icon=":material/logout:"
        )

        if rol == "admin":
            dashboard = st.Page(
                "pages/Admin/Dashboard.py", title="Dashboard", icon=":material/dashboard:"
            )
            poblacion = st.Page(
                "pages/Admin/Poblacion.py", title="Población", icon=":material/groups:"
            )
            cartas = st.Page(
                "pages/Admin/Cartas.py", title="Cartas", icon=":material/article:"
            )
            reportes = st.Page(
                "pages/Admin/Reportes/Censo.py", title="Reportes", icon=":material/bar_chart:"
            )
            notificaciones = st.Page(
                "pages/Admin/Notificaciones.py", title="Notificaciones", icon=":material/notifications:"
            )
            reset = st.Page(
                "pages/Admin/ResetPassword.py", title="Reset Password", icon=":material/lock_reset:"
            )
            return [dashboard, poblacion, cartas, reportes, notificaciones, reset, logout]
        elif rol == "vecino":
            home = st.Page(
                "pages/Vecinos/Home.py", title="Inicio", icon=":material/home:"
            )   
            perfil = st.Page(
            "pages/Vecinos/Perfil.py", title="Mi Perfil", icon=":material/person:"
            )
            solicitudes = st.Page(
            "pages/Vecinos/Solicitudes.py", title="Solicitudes", icon=":material/request_page:"
            )
            if _pagina_actual_url() == "Mensajes":
                try:
                    _marcar_mensajes_leidos()
                except Exception:
                    pass
            sin_leer = 0
            try:
                usuario = st.session_state.get("usuario") or {}
                habitante_id = (
                    usuario.get("habitante_id") if isinstance(usuario, dict) else None
                )
                controller = NotificacionesController()
                notificaciones = controller.obtener_notificaciones()
                leidas = controller.obtener_notificaciones_leidas(habitante_id)
                sin_leer = sum(1 for n in notificaciones if n["id"] not in leidas)
            except Exception:
                sin_leer = 0
            titulo_mensajes = "Mensajes" + (f" ({sin_leer})" if sin_leer else "")
            mensajes = st.Page(
            "pages/Vecinos/Mensajes.py", title=titulo_mensajes, icon=":material/mail:"
            )
            return [home, perfil, solicitudes, mensajes, logout]
        return []