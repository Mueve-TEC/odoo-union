# Import Test Files — odoo-union

CSVs y XLSX para probar manualmente los flujos de importación (base_import) de
los 4 módulos (`union_affiliation`, `union_contribution`, `union_school_position`,
`union_benefit_request`), incluyendo la **creación automática de afiliados**
desde la importación (`create_user_from_*` en Configuración).

Estos archivos NO se cargan solos: son insumos para el diálogo **Importar** de
la vista lista de cada modelo. No están en el addons path ni referenciados por
ningún `__manifest__.py`.

---

## 1. Contenido

| Archivo | Escenario | Flag requerido | Resultado esperado |
|---|---|---|---|
| `affiliates/affiliates_existing.xlsx` | 5 afiliados con los uids que usan todos los demás fixtures (10000001..10000005) | n/a | 5 afiliados creados con nombre, estado, DNI y datos de contacto |
| `positions/position_types.xlsx` | Tipos de cargo DOC / DIR / ADM (código, descripción, in_hours, dedicación) | n/a | 3 tipos de cargo creados |
| `positions/positions_existing.csv` | 3 cargos para afiliados demo existentes (10000001/10000003/10000004) | OFF (default) | 3 posiciones creadas, `affiliate_id` resuelto por uid |
| `positions/positions_new_affiliates.csv` | 2 cargos con uids desconocidos → auto-crea afiliados | **ON**: `create_user_from_position` | 2 afiliados nuevos (state=New) + 2 posiciones |
| `positions/positions_invalid_uids.csv` | uid `ABCD1234` (no numérico), `01234567` (cero inicial) | ver nota ↓ | ValidationError por fila — NO debe crear nada |
| `positions/positions_type_by_code.xlsx` | 3 cargos demo con `type_id` por código (`DOC`, `ADM`, `DIR`) | OFF (default) | 3 posiciones; tipo resuelto por `code` |
| `positions/positions_type_by_description.xlsx` | mismos 3 cargos, pero `type_id` por descripción (`Docente`, `Administrativo`, `Directivo`) | OFF (default) | 3 posiciones; tipo resuelto por `name` |
| `benefit_requests/requests_existing.csv` | 3 solicitudes para afiliados existentes | OFF (default) | 3 solicitudes draft, `partner_id` = partner del afiliado |
| `benefit_requests/requests_new_affiliates.csv` | uids desconocidos → auto-crea | **ON**: `create_user_from_request` | 2 afiliados nuevos + 2 solicitudes vinculadas |
| `benefit_requests/requests_invalid_uids.csv` | uids inválidos | ver nota ↓ | ValidationError — no crea nada |
| `benefit_requests/requests_existing.xlsx` | mismas 3 solicitudes que el CSV, con celdas de fecha reales | OFF (default) | 3 solicitudes draft, `partner_id` = partner del afiliado |
| `contributions/contributions_existing.csv` | 4 aportes para 10000002/10000003 | OFF (default) | 4 aportes, afiliado resuelto por uid |
| `contributions/contributions_existing.xlsx` | mismos 3 aportes que el CSV, con celdas de fecha reales | OFF (default) | 3 aportes, afiliado resuelto por uid |
| `contributions/contributions_new_affiliates.csv` | uids desconocidos → auto-crea | **ON**: `create_user_from_contribution` | 2 afiliados nuevos + 2 aportes |
| `contributions/contributions_invalid_uids.csv` | uids inválidos | cualquiera | ValidationError — no crea nada |

### Orden sugerido en una base sin datos demo

Dos fixtures sirven para arrancar una base que no tiene demo data. Importarlos
en este orden:

1. `positions/position_types.xlsx` → **Positions → Position's type**: crea
   `DOC` / `DIR` / `ADM`, que los fixtures de cargos usan como `type_id`.
2. `affiliates/affiliates_existing.xlsx` → **Affiliates**: crea los afiliados
   `10000001`..`10000005` que referencian los fixtures de cargos, aportes y
   solicitudes.
3. Cualquiera de los fixtures de cargos / aportes / solicitudes.

> Estos dos archivos están pensados para una base **sin** demo data. Si la base
> ya los tiene, `position_types.xlsx` crea tipos duplicados (el modelo no
> tiene restricción única sobre `code`) y `affiliates_existing.xlsx` falla con
> "There is already exist an affiliated with the same affiliate UID!".

Prerrequisitos que siguen siendo demo data y **no** tienen fixture todavía:

| Fixture a importar | Requiere primero (demo data) |
|---|---|
| `contributions/*` | códigos de aporte: `Aporte Normal`, `Aporte Extraordinario`, `Aporte Jubilado` |
| `benefit_requests/*` | tipos de solicitud: `Solicitud de Bolsones`, `Solicitud Simple` |
| `positions/positions_*` | caracteres: `TIT`, `INT`, `SUP` (y lugares `ESC01` si se usa la columna `workplace_id`) |

## 2. Cómo importar

1. Activar/desactivar el flag correspondiente en
   **Union → Configuration → Affiliation configuration**
   (`create_user_from_position` / `..._from_request` / `..._from_contribution`).
2. Ir a la vista **lista del modelo** correcto:
   - Affiliates → *Union → Affiliates → Affiliates list*
   - Position types → *Union → Positions → Position's type*
   - Positions → *Union → Positions → Positions list*
   - Benefit requests → *Union → Requests → Requests list*
   - Contributions → *Union → Contributions → Contributions list*
3. Botón **Importar** (⚙/icono de import) → subir el CSV o XLSX → verificar
   el mapeo sugerido (los headers usan nombres técnicos de campos, el mapeo
   debería ser automático) → **Test** → **Import**. En los XLSX, elegir la
   hoja correcta en el selector del diálogo.
4. Repetir dejando los flags en OFF salvo donde la tabla indique ON.

> Importante: cada archivo se importa desde SU modelo. Si se importa
> `positions_existing.csv` desde otro modelo, el mapeo fallará (es lo esperado).

### Nota sobre los archivos `_invalid_uids`

El mensaje de error depende del estado del flag:

- **Flag OFF** (positions / benefit_requests): el flujo corta antes, con
  *"Affiliate does not exist in the database (UID: …)"* — los chequeos de
  dígito/cero viven dentro de la rama de auto-creación.
- **Flag ON**: se llega a las validaciones específicas —
  *"El campo ID debe contener un número entero válido."* y
  *"El campo ID debe ser un número positivo."*
- **Contributions**: la validación de uid es **incondicional** (ver nota
  en §5), así que el mensaje específico aparece con el flag en cualquier estado.

## 3. Qué ejercita cada diseño de columna

- **Celda vacía en una columna Integer** (`affiliation_number`, `hs_amount`, …):
  la celda se escribe como `0`, no como `NULL`, porque `ir.fields.converter`
  devuelve `False` y `Integer.convert_to_column(False)` es `0`. En `hs_amount`
  eso dispara las constraints de los cargos en horas. En `affiliation_number`
  dos filas en blanco chocarían con `unique(affiliation_number)` (el error
  nombraría a un afiliado inexistente) y en una importación con `id` borraría
  el número ya guardado. Por eso `affiliation.affiliate` descarta el número en
  blanco: al crear la columna queda sin asignar (`NULL`) y al actualizar no se
  toca el valor guardado (ver `test_blank_affiliation_number_*`). Un archivo
  propio también puede dejar de lado la columna entera.
- **`type_id` con código o descripción** (`DOC`, `Docente`, …): el tipo de cargo
  se muestra como `[COD] Descripción` y, en contexto `import_file`, resuelve
  tanto por `code` como por `name` exactos.
- **`character_id` con código** (`TIT`, `INT`, …): su `name_search` sigue
  matcheando **solo por code** en contexto `import_file`. Usar "Titular" en el
  CSV NO resolvería.
- **`request_type_id` con nombre**: `benefit_request.request_type` usa su
  `_rec_name` (name), sin override de import.
- **`contribution_code_id` con descripción**: `_rec_name = description`.
- **`workplace_id` con código** (`ESC01`): `union.workplace.name_search`
  matchea name/code/complete_name.
- **Fila DIR sin `hs_amount`**: ejercita la constraint "hs_amount must be
  empty for positions that are not in hours" (si se le pone valor, falla).
- **`date_to` > `date_from`** solo en P-103: valida `_check_dates`.

### Prueba XLSX de `type_id` por código o descripción

`positions_type_by_code.xlsx` y `positions_type_by_description.xlsx` tienen
exactamente las mismas filas; solo cambia la columna `type_id`. Importar cada
archivo desde **Positions** y verificar que se crean las tres posiciones:

- el archivo por código ejercita `type_id` = `DOC`, `ADM`, `DIR`;
- el archivo por descripción ejercita `type_id` = `Docente`,
  `Administrativo`, `Directivo`, que solo resuelve porque
  `school_position.type` busca por `code` o `name` (`_rec_names_search`).

Las fechas son celdas Excel reales con formato `yyyy-mm-dd`, no texto, para
comprobar que el lector XLSX las convierte correctamente.

Los tipos (`DOC`, `ADM`, `DIR` / `Docente`, `Administrativo`, `Directivo`) y
los afiliados 10000001/10000003/10000004 son los del demo data. Usar una base
con demo (`sindicato_demo`) o crear esos registros antes de importar.

## 4. Verificaciones post-importación

### Afiliados creados automáticamente
*Union → Affiliates*: deben aparecer con state=New y los uids del CSV.
Verificar además que propagaron `personal_id`/`vat` cuando el CSV los trae.

### Posiciones
- Lista de cargos: filas nuevas; agrupar por **Sector** y por
  **Workplace Level 1..3** debe incluir las nuevas.
- Abrir el afiliado Juan Perez (10000001): página **Cargos** lista P-101.

### Solicitudes
- Lista de solicitudes: nuevas filas en estado **Draft** con la columna
  `state` visible.
- El partner del afiliado queda suscripto al chatter de la solicitud.

### Aportes
- Lista de aportes: nuevos importes; display_name
  `<Afiliado>,<fecha>`.
- Página **Aportes** del afiliado muestra los nuevos registros (orden fecha desc).

## 5. ~~Bug conocido~~ — FIXED

`contribution.affiliate_contribution._prepare_import_vals()` ahora valida
`import_uid` sólo dentro de la rama `if import_uid:`, permitiendo que los
fallbacks por `import_personal_id` / `import_vat` / `import_name` funcionen
cuando el uid no está presente.

El uid se validó de `Char` a `Integer` en todo el stack (ver commit
`[REFACTOR] union_*: change affiliate uid from Char to Integer`).

## 6. Limpieza

Los registros creados son datos reales en la DB. Para repetir una corrida:
eliminar las posiciones/solicitudes/aportes creados y los afiliados
auto-creados (states=New con los uids de prueba), o restaurar desde backup.
