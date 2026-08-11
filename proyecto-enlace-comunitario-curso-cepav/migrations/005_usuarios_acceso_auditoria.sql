-- Migración 005: Usuarios de acceso + auditoría
--
-- Objetivos:
--   1. `usuarios` pasa a ser una tabla SOLO de acceso. La información personal
--      (nombre, correo, teléfono, dirección) vive en `habitantes`, por lo que
--      se elimina de `usuarios` y se vincula con `habitante_id`.
--   2. Nuevos campos de control de acceso: activo, bloqueado, ultimo_ingreso.
--   3. Campos de auditoría (created_at, updated_at) en las tablas principales.

-- ============================================================================
-- 1. Vínculo: usuarios.habitante_id -> habitantes.id_habitante
--    Un habitante puede tener o no un usuario de acceso (relación opcional 1:1).
-- ============================================================================
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS habitante_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'usuarios_habitante_fk'
    ) THEN
        ALTER TABLE usuarios
            ADD CONSTRAINT usuarios_habitante_fk
            FOREIGN KEY (habitante_id) REFERENCES habitantes (id_habitante);
    END IF;
END $$;

-- Vincular usuarios existentes cuyo correo coincide con el de un habitante
UPDATE usuarios u
SET habitante_id = h.id_habitante
FROM habitantes h
WHERE u.habitante_id IS NULL
  AND u.correo = h.email;

-- Usuarios de demostración sin habitante asociado: se crea su registro censal
-- para no perder el acceso (la credencial de login es habitantes.email).
INSERT INTO habitantes (nombre, apellido, cedula, genero, email)
SELECT u.nombre, '', 'USU-' || u.id::text, 'M', u.correo
FROM usuarios u
WHERE u.habitante_id IS NULL
  AND u.correo IS NOT NULL
ON CONFLICT (email) DO NOTHING;

UPDATE usuarios u
SET habitante_id = h.id_habitante
FROM habitantes h
WHERE u.habitante_id IS NULL
  AND u.correo = h.email;

-- Un usuario por habitante (1:1 opcional)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'usuarios_habitante_unique'
    ) THEN
        ALTER TABLE usuarios
            ADD CONSTRAINT usuarios_habitante_unique UNIQUE (habitante_id);
    END IF;
END $$;

-- ============================================================================
-- 2. Eliminar información redundante (ya está en habitantes)
-- ============================================================================
ALTER TABLE usuarios DROP COLUMN IF EXISTS nombre;
ALTER TABLE usuarios DROP COLUMN IF EXISTS correo;
ALTER TABLE usuarios DROP COLUMN IF EXISTS telefono;
ALTER TABLE usuarios DROP COLUMN IF EXISTS direccion;

-- ============================================================================
-- 3. Control de acceso
-- ============================================================================
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS bloqueado BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ultimo_ingreso TIMESTAMPTZ;

-- ============================================================================
-- 4. Auditoría: created_at / updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- habitantes
ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
DROP TRIGGER IF EXISTS trg_habitantes_updated_at ON habitantes;
CREATE TRIGGER trg_habitantes_updated_at BEFORE UPDATE ON habitantes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- usuarios
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
DROP TRIGGER IF EXISTS trg_usuarios_updated_at ON usuarios;
CREATE TRIGGER trg_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- solicitudes
ALTER TABLE solicitudes ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE solicitudes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
DROP TRIGGER IF EXISTS trg_solicitudes_updated_at ON solicitudes;
CREATE TRIGGER trg_solicitudes_updated_at BEFORE UPDATE ON solicitudes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- notificaciones
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
DROP TRIGGER IF EXISTS trg_notificaciones_updated_at ON notificaciones;
CREATE TRIGGER trg_notificaciones_updated_at BEFORE UPDATE ON notificaciones
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- roles (catálogo)
ALTER TABLE roles ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE roles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
DROP TRIGGER IF EXISTS trg_roles_updated_at ON roles;
CREATE TRIGGER trg_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- tipos_solicitud (catálogo)
ALTER TABLE tipos_solicitud ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE tipos_solicitud ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
DROP TRIGGER IF EXISTS trg_tipos_solicitud_updated_at ON tipos_solicitud;
CREATE TRIGGER trg_tipos_solicitud_updated_at BEFORE UPDATE ON tipos_solicitud
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
