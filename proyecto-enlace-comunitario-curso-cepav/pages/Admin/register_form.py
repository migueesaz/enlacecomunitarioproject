import streamlit as st
from datetime import date
from controllers.habitantes_controller import HabitantesController


class FormularioRegistro:
    def __init__(self):
        self.nombre = ""
        self.apellido = ""
        self.cedula = ""
        self.sexo = "M"
        self.telefono_1 = ""
        self.direccion_1 = ""
        self.email = ""
        self.fecha_nac = date.today()
        self.estado_civil = "Soltero/a"
        self.profesion = ""

        self.controller = HabitantesController()

    def mostrar_formulario(self):

        @st.dialog("Registrar Habitante")
        def dialog():
            self.nombre = st.text_input("Nombre")
            self.apellido = st.text_input("Apellido")
            self.cedula = st.text_input("Cédula")
            self.sexo = st.selectbox("Sexo", ["M", "F"])
            self.telefono_1 = st.text_input("Teléfono")
            self.direccion_1 = st.text_input("Dirección")
            self.email = st.text_input("Email")
            self.fecha_nac = st.date_input(
                "Fecha de Nacimiento",
                value=date.today(),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )
            self.estado_civil = st.selectbox(
                "Estado civil",
                ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión libre"],
            )
            self.profesion = st.text_input("Profesión u oficio")

            if st.button("Registrar", type="primary"):
                if not self.nombre or not self.apellido or not self.cedula:
                    st.error("Los campos nombre, apellido y cédula son obligatorios.")
                else:
                    data = {
                        "nombre": self.nombre,
                        "apellido": self.apellido,
                        "cedula": self.cedula,
                        "genero": self.sexo,
                        "telefono1": self.telefono_1,
                        "direccion_1": self.direccion_1,
                        "email": self.email,
                        "fecha_nac": self.fecha_nac,
                        "estado_civil": self.estado_civil,
                        "profesion": self.profesion,
                    }
                    self.controller.create_habitante(data)
                    st.success(f"{self.nombre} {self.apellido} registrado exitosamente.")
                    st.rerun()

        dialog()
