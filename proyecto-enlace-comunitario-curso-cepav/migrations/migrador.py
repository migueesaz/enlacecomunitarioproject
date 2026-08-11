import importlib.util
import os
import re
from pathlib import Path

import psycopg
from dotenv import load_dotenv

MIGRACIONES_DIR = Path(__file__).resolve().parent

load_dotenv()
load_dotenv(dotenv_path=MIGRACIONES_DIR.parent / "env", override=False)


def _cargar_modulo(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def obtener_conexion():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=10,
    )


def _migraciones_pendientes(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cur.execute("SELECT version FROM schema_migrations")
    aplicadas = {row[0] for row in cur.fetchall()}
    archivos = [
        archivo
        for archivo in sorted(MIGRACIONES_DIR.glob("*.sql")) + sorted(MIGRACIONES_DIR.glob("*.py"))
        if re.match(r"^\d+_", archivo.name)
    ]
    return [archivo for archivo in archivos if archivo.name not in aplicadas]


def ejecutar_migraciones():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cur:
            pendientes = _migraciones_pendientes(cur)
            conn.commit()

        if not pendientes:
            return

        for archivo in pendientes:
            with conn.cursor() as cur:
                if archivo.suffix == ".sql":
                    cur.execute(archivo.read_text())
                elif archivo.suffix == ".py":
                    modulo = _cargar_modulo(archivo)
                    if not hasattr(modulo, "up"):
                        raise RuntimeError(
                            f"Migración {archivo.name} debe definir la función 'up(cur)'."
                        )
                    modulo.up(cur)
                else:
                    raise RuntimeError(f"Formato de migración no soportado: {archivo.name}")
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (archivo.name,),
                )
            conn.commit()
            print(f"[migraciones] Aplicada: {archivo.name}")
    finally:
        conn.close()


if __name__ == "__main__":
    ejecutar_migraciones()
    print("[migraciones] Todas las migraciones al día.")
