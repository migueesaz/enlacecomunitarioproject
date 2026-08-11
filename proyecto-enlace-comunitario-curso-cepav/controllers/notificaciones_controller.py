from models.notificaciones_model import NotificacionesModel

class NotificacionesController:
    def __init__(self):
        self.model = NotificacionesModel()

    def obtener_notificaciones(self):
        return self.model.obtener_notificaciones()

    def agregar_notificacion(self, titulo, mensaje, fecha):
        return self.model.agregar_notificacion(titulo, mensaje, fecha)

    def actualizar_notificacion(self, id, titulo, mensaje):
        return self.model.actualizar_notificacion(id, titulo, mensaje)

    def registrar_vista(self, notificacion_id, usuario=None):
        return self.model.registrar_vista(notificacion_id, usuario)

    def obtener_notificaciones_leidas(self, usuario):
        return self.model.obtener_notificaciones_leidas(usuario)

    def obtener_vistas_detalle(self, notificacion_id=None):
        return self.model.obtener_vistas_detalle(notificacion_id)

    def eliminar_notificacion(self, id):
        return self.model.eliminar_notificacion(id)