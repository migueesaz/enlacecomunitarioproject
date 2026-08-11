from datetime import datetime
from models.pg_conn import PGConn

cursor = PGConn()


class CartasModel:
    def __init__(self):
        self.db = PGConn()

    def solicitar_carta(self, usuario, tipo_carta):

        query = """
            INSERT INTO solicitudes (usuario, tipo_carta, estado, fecha_solicitud)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute(
            query, (usuario, tipo_carta, "Pendiente", datetime.now().date())
        )

    def obtener_solicitudes(self, id_solicitud=None):
        if id_solicitud is not None:
            query = """
            SELECT s.*,
                   h.nombre AS habitante_nombre,
                   h.apellido AS habitante_apellido,
                   h.direccion_1 AS habitante_direccion,
                   h.telefono1 AS habitante_telefono,
                   h.estado_civil AS habitante_estado_civil,
                   h.profesion AS habitante_profesion
            FROM solicitudes s
            LEFT JOIN habitantes h ON h.cedula = s.usuario
            WHERE s.id = %s
            """
            resultado = self.db.execute(query, (id_solicitud,))
            if resultado:
                return resultado[0]
            return None

        query = """
        SELECT s.*,
               h.nombre AS habitante_nombre,
               h.apellido AS habitante_apellido,
               h.direccion_1 AS habitante_direccion,
               h.telefono1 AS habitante_telefono,
               h.estado_civil AS habitante_estado_civil,
               h.profesion AS habitante_profesion
        FROM solicitudes s
        LEFT JOIN habitantes h ON h.cedula = s.usuario
        ORDER BY s.fecha_solicitud DESC, s.id DESC
        """
        return self.db.execute(query) or []
    

    def aprobar(self, id_solicitud):
        query = """
        UPDATE solicitudes
        SET estado = 'Aprobada'
        WHERE id = %s
        """
        self.db.execute(query, (id_solicitud,))

    def rechazar(self, id_solicitud):
        query = """
        UPDATE solicitudes
        SET estado = 'Rechazada'
        WHERE id = %s
        """
        self.db.execute(query, (id_solicitud,))
    def en_revision(self, id_solicitud):
        query = """
        UPDATE solicitudes
        SET estado = 'En revisión'
        WHERE id = %s
        """
        self.db.execute(query, (id_solicitud,))

    def eliminar_solicitud(self, id_solicitud):
        query = """
        DELETE FROM solicitudes
        WHERE id = %s
        """
        self.db.execute(query, (id_solicitud,))
    def buscar_solicitud(self, texto):
        query = """
        SELECT s.*,
               h.nombre AS habitante_nombre,
               h.apellido AS habitante_apellido,
               h.direccion_1 AS habitante_direccion,
               h.telefono1 AS habitante_telefono,
               h.estado_civil AS habitante_estado_civil,
               h.profesion AS habitante_profesion
        FROM solicitudes s
        LEFT JOIN habitantes h ON h.cedula = s.usuario
        WHERE 
        s.tipo_carta ILIKE %s OR
        s.estado ILIKE %s
        ORDER BY s.fecha_solicitud DESC
        """
        filtro = f"%{texto}%"
        return self.db.execute(query, (filtro, filtro)
        )