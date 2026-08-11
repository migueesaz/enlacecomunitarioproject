from models.solicitudes_model import SolicitudesModel


class SolicitudesController:
    def __init__(self):
        self.modelo = SolicitudesModel()

    def obtener_tipos(self):
        return self.modelo.obtener_tipos()

    def obtener_solicitudes_usuario(self, usuario_cedula):
        return self.modelo.obtener_solicitudes_usuario(usuario_cedula)

    def tiene_solicitud_activa(self, usuario_cedula, tipo_id):
        return self.modelo.tiene_solicitud_activa(usuario_cedula, tipo_id)

    def crear_solicitud(self, usuario_cedula, tipo_id, tipo_nombre):
        return self.modelo.crear_solicitud(usuario_cedula, tipo_id, tipo_nombre)

    def invalidar_aprobadas_usuario(self, usuario_cedula):
        return self.modelo.invalidar_aprobadas_usuario(usuario_cedula)
