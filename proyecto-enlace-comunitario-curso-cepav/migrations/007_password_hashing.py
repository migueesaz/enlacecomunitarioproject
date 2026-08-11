# Migración 007: Hash de contraseñas con bcrypt
#
# Convierte las contraseñas almacenadas en texto plano (columna `password`
# de `usuarios`) a hashes bcrypt, en el mismo lugar. Si un valor ya parece
# un hash bcrypt se deja intacto (idempotente).

import bcrypt

MAX_BYTES = 72
PREFIJOS_BCRYPT = ("$2a$", "$2b$", "$2y$")


def up(cur):
    cur.execute("SELECT id, password FROM usuarios")
    filas = cur.fetchall()

    for usuario_id, password in filas:
        if not password:
            continue
        if password.startswith(PREFIJOS_BCRYPT):
            continue
        hashed = bcrypt.hashpw(
            password.encode("utf-8")[:MAX_BYTES], bcrypt.gensalt()
        ).decode("utf-8")
        cur.execute(
            "UPDATE usuarios SET password = %s WHERE id = %s",
            (hashed, usuario_id),
        )
