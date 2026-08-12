import sys
import traceback
from pathlib import Path

import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / "env", override=False)


class PGConn:
    def __init__(self):
        try:
            self.conn = psycopg.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )
        except psycopg.Error as e:
            print(f"[PGConn] Error de conexión a la BD: {e}", file=sys.stderr, flush=True)
            raise

    def execute(self, query, params=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                resultado = None
                if cursor.description:
                    dictionary = []
                    for row in cursor.fetchall():
                        row_dict = {}
                        for i, column in enumerate(cursor.description):
                            row_dict[column.name] = row[i]
                        dictionary.append(row_dict)
                    resultado = dictionary
                self.conn.commit()
                return resultado
        except Exception:
            print("[PGConn] Error al ejecutar consulta:", file=sys.stderr, flush=True)
            traceback.print_exc()
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise
