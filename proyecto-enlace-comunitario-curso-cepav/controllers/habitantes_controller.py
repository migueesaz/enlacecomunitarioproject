from models.habitantes_model import HabitantesModel
class HabitantesController:
    def __init__(self):
        self.service = HabitantesModel()

    def get_habitantes(self):
        return self.service.obtener_habitantes()

    def get_habitante(self, habitante_id):
        return self.service.obtener_habitante_por_id(habitante_id)

    def create_habitante(self, habitante_data):
        return self.service.agregar_habitante(**habitante_data)

    def update_habitante(self, habitante_id, habitante_data):
        return self.service.actualizar_habitante(
            habitante_id,
            habitante_data["nombre"],
            habitante_data["apellido"],
            habitante_data["cedula"],
            habitante_data["genero"],
            habitante_data["email"],
            habitante_data["fecha_nac"],
            habitante_data["telefono1"],
            habitante_data["direccion_1"],
            habitante_data.get("rol_id"),
            habitante_data.get("estado_civil"),
            habitante_data.get("profesion"),
            habitante_data.get("latitud"),
            habitante_data.get("longitud"),
        )

    def get_roles(self):
        return self.service.obtener_roles()

    def delete_habitante(self, habitante_id):
        return self.service.eliminar_habitante(habitante_id)

    def buscar_habitantes(self, texto):
        return self.service.buscar_habitantes(texto)