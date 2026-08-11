-- Migración 009: notificaciones_vistas.usuario guarda el id_habitante
--
-- Antes esta columna almacenaba la cédula del habitante (texto). Ahora pasa a
-- guardar el id_habitante (entero), que es la clave estable de la tabla
-- `habitantes`. Se convierten los registros existentes y se agrega la llave
-- foránea correspondiente.

-- 1) Limpiar registros que no se puedan asociar a un habitante.
UPDATE notificaciones_vistas v
SET usuario = NULL
WHERE usuario IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM habitantes h WHERE h.cedula = v.usuario
  );

-- 2) Convertir los registros existentes: de cédula (texto) a id_habitante.
UPDATE notificaciones_vistas v
SET usuario = h.id_habitante
FROM habitantes h
WHERE h.cedula = v.usuario;

-- 3) Cambiar el tipo de la columna a INTEGER.
ALTER TABLE notificaciones_vistas
    ALTER COLUMN usuario DROP NOT NULL;

ALTER TABLE notificaciones_vistas
    ALTER COLUMN usuario TYPE INTEGER USING usuario::integer;

-- 4) Llave foránea hacia habitantes(id_habitante) (idempotente).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'notificaciones_vistas_usuario_fk'
    ) THEN
        ALTER TABLE notificaciones_vistas
            ADD CONSTRAINT notificaciones_vistas_usuario_fk
            FOREIGN KEY (usuario) REFERENCES habitantes (id_habitante);
    END IF;
END $$;
