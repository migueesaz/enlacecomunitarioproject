from models.cartas_model import CartasModel


class CartasController:
    def __init__(self):
        self.modelo = CartasModel()
    def solicitar_carta(self, usuario, tipo_carta):
        return self.modelo.solicitar_carta(usuario, tipo_carta)
    def listar(self):
        return self.modelo.obtener_solicitudes()
    def aprobar(self, id_solicitud):
        return self.modelo.aprobar(id_solicitud)
    def rechazar(self, id_solicitud):
        return self.modelo.rechazar(id_solicitud)
    def en_revision(self, id_solicitud):
        return self.modelo.en_revision(id_solicitud)
    def buscar_solicitud(self, texto):
        return self.modelo.buscar_solicitud(texto)
    def eliminar_solicitud(self, id_solicitud):
        return self.modelo.eliminar_solicitud(id_solicitud)
    