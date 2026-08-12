-- Migración 014: Corregir índice único de solicitudes activas
--
-- El índice 006 consideraba "activas" las solicitudes en estado
-- 'Requiere actualización', pero la app lo trata como estado final.
-- Al invalidar una carta aprobada (perfil actualizado) el vecino quedaba
-- bloqueado para solicitar de nuevo ese mismo tipo.
-- Se recrea el índice excluyendo los tres estados finales.

DROP INDEX IF EXISTS idx_solicitudes_activas_unicas;

CREATE UNIQUE INDEX idx_solicitudes_activas_unicas
ON solicitudes (usuario, tipo_solicitud_id)
WHERE estado NOT IN ('Aprobada', 'Rechazada', 'Requiere actualización');
