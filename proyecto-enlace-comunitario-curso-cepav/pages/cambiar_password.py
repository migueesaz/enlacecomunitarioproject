import streamlit as st
from models.user_model import UserModel, evaluar_password, validar_password

st.title("Cambiar Contraseña")
st.caption("Por seguridad, debes cambiar tu contraseña antes de continuar.")

usuario = st.session_state.get("usuario") or {}

nueva = st.text_input("Nueva contraseña", type="password", key="nueva_pass")
confirmar = st.text_input("Confirmar contraseña", type="password", key="confirmar_pass")

if nueva:
    for descripcion, cumple in evaluar_password(nueva):
        simbolo = "✓" if cumple else "✗"
        st.markdown(f"{simbolo} {descripcion}")

if st.button("Cambiar contraseña", type="primary"):
    errores = []
    if not nueva or not confirmar:
        errores.append("Ingresa la contraseña en ambos campos.")
    elif nueva != confirmar:
        errores.append("Las contraseñas no coinciden.")
    else:
        pendientes = validar_password(nueva)
        if pendientes:
            errores.append("La contraseña no cumple los requisitos: " + ", ".join(pendientes).lower())
        else:
            model = UserModel()
            if model.password_coincide(usuario["id"], nueva):
                errores.append("No puedes usar la contraseña anterior.")
            else:
                model.cambiar_password(usuario["id"], nueva, forzar_cambio=False)
                st.session_state.cambiar_password = False
                st.success("Contraseña actualizada correctamente. Ya puedes continuar.")
                st.rerun()

    for error in errores:
        st.error(error)
