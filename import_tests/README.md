# Import Test Files — odoo-union

CSVs para probar manualmente los flujos de importación (base_import) de los
3 módulos con lógica `create`-from-import, incluyendo la **creación automática
de afiliados** desde la importación (`create_user_from_*` en Configuración).

Estos archivos NO se cargan solos: son insumos para el diálogo **Importar** de
la vista lista de cada modelo. No están en el addons path ni referenciados por
ningún `__manifest__.py`.

---

## 1. Contenido

| Archivo | Escenario | Flag requerido | Resultado esperado |
|---|---|---|---|
| `positions/positions_existing.csv` | 3 cargos para afiliados demo existentes (10000001/10000003/10000004) | OFF (default) | 3 posiciones creadas, `affiliate_id` resuelto por uid |
| `positions/positions_new_affiliates.csv` | 2 cargos con uids desconocidos → auto-crea afiliados | **ON**: `create_user_from_position` | 2 afiliados nuevos (state=New) + 2 posiciones |
| `positions/positions_invalid_uids.csv` | uid `ABCD1234` (no numérico), `01234567` (cero inicial) | ver nota ↓ | ValidationError por fila — NO debe crear nada |
| `benefit_requests/requests_existing.csv` | 3 solicitudes para afiliados existentes | OFF (default) | 3 solicitudes draft, `partner_id` = partner del afiliado |
| `benefit_requests/requests_new_affiliates.csv` | uids desconocidos → auto-crea | **ON**: `create_user_from_request` | 2 afiliados nuevos + 2 solicitudes vinculadas |
| `benefit_requests/requests_invalid_uids.csv` | uids inválidos | ver nota ↓ | ValidationError — no crea nada |
| `contributions/contributions_existing.csv` | 4 aportes para 10000002/10000003 | OFF (default) | 4 aportes, afiliado resuelto por uid |
| `contributions/contributions_new_affiliates.csv` | uids desconocidos → auto-crea | **ON**: `create_user_from_contribution` | 2 afiliados nuevos + 2 aportes |
| `contributions/contributions_invalid_uids.csv` | uids inválidos | cualquiera | ValidationError — no crea nada |

## 2. Cómo importar

1. Activar/desactivar el flag correspondiente en
   **Union → Configuration → Affiliation configuration**
   (`create_user_from_position` / `..._from_request` / `..._from_contribution`).
2. Ir a la vista **lista del modelo** correcto:
   - Positions → *Union → Positions → Positions list*
   - Benefit requests → *Union → Requests → Requests list*
   - Contributions → *Union → Contributions → Contributions list*
3. Botón **Importar** (⚙/icono de import) → subir el CSV → verificar el
   mapeo sugerido (los headers usan nombres técnicos de campos, el mapeo
   debería ser automático) → **Test** → **Import**.
4. Repetir dejando los flags en OFF salvo donde la tabla indique ON.

> Importante: cada archivo se importa desde SU modelo. Si se importa
> `positions_existing.csv` desde otro modelo, el mapeo fallará (es lo esperado).

### Nota sobre los archivos `_invalid_uids`

El mensaje de error depende del estado del flag:

- **Flag OFF** (positions / benefit_requests): el flujo corta antes, con
  *"Affiliate does not exist in the database (UID: …)"* — los chequeos de
  dígito/cero viven dentro de la rama de auto-creación.
- **Flag ON**: se llega a las validaciones específicas —
  *"El campo ID debe contener únicamente números."* y
  *"El campo ID no puede comenzar con cero."*
- **Contributions**: la validación de dígitos es **incondicional** (ver bug
  en §5), así que el mensaje específico aparece con el flag en cualquier estado.

## 3. Qué ejercita cada diseño de columna

- **`type_id` / `character_id` con códigos** (`DOC`, `TIT`, …): en contexto
  `import_file` el `name_search` de ambos modelos matchea **solo por code**,
  nunca por nombre. Usar "Docente" en el CSV NO resolvería.
- **`request_type_id` con nombre**: `benefit_request.request_type` usa su
  `_rec_name` (name), sin override de import.
- **`contribution_code_id` con descripción**: `_rec_name = description`.
- **`workplace_id` con código** (`ESC01`): `union.workplace.name_search`
  matchea name/code/complete_name.
- **Fila DIR sin `hs_amount`**: ejercita la constraint "hs_amount must be
  empty for positions that are not in hours" (si se le pone valor, falla).
- **`date_to` > `date_from`** solo en P-103: valida `_check_dates`.

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

## 5. ⚠️ Bug conocido detectado al diseñar estos CSVs

`contribution.affiliate_contribution._prepare_import_vals()` valida
`import_uid.isdigit()` **antes** de los fallbacks por
`import_personal_id` / `import_vat` / `import_name`. Consecuencia:

- Una fila SIN `import_uid` (aunque traiga un `import_personal_id` válido)
  siempre lanza *"El campo ID debe contener únicamente números."* — los
  fallbacks de búsqueda son código muerto hoy.
- Por eso TODAS las filas de aportes de estos CSVs incluyen `import_uid`.

Fix sugerido (pendiente): mover la validación dentro de la rama que usa el
uid (búsqueda + auto-creación) y validar `import_uid` sólo si está presente.

## 6. Limpieza

Los registros creados son datos reales en la DB. Para repetir una corrida:
eliminar las posiciones/solicitudes/aportes creados y los afiliados
auto-creados (states=New con los uids de prueba), o restaurar desde backup.
