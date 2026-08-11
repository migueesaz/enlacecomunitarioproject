-- Migración 001: Esquema inicial de Enlace Comunitario
-- Todas las sentencias son idempotentes (IF NOT EXISTS) para poder
-- ejecutarse en cada inicio de la aplicación sin duplicar datos.

-- ============================================================================
-- 1. Tabla: habitantes
--    Ya existe en la base con un esquema parcial; CREATE TABLE IF NOT EXISTS
--    no la modifica. Debajo se reconcilian las columnas para que coincidan
--    con lo que la aplicación espera (id con secuencia, email opcional,
--    cédula y teléfonos como texto).
-- ============================================================================
CREATE TABLE IF NOT EXISTS habitantes (
    id_habitante SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    fecha_nac DATE,
    genero CHAR(1),
    telefono1 VARCHAR(20),
    telefono2 VARCHAR(20),
    direccion_1 VARCHAR(255),
    direccion_2 VARCHAR(255),
    categoria VARCHAR(20)
);

-- Reconciliación idempotente para bases existentes
ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS categoria VARCHAR(20);
ALTER TABLE habitantes ALTER COLUMN email DROP NOT NULL;
ALTER TABLE habitantes ALTER COLUMN cedula TYPE VARCHAR(20) USING cedula::text;
ALTER TABLE habitantes ALTER COLUMN telefono1 TYPE VARCHAR(20) USING telefono1::text;
ALTER TABLE habitantes ALTER COLUMN telefono2 TYPE VARCHAR(20) USING telefono2::text;

-- Asegurar que id_habitante genere su valor automáticamente.
-- Si la columna ya es IDENTITY/SERIAL no se modifica (no se permite
-- SET DEFAULT sobre una columna identity).
DO $$
DECLARE
    tiene_auto boolean;
BEGIN
    SELECT (is_identity = 'YES' OR column_default IS NOT NULL) INTO tiene_auto
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'habitantes'
      AND column_name = 'id_habitante';

    IF NOT tiene_auto THEN
        CREATE SEQUENCE IF NOT EXISTS habitantes_id_habitante_seq;
        ALTER TABLE habitantes ALTER COLUMN id_habitante
            SET DEFAULT nextval('habitantes_id_habitante_seq');
    END IF;
END $$;

-- Sincronizar la secuencia con el valor máximo existente (idempotente)
CREATE SEQUENCE IF NOT EXISTS habitantes_id_habitante_seq;
SELECT setval(
    'habitantes_id_habitante_seq',
    COALESCE((SELECT MAX(id_habitante) FROM habitantes), 0) + 1,
    false
);

-- ============================================================================
-- 2. Tabla: usuarios
--    Usuarios del sistema. El login actual (user_model.py) usa datos en
--    memoria; esta tabla queda lista para persistirlos y se siembra con los
--    mismos usuarios de demostración.
-- ============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    rol VARCHAR(20) NOT NULL DEFAULT 'vecino'
);

INSERT INTO usuarios (nombre, correo, password, telefono, direccion, rol)
VALUES
    ('Juan Pérez', 'vecino@gmail.com', 'vecino123', '123456789', 'Calle Falsa 123', 'vecino'),
    ('Admin', 'admin@cepav.com', 'admin123', '987654321', 'Calle Admin 456', 'admin')
ON CONFLICT (correo) DO NOTHING;

-- ============================================================================
-- 3. Tabla: solicitudes
--    Solicitudes de cartas (residencia, buena conducta, aval). La usa
--    models/cartas_model.py.
-- ============================================================================
CREATE TABLE IF NOT EXISTS solicitudes (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(255) NOT NULL,
    tipo_carta VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    fecha_solicitud DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX IF NOT EXISTS idx_solicitudes_estado ON solicitudes (estado);

-- ============================================================================
-- 4. Tabla: notificaciones
--    Notificaciones publicadas por el administrador. La usan los módulos de
--    administración y la bandeja de mensajes del vecino.
CREATE TABLE IF NOT EXISTS notificaciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE
);
