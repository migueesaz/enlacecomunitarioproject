-- Migración 004: Rol del sistema para habitantes
--
-- Agrega el rol del sistema (admin/vecino) a la tabla habitantes,
-- reutilizando el catálogo `roles` creado en la migración 003.

-- ============================================================================
-- 1. Columna: habitantes.rol_id
--    Rol del sistema que tiene cada habitante (admin / vecino).
-- ============================================================================
ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS rol_id INTEGER;

-- ============================================================================
-- 2. Llave foránea: habitantes.rol_id -> roles.id
--    Se verifica en pg_constraint antes de crearla (idempotente).
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'habitantes_rol_fk'
    ) THEN
        ALTER TABLE habitantes
            ADD CONSTRAINT habitantes_rol_fk
            FOREIGN KEY (rol_id) REFERENCES roles (id);
    END IF;
END $$;
