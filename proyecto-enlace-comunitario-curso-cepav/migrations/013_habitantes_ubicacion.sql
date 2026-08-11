-- Migración 013: Ubicación (latitud y longitud) en habitantes
-- El vecino la registra desde su perfil y el admin la visualiza en el mapa.

ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS latitud DOUBLE PRECISION;
ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS longitud DOUBLE PRECISION;
