-- Migración 008: Conteo de vistas y registro de quién vio cada notificación
--
-- Agrega a `notificaciones` un contador de vistas y crea la tabla
-- `notificaciones_vistas` que guarda quién (cédula del usuario) y cuándo
-- vio cada notificación. Esta tabla queda preparada para futuros análisis
-- de audiencia por notificación.

ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS vistas INT NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS notificaciones_vistas (
    id SERIAL PRIMARY KEY,
    notificacion_id INT NOT NULL REFERENCES notificaciones(id) ON DELETE CASCADE,
    usuario VARCHAR(255),
    fecha_vista TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notificaciones_vistas_notificacion
    ON notificaciones_vistas (notificacion_id);
