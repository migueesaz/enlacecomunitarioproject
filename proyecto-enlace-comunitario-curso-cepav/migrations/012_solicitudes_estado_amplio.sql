-- Migración 012: Ampliar columna estado de solicitudes
-- Para admitir el estado "Requiere actualización" (22 caracteres).

ALTER TABLE solicitudes ALTER COLUMN estado TYPE VARCHAR(30);
