# Migraciones de Base de Datos — Enlace Comunitario

Documento de migraciones del proyecto **Enlace Comunitario** (Consejo Comunal La Cruz).

## Base de datos

- **Motor:** PostgreSQL
- **Cliente:** `psycopg` (v3)
- **Conexión:** variables de entorno en `.env` (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- **Esquema:** `public`

## Cómo funcionan las migraciones

1. Al iniciar la aplicación, `main.py` ejecuta `ejecutar_migraciones()` (módulo `migrations/migrador.py`).
2. El migrador se conecta a PostgreSQL y crea, si no existe, la tabla de control **`schema_migrations`**, donde se registra cada migración aplicada (`version`, `applied_at`).
3. Lee los archivos `*.sql` y `*.py` de la carpeta `migrations/` en orden alfabético (por eso se numeran: `001_`, `002_`, ...). Los archivos `.py` deben exponer una función `up(cur)` que recibe el cursor de la transacción.
4. Aplica **solo** los archivos que aún no estén registrados en `schema_migrations`.
5. Cada archivo se ejecuta dentro de una **transacción**: si algo falla, se revierte todo y la aplicación muestra un error claro y se detiene.
6. Las migraciones ya aplicadas se ignoran en ejecuciones posteriores (no se duplican ni fallan).

## Lista de migraciones

| Archivo | Descripción |
|---------|-------------|
| `001_inicial.sql` | Esquema inicial: tablas `habitantes`, `usuarios`, `solicitudes` y `notificaciones`, con reconciliación idempotente de `habitantes`. |
| `002_tipos_solicitud.sql` | Catálogo `tipos_solicitud` y relación con `solicitudes`. |
| `003_roles.sql` | Catálogo `roles` y relación con `usuarios`. |
| `004_rol_habitantes.sql` | Rol del sistema para `habitantes`: columna `rol_id` y llave foránea hacia `roles`. |
| `005_usuarios_acceso_auditoria.sql` | `usuarios` pasa a ser solo acceso (vinculado a `habitantes`), campos `activo`/`bloqueado`/`ultimo_ingreso`, y auditoría `created_at`/`updated_at` en todas las tablas. |
| `006_solicitudes_activas_unicas.sql` | Índice único parcial sobre `solicitudes (usuario, tipo_solicitud_id)` que impide dos solicitudes activas del mismo tipo por vecino (activas = estado distinto de `Aprobada`/`Rechazada`). |
| `007_password_hashing.py` | Convierte las contraseñas de `usuarios` de texto plano a hashes bcrypt (idempotente; ignora valores que ya son hashes). |
| `008_vistas_notificaciones.sql` | Conteo de vistas: agrega `notificaciones.vistas` y crea `notificaciones_vistas` (quién y cuándo vio cada notificación). |
| `009_notificaciones_vistas_id_habitante.sql` | `notificaciones_vistas.usuario` pasa de guardar la cédula (texto) a guardar el `id_habitante` (entero) con llave foránea a `habitantes`. Convierte los registros existentes. |
| `010_habitantes_registrado_admin.sql` | Agrega `habitantes.registrado_por_admin` (BOOLEAN). Solo los habitantes creados desde la app se marcan con `TRUE`; los de demostración y los insertados directo en BD no aparecen en búsquedas ni filtros. |

### `001_inicial.sql`

**Tabla `habitantes`** — Registro censal de la comunidad.
- `id_habitante` SERIAL PRIMARY KEY (se asegura una secuencia por defecto).
- `nombre`, `apellido` VARCHAR NOT NULL.
- `cedula` VARCHAR(20) UNIQUE.
- `email` VARCHAR(150) UNIQUE (opcional).
- `fecha_nac` DATE, `genero` CHAR(1).
- `telefono1`, `telefono2` VARCHAR(20).
- `direccion_1`, `direccion_2` VARCHAR(255).
- `categoria` VARCHAR(20) (Adulto / NNA).

> Esta tabla ya existía en la base con un esquema parcial. La migración usa
> `CREATE TABLE IF NOT EXISTS` (no modifica la tabla existente) y luego aplica
> sentencias idempotentes para reconciliar el esquema: agrega `categoria` si
> falta, hace opcional el `email`, convierte `cedula` y teléfonos a texto y
> garantiza que `id_habitante` tenga secuencia.

**Tabla `usuarios`** — Credenciales y roles.
- `id` SERIAL PRIMARY KEY, `nombre` VARCHAR NOT NULL.
- `correo` VARCHAR(150) UNIQUE NOT NULL, `password` VARCHAR(255) NOT NULL.
- `telefono`, `direccion` VARCHAR, `rol` VARCHAR(20) DEFAULT `'vecino'`.
- Se siembran los usuarios de demostración (`vecino@gmail.com` / `admin@cepav.com`) con `ON CONFLICT DO NOTHING`.

**Tabla `solicitudes`** — Solicitudes de cartas (residencia, buena conducta, aval). La usa `models/cartas_model.py`.
- `id` SERIAL PRIMARY KEY, `usuario` VARCHAR NOT NULL.
- `tipo_carta` VARCHAR(50) NOT NULL.
- `estado` VARCHAR(20) DEFAULT `'Pendiente'` (Pendiente / Aprobada / Rechazada).
- `fecha_solicitud` DATE DEFAULT `CURRENT_DATE`.
- Índice sobre `estado`.

**Tabla `notificaciones`** — Comunicados de la comunidad.
- `id` SERIAL PRIMARY KEY, `titulo` VARCHAR(200) NOT NULL, `mensaje` TEXT.
- `fecha` DATE DEFAULT `CURRENT_DATE`.

### `002_tipos_solicitud.sql`

**Tabla `tipos_solicitud`** — Catálogo de tipos de solicitud (cartas, constancias).
- `id` SERIAL PRIMARY KEY, `nombre` VARCHAR(100) UNIQUE NOT NULL.
- `descripcion` TEXT, `activo` BOOLEAN DEFAULT `TRUE`.
- Se siembran los tipos base con `ON CONFLICT DO NOTHING`:
  Carta de Residencia, Constancia de Residencia, Carta de Buena Conducta y Carta Aval.

**Relación con `solicitudes`** — Se agrega la columna `tipo_solicitud_id` (opcional)
y la llave foránea `solicitudes_tipo_solicitud_fk` hacia `tipos_solicitud(id)`.
La columna es nullable para no romper solicitudes existentes; el agregado del
constraint es idempotente (se verifica en `pg_constraint` antes de crearlo).

### `003_roles.sql`

**Tabla `roles`** — Catálogo de roles de usuario.
- `id` SERIAL PRIMARY KEY, `nombre` VARCHAR(50) UNIQUE NOT NULL, `descripcion` TEXT.
- Se siembran los roles base con `ON CONFLICT DO NOTHING`: `admin` y `vecino`.

**Relación con `usuarios`** — Se agrega la columna `rol_id` (opcional) y la llave
foránea `usuarios_rol_fk` hacia `roles(id)`. Un `UPDATE` idempotente vincula los
usuarios existentes a su rol según su valor de texto (`rol`), rellenando solo los
`rol_id` que estén en `NULL`.

### `004_rol_habitantes.sql`

**Columna `habitantes.rol_id`** — Rol del sistema (admin/vecino) que tiene cada
habitante registrado. Se reutiliza el catálogo `roles` de la migración `003`.

- `ALTER TABLE habitantes ADD COLUMN IF NOT EXISTS rol_id INTEGER;`
- Llave foránea `habitantes_rol_fk` hacia `roles(id)`, creada de forma idempotente
  (se verifica en `pg_constraint` antes de crearla).

**Uso en la app** — El formulario de registro de habitantes (`pages/Admin/Poblacion.py`)
incluye un `selectbox` "Rol" (Admin/Vecino) que se guarda en `habitantes.rol_id`.
El modelo devuelve además `rol_nombre` (JOIN a `roles`) y `categoria` (Adulto/NNA,
calculada a partir de `fecha_nac`).

### `005_usuarios_acceso_auditoria.sql`

**`usuarios` pasa a ser una tabla solo de acceso.** Un habitante puede tener o no
un usuario de acceso, por lo que la información personal ya no se duplica:

- Se vincula con `habitantes` mediante `habitante_id` (relación opcional 1:1,
  constraint `usuarios_habitante_unique`).
- Se **eliminan** las columnas `nombre`, `correo`, `telefono` y `direccion` (viven
  en `habitantes`).
- Se **agregan**: `activo BOOLEAN DEFAULT TRUE`, `bloqueado BOOLEAN DEFAULT FALSE`
  y `ultimo_ingreso TIMESTAMPTZ`.

La credencial de login ahora es `habitantes.email`: `models/user_model.py` hace
JOIN `usuarios → habitantes → roles`, y el login solo se permite si el usuario está
activo y no bloqueado. Tras un login exitoso se actualiza `ultimo_ingreso`.

**Usuarios de demostración** (`vecino@gmail.com`, `admin@cepav.com`) sin habitante
vinculado: la migración crea su registro censal (cédula `USU-1`/`USU-2`) para no
perder el acceso.

**Auditoría** — Las tablas `habitantes`, `usuarios`, `solicitudes`, `notificaciones`,
`roles` y `tipos_solicitud` ahora tienen `created_at` y `updated_at`
(`TIMESTAMPTZ NOT NULL DEFAULT NOW()`). La función `set_updated_at()` y los triggers
`trg_*_updated_at` actualizan `updated_at` automáticamente en cada `UPDATE`.

**Modelo** — `UserModel` (en `models/user_model.py`) ahora ofrece además:
`registrar_ultimo_ingreso()`, `crear_usuario()` (crea o reactiva el acceso de un
habitante), `actualizar_estado()` (activa/bloquea cuentas), `obtener_usuario_por_habitante()`
y `cambiar_password()`.

**Cambio de contraseña obligatorio** — El acceso se gestiona desde el formulario de
edición de habitantes (`pages/Admin/Poblacion.py`): un `toggle` "Acceso al sistema"
(Sí/No, apagado por defecto). Al activarlo se permite establecer o cambiar la
contraseña; al desactivarlo se revoca el acceso (`activo = FALSE`).

Cuando el administrador establece o cambia la contraseña de un usuario, se limpia
`usuarios.ultimo_ingreso` (queda en `NULL`). Así, en el siguiente inicio de sesión
la app detecta que el vecino debe cambiar su contraseña y lo redirige a la página
`pages/cambiar_password.py` antes de mostrar el resto de la navegación. Tras cambiarla,
`ultimo_ingreso` se actualiza y el acceso queda normal.

**Política de contraseñas** — Tanto `pages/cambiar_password.py` como el formulario de
edición de habitantes validan la nueva contraseña con `models/user_model.py`
(`validar_password` / `evaluar_password`): mínimo 8 caracteres, al menos una mayúscula,
una minúscula, un número y un carácter especial. Además no se permite reutilizar la
contraseña actual (se compara con `password_coincide()`).

### `007_password_hashing.py`

**Contraseñas con hash bcrypt.** Reemplaza el almacenamiento en texto plano:

- Es una migración de datos en Python (el migrador soporta archivos `.py` con
  función `up(cur)`). No modifica el esquema: reutiliza la columna `password`.
- Convierte cada contraseña en texto plano a un hash bcrypt **en el mismo lugar**.
- Es idempotente: los valores que ya empiezan por `$2a$`/`$2b$`/`$2y$` se ignoran.
- `models/user_model.py` ahora siempre guarda hashes (`crear_usuario`,
  `cambiar_password`) y verifica con `bcrypt.checkpw`. Si un registro quedara en
  texto plano, el login lo detecta, compara y lo **migra automáticamente** a hash
  (upgrade transparente). `obtener_contrasena_actual()` se eliminó y se reemplazó
  por `password_coincide()` (compara contra el hash sin devolver la contraseña).

## Idempotencia ("CREATE IF NOT EXISTS")

Todas las migraciones son **re-ejecutables** y usan las cláusulas de PostgreSQL:

- `CREATE TABLE IF NOT EXISTS ...`
- `CREATE SEQUENCE IF NOT EXISTS ...`
- `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`
- `CREATE INDEX IF NOT EXISTS ...`
- `ALTER COLUMN ... SET DEFAULT` / `DROP NOT NULL` / `TYPE ... USING ...` (no fallan si ya están así)
- `INSERT ... ON CONFLICT DO NOTHING`

Por eso pueden ejecutarse en cada inicio de la app sin riesgos.

## Ejecución manual

```bash
python -m migrations.migrador
```

Para resetear desde cero (borrar el registro de migraciones y volver a aplicar):

```sql
DELETE FROM schema_migrations;
```

## Análisis del proyecto (hallazgos)

- **`habitantes`**: el esquema preexistente no coincidía con lo que espera la app
  (sin secuencia para `id_habitante`, `email` obligatorio, cédula/teléfonos
  numéricos). La migración `001` lo reconcilia.
- **`solicitudes`** y **`notificaciones`**: no existían en la base; se crean.
- **`usuarios`**: el login (`models/user_model.py`) aún usa datos hardcodeados.
  La tabla queda lista y sembrada con los mismos usuarios para conectar el login
  a la base en una próxima iteración.
- **Bugs detectados (sin corregir en esta entrega):**
  - `CartasController.listar()` llama a `obtener_solicitudes()` sin argumento,
    pero el modelo exige `id_solicitud`.
  - `CartasController.en_revision()` no existe en `CartasModel`.
  - `pages/Admin/Reportes/Censo.py` usa columnas `sexo`/`direccion`, pero el
    modelo devuelve `genero`/`direccion_1` (puede lanzar `KeyError`).
  - `Dashboard.py` y `Censo.py` dependen de datos en `st.session_state`, no de
    la base de datos.
