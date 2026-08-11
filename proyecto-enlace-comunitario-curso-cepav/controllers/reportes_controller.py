from datetime import date

from models.pg_conn import PGConn

ESTADOS_SOLICITUD = ("Pendiente", "En revisión", "Aprobada", "Rechazada", "Requiere actualización")


def _edad(fecha_nac):
    if fecha_nac is None:
        return None
    hoy = date.today()
    return hoy.year - fecha_nac.year - (
        (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day)
    )


def _categoria(fecha_nac):
    edad = _edad(fecha_nac)
    if edad is None:
        return "N/A"
    return "Adulto" if edad >= 18 else "NNA"


class ReportesController:
    def __init__(self):
        self.db = PGConn()

    def tipos_solicitud(self):
        return self.db.execute(
            "SELECT id, nombre FROM tipos_solicitud WHERE activo = TRUE ORDER BY nombre"
        ) or []

    def censo(self, fecha_desde, fecha_hasta):
        query = """
            SELECT h.*, r.nombre AS rol_nombre
            FROM habitantes h
            LEFT JOIN roles r ON r.id = h.rol_id
            WHERE h.registrado_por_admin = TRUE
              AND h.created_at::date BETWEEN %s AND %s
            ORDER BY h.nombre, h.apellido
        """
        resultado = self.db.execute(query, (fecha_desde, fecha_hasta)) or []
        for h in resultado:
            h["edad"] = _edad(h["fecha_nac"])
            h["categoria"] = _categoria(h["fecha_nac"])
        return resultado

    def solicitudes(self, fecha_desde, fecha_hasta, estado=None, tipo_id=None):
        query = """
            SELECT s.id, s.usuario AS cedula, s.tipo_carta, s.estado,
                   s.fecha_solicitud, s.created_at,
                   t.nombre AS tipo_nombre,
                   h.nombre, h.apellido, h.genero, h.fecha_nac
            FROM solicitudes s
            LEFT JOIN tipos_solicitud t ON t.id = s.tipo_solicitud_id
            LEFT JOIN habitantes h ON h.cedula = s.usuario
            WHERE s.fecha_solicitud BETWEEN %s AND %s
        """
        params = [fecha_desde, fecha_hasta]
        if estado:
            query += " AND s.estado = %s"
            params.append(estado)
        if tipo_id:
            query += " AND s.tipo_solicitud_id = %s"
            params.append(tipo_id)
        query += " ORDER BY s.fecha_solicitud DESC, s.id DESC"
        return self.db.execute(query, tuple(params)) or []

    def usuarios(self, fecha_desde, fecha_hasta):
        query = """
            SELECT u.id, u.habitante_id, u.activo, u.bloqueado, u.ultimo_ingreso,
                   u.created_at AS fecha_creacion, u.rol_id,
                   h.nombre, h.apellido, h.cedula, h.email AS correo,
                   COALESCE(r.nombre, 'vecino') AS rol
            FROM usuarios u
            JOIN habitantes h ON h.id_habitante = u.habitante_id
            LEFT JOIN roles r ON r.id = u.rol_id
            WHERE u.created_at::date BETWEEN %s AND %s
            ORDER BY u.created_at DESC, h.nombre, h.apellido
        """
        return self.db.execute(query, (fecha_desde, fecha_hasta)) or []

    def notificaciones(self, fecha_desde, fecha_hasta):
        query = """
            SELECT n.id, n.titulo, n.mensaje, n.fecha, n.vistas, n.created_at
            FROM notificaciones n
            WHERE n.fecha BETWEEN %s AND %s
            ORDER BY n.fecha DESC, n.id DESC
        """
        return self.db.execute(query, (fecha_desde, fecha_hasta)) or []

    def vistas_detalle(self, notificacion_id):
        query = """
            SELECT v.usuario, v.fecha_vista,
                   n.titulo AS notificacion, n.fecha AS notificacion_fecha,
                   h.nombre, h.apellido, h.cedula
            FROM notificaciones_vistas v
            JOIN notificaciones n ON n.id = v.notificacion_id
            LEFT JOIN habitantes h ON h.id_habitante = v.usuario
            WHERE v.notificacion_id = %s
            ORDER BY v.fecha_vista DESC
        """
        return self.db.execute(query, (notificacion_id,)) or []
