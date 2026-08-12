import streamlit as st
from controllers.habitantes_controller import HabitantesController
from controllers.solicitudes_controller import SolicitudesController

_HTML_UBICACION = """
<style>
  #btn-ubicacion {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer;
    font-family: inherit; font-size: 1rem; line-height: 1.5;
    border: 1px solid var(--st-primary-color, #ff4b4b);
    background: var(--st-secondary-background-color, #ffffff);
    color: var(--st-text-color, #262730);
    transition: background 0.15s ease, color 0.15s ease;
  }
  #btn-ubicacion:hover:not(:disabled) {
    background: var(--st-primary-color, #ff4b4b);
    color: var(--st-text-color, #ffffff);
  }
  #btn-ubicacion:disabled { opacity: 0.6; cursor: not-allowed; }
  .geo-estado { margin-top: 8px; font-size: 0.85rem; color: var(--st-secondary-text-color, #616161); }
  .geo-estado.error { color: var(--st-error-color, #e74c3c); }
</style>
<button id="btn-ubicacion" type="button">Usar mi ubicación</button>
<div id="estado" class="geo-estado"></div>
"""

_JS_UBICACION = """\
export default function (component) {
  const { parentElement, setStateValue, setTriggerValue } = component
  const btn = parentElement.querySelector("#btn-ubicacion")
  const estado = parentElement.querySelector("#estado")
  if (!btn || !estado) return

  btn.onclick = () => {
    if (!navigator.geolocation) {
      const msg = "Este navegador no soporta geolocalización."
      estado.textContent = msg
      estado.className = "geo-estado error"
      setStateValue("error", msg)
      return
    }
    btn.disabled = true
    estado.textContent = "Solicitando permiso de ubicación..."
    estado.className = "geo-estado"
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = { latitud: pos.coords.latitude, longitud: pos.coords.longitude }
        btn.disabled = false
        estado.textContent = "Ubicación obtenida."
        estado.className = "geo-estado"
        setStateValue("error", null)
        setTriggerValue("obtenida", coords)
      },
      (err) => {
        btn.disabled = false
        let msg
        if (err.code === err.PERMISSION_DENIED) {
          msg = "Permiso denegado. Actívalo en la configuración del navegador o escribe las coordenadas manualmente."
        } else if (err.code === err.POSITION_UNAVAILABLE) {
          msg = "No se pudo obtener la ubicación. Intenta de nuevo."
        } else {
          msg = "No se pudo obtener la ubicación (timeout). Intenta de nuevo."
        }
        estado.textContent = msg
        estado.className = "geo-estado error"
        setStateValue("error", msg)
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    )
  }
}
"""

_GEO_COMPONENT = st.components.v2.component(
    "geolocalizacion_navegador",
    html=_HTML_UBICACION,
    js=_JS_UBICACION,
)


def boton_ubicacion(*, key, on_obtenida=None):
    if on_obtenida is None:
        on_obtenida = lambda: None
    return _GEO_COMPONENT(
        key=key,
        on_obtenida_change=on_obtenida,
        on_error_change=lambda: None,
    )


usuario = st.session_state.get("usuario", {})

st.title("Mi Perfil")

opciones_estado = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"]

st.subheader("Datos Personales")

c1, c2 = st.columns(2)
with c1:
    nombre = st.text_input("Nombres", value=usuario.get("nombre", ""))
with c2:
    apellido = st.text_input("Apellidos", value=usuario.get("apellido", ""))

c1, c2 = st.columns(2)
with c1:
    cedula = st.text_input("Cédula de identidad", value=usuario.get("cedula", ""))
with c2:
    correo = st.text_input("Correo electrónico", value=usuario.get("correo", ""))

c1, c2 = st.columns(2)
with c1:
    telefono = st.text_input("Teléfono", value=usuario.get("telefono", ""))
with c2:
    indice_estado = (
        opciones_estado.index(usuario["estado_civil"])
        if usuario.get("estado_civil") in opciones_estado
        else 0
    )
    estado_civil = st.selectbox("Estado civil", opciones_estado, index=indice_estado)

c1, c2 = st.columns(2)
with c1:
    profesion = st.text_input("Profesión u oficio", value=usuario.get("profesion", ""))
with c2:
    direccion = st.text_input("Dirección", value=usuario.get("direccion", ""))

st.subheader("Ubicación de tu vivienda")
st.caption("Registra las coordenadas de tu casa para que el consejo comunal te ubique en el mapa. Tienes dos opciones: copiarlas desde Google Maps o autocompletarlas con el botón.")

with st.expander("¿Cómo copio las coordenadas en Google Maps?"):
    st.markdown("""
1. Haz clic en **"Abrir en Google Maps"** (o entra a [maps.google.com](https://maps.google.com)).
2. Escribe tu dirección y acerca el mapa hasta tu vivienda.
3. Haz **clic derecho** sobre el punto exacto de tu casa y elige **"¿Qué hay aquí?"** (o *"¿Qué hay en este lugar?"*).
4. Abajo aparece un recuadro gris con las **coordenadas**, por ejemplo:
    ```
    10.4805937, -66.9036063
    ```
5. Haz clic en ese texto para copiarlo y pégalo aquí:
    - **Latitud** → primer número (ej. `10.4805937`)
    - **Longitud** → segundo número (ej. `-66.9036063`)
""")
    st.info("**Ejemplo (Caracas):** `10.4805937, -66.9036063` → Latitud `10.4805937` y Longitud `-66.9036063`.")

GEO_KEY = "geo_perfil"


def _aplicar_ubicacion():
    datos = st.session_state.get(GEO_KEY) or {}
    coords = datos.get("obtenida")
    if coords:
        st.session_state["lat_perfil"] = coords["latitud"]
        st.session_state["lon_perfil"] = coords["longitud"]


lat_actual = st.session_state.get("lat_perfil", usuario.get("latitud"))
lon_actual = st.session_state.get("lon_perfil", usuario.get("longitud"))
url_maps = (
    f"https://www.google.com/maps?q={lat_actual},{lon_actual}"
    if lat_actual is not None and lon_actual is not None
    else "https://maps.google.com"
)

c_maps, c_geo = st.columns(2)
with c_maps:
    st.link_button(":material/location_on: Abrir en Google Maps", url_maps, width="stretch")
with c_geo:
    res_geo = boton_ubicacion(key=GEO_KEY, on_obtenida=_aplicar_ubicacion)

if res_geo.error:
    st.warning(res_geo.error)

st.caption("El botón requiere abrir la app en localhost o con HTTPS (los navegadores exigen conexión segura para la ubicación).")
c1, c2 = st.columns(2)
with c1:
    latitud = st.number_input(
        "Latitud",
        value=usuario.get("latitud"),
        format="%.6f",
        step=0.000001,
        min_value=-90.0,
        max_value=90.0,
        key="lat_perfil",
        help="Primer número de las coordenadas (ej. 10.4805937).",
    )
with c2:
    longitud = st.number_input(
        "Longitud",
        value=usuario.get("longitud"),
        format="%.6f",
        step=0.000001,
        min_value=-180.0,
        max_value=180.0,
        key="lon_perfil",
        help="Segundo número de las coordenadas (ej. -66.9036063).",
    )

if st.button("Guardar cambios"):
    habitante_id = usuario.get("habitante_id")
    actual = None
    if habitante_id:
        actual = HabitantesController().get_habitante(habitante_id)
    if not actual:
        st.error("No se encontró tu registro en la base de datos.")
    else:
        try:
            HabitantesController().update_habitante(
                habitante_id,
                {
                    "nombre": nombre,
                    "apellido": apellido,
                    "cedula": cedula,
                    "genero": actual["genero"],
                    "email": correo,
                    "fecha_nac": actual["Fecha_nacimiento"],
                    "telefono1": telefono,
                    "direccion_1": direccion,
                    "rol_id": actual["rol_id"],
                    "estado_civil": estado_civil,
                    "profesion": profesion,
                    "latitud": latitud if latitud is not None else actual.get("latitud"),
                    "longitud": longitud if longitud is not None else actual.get("longitud"),
                },
            )
        except Exception:
            st.error(
                "No se pudieron guardar los datos. Revisa que la cédula y el "
                "correo no estén registrados por otro vecino."
            )
        else:
            solicitudes_ctrl = SolicitudesController()
            if cedula != actual["cedula"]:
                solicitudes_ctrl.reasignar_cedula(actual["cedula"], cedula)
            invalidadas = solicitudes_ctrl.invalidar_aprobadas_usuario(cedula)
            st.session_state.usuario.update({
                "nombre": nombre,
                "apellido": apellido,
                "cedula": cedula,
                "correo": correo,
                "telefono": telefono,
                "direccion": direccion,
                "estado_civil": estado_civil,
                "profesion": profesion,
                "latitud": latitud if latitud is not None else usuario.get("latitud"),
                "longitud": longitud if longitud is not None else usuario.get("longitud"),
            })
            st.success("Perfil actualizado correctamente")
            if invalidadas:
                st.info(
                    "Actualizaste tus datos personales. Para obtener una carta con tu "
                    "información actualizada, por favor crea una solicitud nueva; el "
                    "administrador la verificará antes de emitirla."
                )
