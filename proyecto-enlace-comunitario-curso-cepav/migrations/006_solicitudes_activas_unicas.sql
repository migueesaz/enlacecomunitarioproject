-- Migración 006: Restricción de solicitudes activas por usuario y tipo
--
-- Evita que un vecino tenga dos solicitudes ACTIVAS del mismo tipo.
-- Se usa un índice único parcial: solo aplica sobre solicitudes cuyo estado
-- no sea final (Aprobada / Rechazada). Una vez finalizada una solicitud, el
-- vecino puede volver a solicitar ese mismo tipo.

CREATE UNIQUE INDEX IF NOT EXISTS idx_solicitudes_activas_unicas
ON solicitudes (usuario, tipo_solicitud_id)
WHERE estado NOT IN ('Aprobada', 'Rechazada');
