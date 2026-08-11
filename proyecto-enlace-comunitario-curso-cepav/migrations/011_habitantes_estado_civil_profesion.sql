-- Migración 011: Campos estado civil y profesión u oficio en habitantes
-- Se usan en el registro de habitantes y en la carta aval.

ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS estado_civil VARCHAR(50);
ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS profesion VARCHAR(100);
