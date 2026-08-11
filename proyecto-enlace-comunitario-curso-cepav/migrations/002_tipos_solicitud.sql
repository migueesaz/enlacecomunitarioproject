-- Migración 002: Catálogo de tipos de solicitud

-- ============================================================================
-- 1. Tabla: tipos_solicitud
--    Catálogo de tipos de solicitudes (cartas, constancias, etc.). Se usa
--    como fuente de opciones para los formularios de solicitud.
-- ============================================================================
CREATE TABLE IF NOT EXISTS tipos_solicitud (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO tipos_solicitud (nombre, descripcion)
VALUES
    ('Carta de Residencia', 'Solicitud de carta que acredita residencia en la comunidad.'),
    ('Carta de Buena Conducta', 'Solicitud de carta de buena conducta.'),
    ('Carta Aval', 'Solicitud de carta de aval o recomendación.')
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================================
-- 2. Relación: solicitudes.tipo_solicitud_id -> tipos_solicitud.id
--    Columna opcional para mantener compatibilidad con solicitudes existentes.
-- ============================================================================
ALTER TABLE solicitudes ADD COLUMN IF NOT EXISTS tipo_solicitud_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'solicitudes_tipo_solicitud_fk'
    ) THEN
        ALTER TABLE solicitudes
            ADD CONSTRAINT solicitudes_tipo_solicitud_fk
            FOREIGN KEY (tipo_solicitud_id) REFERENCES tipos_solicitud (id);
    END IF;
END $$;
