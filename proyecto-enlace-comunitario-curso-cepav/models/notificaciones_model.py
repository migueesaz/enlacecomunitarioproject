from models.pg_conn import PGConn


class NotificacionesModel:
    def __init__(self):
        self.conexion = PGConn()

    def obtener_notificaciones(self):
        query = """
            SELECT id, titulo, mensaje, fecha, vistas
            FROM notificaciones
            ORDER BY fecha DESC, id DESC
        """
        return self.conexion.execute(query) or []

    def agregar_notificacion(self, titulo, mensaje, fecha):
        query = """
            INSERT INTO notificaciones (titulo, mensaje, fecha)
            VALUES (%s, %s, %s)
        """
        self.conexion.execute(query, (titulo, mensaje, fecha))
        return {"id": None, "titulo": titulo, "mensaje": mensaje, "fecha": fecha}

    def actualizar_notificacion(self, id, titulo, mensaje):
        query = """
            UPDATE notificaciones
            SET titulo = %s, mensaje = %s, vistas = 0
            WHERE id = %s
        """
        self.conexion.execute(query, (titulo, mensaje, id))
        query = "DELETE FROM notificaciones_vistas WHERE notificacion_id = %s"
        self.conexion.execute(query, (id,))

    def registrar_vista(self, notificacion_id, usuario=None):
        query = """
            INSERT INTO notificaciones_vistas (notificacion_id, usuario)
            SELECT %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM notificaciones_vistas
                WHERE notificacion_id = %s AND usuario IS NOT DISTINCT FROM %s
            )
            RETURNING id
        """
        resultado = self.conexion.execute(
            query, (notificacion_id, usuario, notificacion_id, usuario)
        )
        if resultado:
            query = "UPDATE notificaciones SET vistas = vistas + 1 WHERE id = %s"
            self.conexion.execute(query, (notificacion_id,))

    def obtener_notificaciones_leidas(self, usuario):
        query = """
            SELECT notificacion_id
            FROM notificaciones_vistas
            WHERE usuario = %s
        """
        resultado = self.conexion.execute(query, (usuario,)) or []
        return {row["notificacion_id"] for row in resultado}

    def obtener_vistas_detalle(self, notificacion_id=None):
        base = """
            SELECT v.id, v.notificacion_id, v.usuario, v.fecha_vista,
                   h.nombre, h.apellido, h.cedula
            FROM notificaciones_vistas v
            LEFT JOIN habitantes h ON h.id_habitante = v.usuario
        """
        if notificacion_id is not None:
            query = base + """
                WHERE v.notificacion_id = %s
                ORDER BY v.fecha_vista DESC
            """
            return self.conexion.execute(query, (notificacion_id,)) or []
        query = base + " ORDER BY v.fecha_vista DESC"
        return self.conexion.execute(query) or []

    def eliminar_notificacion(self, id):
        query = "DELETE FROM notificaciones WHERE id = %s"
        self.conexion.execute(query, (id,))
