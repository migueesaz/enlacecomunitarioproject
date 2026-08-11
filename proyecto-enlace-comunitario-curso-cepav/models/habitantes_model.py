from datetime import date

from models.pg_conn import PGConn


class HabitantesModel():
    def __init__(self):
        self.conexion = PGConn()

    def _categoria(self, fecha_nac):
        if fecha_nac is None:
            return "N/A"
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - (
            (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day)
        )
        return "Adulto" if edad >= 18 else "NNA"

    def _a_dict(self, habitante):
        return {
            "id": habitante["id_habitante"],
            "nombre": habitante["nombre"],
            "apellido": habitante["apellido"],
            "nombre_completo": f"{habitante['nombre']} {habitante['apellido']}",
            "cedula": habitante["cedula"],
            "genero": habitante["genero"],
            "email": habitante["email"],
            "Fecha_nacimiento": habitante["fecha_nac"],
            "telefono_1": habitante["telefono1"],
            "telefono_2": habitante["telefono2"],
            "direccion_1": habitante["direccion_1"],
            "direccion_2": habitante["direccion_2"],
            "estado_civil": habitante["estado_civil"],
            "profesion": habitante["profesion"],
            "latitud": habitante["latitud"],
            "longitud": habitante["longitud"],
            "rol_id": habitante["rol_id"],
            "rol_nombre": habitante["rol_nombre"],
            "categoria": self._categoria(habitante["fecha_nac"]),
            "created_at": habitante["created_at"],
        }

    _SELECT_BASE = """
        SELECT h.*, r.nombre AS rol_nombre
        FROM habitantes h
        LEFT JOIN roles r ON r.id = h.rol_id
    """

    def obtener_roles(self):
        query = "SELECT id, nombre FROM roles ORDER BY nombre"
        return self.conexion.execute(query) or []

    def obtener_habitantes(self):
        try:
            query = self._SELECT_BASE + (
                " WHERE h.registrado_por_admin = TRUE"
                " ORDER BY h.nombre, h.apellido"
            )
            lista_habitantes = self.conexion.execute(query)
            if lista_habitantes is None:
                return []
            return [self._a_dict(h) for h in lista_habitantes]
        except Exception as e:
            print(f"Error al obtener habitantes: {e}")
            return []

    def obtener_habitante_por_id(self, habitante_id):
        query = self._SELECT_BASE + " WHERE h.id_habitante = %s"
        params = (habitante_id,)
        habitante = self.conexion.execute(query, params)

        if habitante:
            return self._a_dict(habitante[0])
        else:
            return None

    def agregar_habitante(self, nombre, apellido, cedula, genero, email, fecha_nac, telefono1, direccion_1, telefono2=None, direccion_2=None, rol_id=None, estado_civil=None, profesion=None, latitud=None, longitud=None):
        query = """
            INSERT INTO habitantes (nombre, apellido, cedula, genero, email, fecha_nac, telefono1, direccion_1, rol_id, registrado_por_admin, estado_civil, profesion, latitud, longitud)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s, %s, %s)
        """
        params = (nombre, apellido, cedula, genero, email, fecha_nac, telefono1, direccion_1, rol_id, estado_civil, profesion, latitud, longitud)
        self.conexion.execute(query, params)

    def actualizar_habitante(self, habitante_id, nombre, apellido, cedula, genero, email, fecha_nac, telefono1, direccion_1, rol_id=None, estado_civil=None, profesion=None, latitud=None, longitud=None):
        query = """
            UPDATE habitantes
            SET nombre = %s,
                apellido = %s,
                cedula = %s,
                genero = %s,
                email = %s,
                fecha_nac = %s,
                telefono1 = %s,
                direccion_1 = %s,
                rol_id = %s,
                estado_civil = %s,
                profesion = %s,
                latitud = %s,
                longitud = %s
            WHERE id_habitante = %s
        """
        params = (nombre, apellido, cedula, genero, email, fecha_nac, telefono1, direccion_1, rol_id, estado_civil, profesion, latitud, longitud, habitante_id)
        self.conexion.execute(query, params)

    def eliminar_habitante(self, habitante_id):
        query = "DELETE FROM habitantes WHERE id_habitante = %s"
        params = (habitante_id,)
        self.conexion.execute(query, params)

    def buscar_habitantes(self, texto):
        query = self._SELECT_BASE + """
            WHERE 
                h.registrado_por_admin = TRUE
                AND (h.nombre ILIKE %s 
                OR h.apellido ILIKE %s 
                OR h.cedula ILIKE %s)
            ORDER BY h.nombre"""
        filtro = f"%{texto}%"
        params = (
            filtro,
            filtro,
            filtro
        )
        habitantes = self.conexion.execute(query, params)
        if habitantes is None:
            return []
        return [self._a_dict(h) for h in habitantes]
