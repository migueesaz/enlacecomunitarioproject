import streamlit as st
from datetime import date

st.title("Registro de Habitantes")

with st.form("registro_form"):
    st.subheader("Datos Personales")
    col1, col2 = st.columns(2)
    with col1:
        cedula = st.text_input("Cédula de identidad *")
        nombre = st.text_input("Nombre *")
        apellido = st.text_input("Apellido *")
    with col2:
        fecha_nac = st.date_input(
            "Fecha de nacimiento *",
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )
        sexo = st.selectbox("Sexo *", ["M", "F"])
        telefono = st.text_input("Teléfono")

    direccion = st.text_input("Dirección")
    submit = st.form_submit_button("Registrar", type="primary")

    if submit:
        if not cedula or not nombre or not apellido:
            st.error("Los campos cédula, nombre y apellido son obligatorios.")
        else:
            existente = any(h["cedula"] == cedula for h in st.session_state.habitantes)
            if existente:
                st.error("Ya existe un habitante con esa cédula.")
            else:
                hoy = date.today()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                categoria = "Adulto" if edad >= 18 else "NNA"

                nuevo = {
                    "cedula": cedula,
                    "nombre": nombre,
                    "apellido": apellido,
                    "fecha_nac": fecha_nac.isoformat(),
                    "sexo": sexo,
                    "telefono": telefono,
                    "direccion": direccion,
                    "categoria": categoria,
                }
                st.session_state.habitantes.append(nuevo)
                st.success(f"Habitante registrado como **{categoria}** (edad: {edad} años)")
                st.rerun()
