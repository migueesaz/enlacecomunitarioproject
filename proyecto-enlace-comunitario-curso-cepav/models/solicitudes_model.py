from datetime import date

from models.pg_conn import PGConn

ESTADOS_FINALES = ("Aprobada", "Rechazada", "Requiere actualización")


class SolicitudesModel:
    def __init__(self):
        self.db = PGConn()

    def obtener_tipos(self):
        query = """
            SELECT id, nombre, descripcion
            FROM tipos_solicitud
            WHERE activo = TRUE
            ORDER BY nombre
        """
        return self.db.execute(query) or []

    def obtener_solicitudes_usuario(self, usuario_cedula):
        query = """
            SELECT s.id, s.estado, s.fecha_solicitud, s.tipo_carta,
                   s.tipo_solicitud_id, t.nombre AS tipo_nombre
            FROM solicitudes s
            LEFT JOIN tipos_solicitud t ON t.id = s.tipo_solicitud_id
            WHERE s.usuario = %s
            ORDER BY s.fecha_solicitud DESC, s.id DESC
        """
        return self.db.execute(query, (usuario_cedula,)) or []

    def tiene_solicitud_activa(self, usuario_cedula, tipo_id):
        query = """
            SELECT id
            FROM solicitudes
            WHERE usuario = %s AND tipo_solicitud_id = %s
              AND estado NOT IN ('Aprobada', 'Rechazada', 'Requiere actualización')
            LIMIT 1
        """
        return bool(self.db.execute(query, (usuario_cedula, tipo_id)))

    def crear_solicitud(self, usuario_cedula, tipo_id, tipo_nombre):
        query = """
            INSERT INTO solicitudes
                (usuario, tipo_carta, tipo_solicitud_id, estado, fecha_solicitud)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(
            query,
            (usuario_cedula, tipo_nombre, tipo_id, "Pendiente", date.today()),
        )

    def invalidar_aprobadas_usuario(self, usuario_cedula):
        query = """
            UPDATE solicitudes
            SET estado = 'Requiere actualización'
            WHERE usuario = %s AND estado = 'Aprobada'
            RETURNING id
        """
        resultado = self.db.execute(query, (usuario_cedula,))
        return len(resultado) if resultado else 0
