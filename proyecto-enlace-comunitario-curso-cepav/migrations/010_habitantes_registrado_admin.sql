-- Migración 010: Marcador de habitantes registrados desde la app
--
-- Agrega la columna `registrado_por_admin` a `habitantes`. Solo los habitantes
-- creados a través de la aplicación (página de Población) se marcan con TRUE;
-- los registros insertados directamente en la BD o sembrados por las
-- migraciones (usuarios de demostración) quedan en FALSE y no aparecen en las
-- búsquedas ni filtros de la app.

ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS registrado_por_admin BOOLEAN NOT NULL DEFAULT FALSE;

-- Conservar los habitantes existentes (excepto los de demostración sembrados
-- por la migración 005, cuya cédula usa el patrón 'USU-<id>').
UPDATE habitantes
SET registrado_por_admin = TRUE
WHERE cedula NOT LIKE 'USU-%';

CREATE INDEX IF NOT EXISTS idx_habitantes_registrado_por_admin
    ON habitantes (registrado_por_admin);
