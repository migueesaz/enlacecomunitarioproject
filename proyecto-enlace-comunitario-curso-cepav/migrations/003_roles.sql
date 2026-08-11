-- Migración 003: Catálogo de roles

-- ============================================================================
-- 1. Tabla: roles
--    Catálogo de roles de usuario (admin, vecino, ...). Se usa como fuente
--    de opciones para el rol de los usuarios.
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

INSERT INTO roles (nombre, descripcion)
VALUES
    ('admin', 'Administrador del sistema.'),
    ('vecino', 'Vecino de la comunidad.')
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================================
-- 2. Relación: usuarios.rol_id -> roles.id
--    Columna opcional para mantener compatibilidad con usuarios existentes.
-- ============================================================================
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'usuarios_rol_fk'
    ) THEN
        ALTER TABLE usuarios
            ADD CONSTRAINT usuarios_rol_fk
            FOREIGN KEY (rol_id) REFERENCES roles (id);
    END IF;
END $$;

-- Vincular usuarios existentes con su rol según su valor de texto (idempotente)
UPDATE usuarios u
SET rol_id = r.id
FROM roles r
WHERE u.rol = r.nombre
  AND u.rol_id IS NULL;
