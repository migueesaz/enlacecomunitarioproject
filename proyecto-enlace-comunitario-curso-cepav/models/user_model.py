import re
import secrets

import bcrypt

from models.pg_conn import PGConn

REQUISITOS_PASSWORD = (
    ("Mínimo 8 caracteres.", lambda p: len(p) >= 8),
    ("Al menos una letra mayúscula (A-Z).", lambda p: re.search(r"[A-Z]", p) is not None),
    ("Al menos una letra minúscula (a-z).", lambda p: re.search(r"[a-z]", p) is not None),
    ("Al menos un número (0-9).", lambda p: re.search(r"\d", p) is not None),
    ("Al menos un carácter especial (!@#$%^&*...).", lambda p: re.search(r"[^A-Za-z0-9\s]", p) is not None),
)

_MAX_BYTES = 72
_PREFIJOS_BCRYPT = ("$2a$", "$2b$", "$2y$")


def _preparar(password):
    return password.encode("utf-8")[:_MAX_BYTES]


def _hash_password(password):
    return bcrypt.hashpw(_preparar(password), bcrypt.gensalt()).decode("utf-8")


def _es_hash(password):
    return isinstance(password, str) and password.startswith(_PREFIJOS_BCRYPT)


def _verificar_password(candidata, almacenada):
    if almacenada is None:
        return False
    if _es_hash(almacenada):
        try:
            return bcrypt.checkpw(_preparar(candidata), almacenada.encode("utf-8"))
        except ValueError:
            return False
    return secrets.compare_digest(candidata, almacenada)


def evaluar_password(password):
    return [(descripcion, cumple(password)) for descripcion, cumple in REQUISITOS_PASSWORD]


def validar_password(password):
    return [descripcion for descripcion, cumple in evaluar_password(password) if not cumple]


class UserModel:
    def __init__(self):
        self.conexion = PGConn()

    def verificar_usuario(self, correo, password):
        query = """
            SELECT u.id,
                   u.habitante_id,
                   u.activo,
                   u.bloqueado,
                   u.ultimo_ingreso,
                   u.password,
                   h.nombre,
                   h.apellido,
                   h.cedula,
                   h.email AS correo,
                   h.telefono1 AS telefono,
                   h.direccion_1 AS direccion,
                   h.estado_civil,
                   h.profesion,
                   h.latitud,
                   h.longitud,
                   COALESCE(r.nombre, 'vecino') AS rol
            FROM usuarios u
            JOIN habitantes h ON h.id_habitante = u.habitante_id
            LEFT JOIN roles r ON r.id = u.rol_id
            WHERE LOWER(h.email) = LOWER(%s)
            LIMIT 1
        """
        usuarios = self.conexion.execute(query, (correo,))
        if not usuarios:
            return None

        usuario = usuarios[0]
        if not _verificar_password(password, usuario["password"]):
            return None

        if not _es_hash(usuario["password"]):
            self._actualizar_hash(usuario["id"], password)

        usuario.pop("password", None)
        return usuario

    def _actualizar_hash(self, usuario_id, password):
        query = "UPDATE usuarios SET password = %s WHERE id = %s"
        self.conexion.execute(query, (_hash_password(password), usuario_id))

    def registrar_ultimo_ingreso(self, usuario_id):
        query = "UPDATE usuarios SET ultimo_ingreso = NOW() WHERE id = %s"
        self.conexion.execute(query, (usuario_id,))

    def crear_usuario(self, habitante_id, password, rol_id=None):
        query = """
            INSERT INTO usuarios (habitante_id, password, rol_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (habitante_id) DO UPDATE
                SET password = EXCLUDED.password,
                    rol_id = EXCLUDED.rol_id,
                    bloqueado = FALSE,
                    activo = TRUE
        """
        self.conexion.execute(query, (habitante_id, _hash_password(password), rol_id))

    def actualizar_estado(self, usuario_id, activo=None, bloqueado=None):
        updates = []
        params = []
        if activo is not None:
            updates.append("activo = %s")
            params.append(activo)
        if bloqueado is not None:
            updates.append("bloqueado = %s")
            params.append(bloqueado)
        if not updates:
            return
        params.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
        self.conexion.execute(query, tuple(params))

    def obtener_usuario_por_habitante(self, habitante_id):
        query = """
            SELECT u.id, u.habitante_id, u.activo, u.bloqueado, u.ultimo_ingreso,
                   u.rol_id, COALESCE(r.nombre, 'vecino') AS rol
            FROM usuarios u
            LEFT JOIN roles r ON r.id = u.rol_id
            WHERE u.habitante_id = %s
        """
        res = self.conexion.execute(query, (habitante_id,))
        return res[0] if res else None

    def _consulta_usuarios_con_acceso(self):
        return """
            SELECT u.id,
                   u.habitante_id,
                   u.activo,
                   u.bloqueado,
                   u.ultimo_ingreso,
                   u.rol_id,
                   h.nombre,
                   h.apellido,
                   h.cedula,
                   h.email AS correo,
                   h.telefono1 AS telefono,
                   COALESCE(r.nombre, 'vecino') AS rol
            FROM usuarios u
            JOIN habitantes h ON h.id_habitante = u.habitante_id
            LEFT JOIN roles r ON r.id = u.rol_id
            WHERE u.activo = TRUE
        """

    def obtener_usuarios_con_acceso(self):
        query = self._consulta_usuarios_con_acceso() + " ORDER BY h.nombre, h.apellido"
        return self.conexion.execute(query)

    def buscar_usuarios(self, texto):
        query = self._consulta_usuarios_con_acceso() + """
            AND (h.nombre ILIKE %s
                 OR h.apellido ILIKE %s
                 OR h.cedula ILIKE %s
                 OR h.email ILIKE %s)
            ORDER BY h.nombre, h.apellido
        """
        like = f"%{texto}%"
        return self.conexion.execute(query, (like, like, like, like))

    def password_coincide(self, usuario_id, candidata):
        query = "SELECT password FROM usuarios WHERE id = %s"
        res = self.conexion.execute(query, (usuario_id,))
        if not res:
            return False
        almacenada = res[0]["password"]
        coincide = _verificar_password(candidata, almacenada)
        if coincide and not _es_hash(almacenada):
            self._actualizar_hash(usuario_id, candidata)
        return coincide

    def cambiar_password(self, usuario_id, nueva_password, forzar_cambio=False):
        if forzar_cambio:
            query = """
                UPDATE usuarios
                SET password = %s, ultimo_ingreso = NULL
                WHERE id = %s
            """
        else:
            query = """
                UPDATE usuarios
                SET password = %s, ultimo_ingreso = NOW()
                WHERE id = %s
            """
        self.conexion.execute(query, (_hash_password(nueva_password), usuario_id))
