# Manual Testing Guideline — odoo-union Migration to Odoo 19

> **Purpose:** Exhaustive manual testing checklist to verify the `odoo-union` 16.0→19.0 migration (including all features ported from 16.0 and fixes from 18.0) works correctly in the running Odoo 19 instance.
> **Date:** 2026-08-21
> **Environment:** Odoo 19 Community, database `sindicato`, demo data loaded (module version `19.0.1.0.0`).
> **Modules under test:** `union_affiliation`, `union_benefit_request`, `union_contribution`, `union_school_position`.

---

## 0. How to Use This Guideline

1. Log in as **admin** at http://localhost:8069 (database: `sindicato`).
2. Work through sections **1 → 12** in order.
3. For each test case, record: **PASS / FAIL** + a note.
4. Use the **demo data** (Section 1) as the baseline. Do NOT delete it while testing — it is `noupdate` but persists in the DB.
5. To reset test data after destructive tests, delete/recreate records or re-upgrade the module (`-u` re-runs `noupdate` data only for missing records; already-existing records are untouched).

---

## 1. Demo Data Inventory (verify all exist)

Open each menu and confirm the expected demo records are present.

### Affiliates (`Union → Affiliates → Affiliates list`)
| UID | Name | State | Quote | Affiliation # |
|---|---|---|---|---|
| 10000001 | Juan Perez | New | No | — |
| 10000002 | Maria Garcia | Affiliated | Sí | 1 |
| 10000003 | Carlos Rodriguez | Affiliated | Sí | 2 |
| 10000004 | Ana Martinez | Not affiliated | No | — |
| 10000005 | Pedro Sanchez | Disaffiliated | No | 3 |

### Workplaces (`Union → Affiliates → Lugares de trabajo`)
| Name | Code | Level | Complete name |
|---|---|---|---|
| Seccional Central | SEC01 | 1 | Seccional Central |
| Departamento Administracion | DEP01 | 2 | Seccional Central / Departamento Administracion |
| Oficina de Personal | OF01 | 3 | Seccional Central / Departamento Administracion / Oficina de Personal |
| Escuela Tecnica | ESC01 | 1 | Escuela Tecnica |

### Positions (`Union → Positions → Positions list`)
| # | Affiliate | Type | Sector | Featured | Workplace L1/L2/L3 |
|---|---|---|---|---|---|
| P-001 | Maria Garcia | Docente | Educacion | Sí | Escuela Tecnica |
| P-002 | Maria Garcia | Administrativo | Administracion | No | Seccional / Departamento / Oficina |
| P-003 | Carlos Rodriguez | Directivo | Direccion | Sí | Escuela Tecnica |
| P-004 | Carlos Rodriguez | Docente | Educacion | No | Escuela Tecnica |
| P-005 | Juan Perez | Administrativo | Sin asignar | No | Sin lugar de trabajo |

### Benefit Requests (`Union → Requests → Requests list`)
| Expedient | Applicant | Type | State |
|---|---|---|---|
| EXP-2026-001 | Maria Garcia | Solicitud de Bolsones | Draft |
| EXP-2026-002 | Carlos Rodriguez | Solicitud de Bolsones | Requested |
| EXP-2024-003 | Maria Garcia | Solicitud de Bolsones | Authorized |
| EXP-2024-004 | Carlos Rodriguez | Solicitud de Bolsones | Finalized |
| EXP-2024-005 | Maria Garcia | Solicitud Simple | Rejected |
| — | Juan Perez | Solicitud Simple | Canceled |

### Contributions (`Union → Contributions → Contributions list`)
| Date | Affiliate | Code | Amount |
|---|---|---|---|
| 2024-06-15 | Maria Garcia | NOR | 5000 |
| 2024-03-10 | Maria Garcia | NOR | 4500 |
| 2024-06-20 | Carlos Rodriguez | JUB | 3500 |
| 2024-01-30 | Maria Garcia | EXT | 10000 |

### Affiliate Children (`Union → Affiliates → Affiliate's childs`)
| Name | Personal ID | Handicapped | Verified |
|---|---|---|---|
| Sofia Perez | 51123456 | No | Sí |
| Diego Perez | 51234567 | Sí | No |

---

## 2. Installation & Integrity Checks

| ID | Test | Steps | Expected |
|---|---|---|---|
| 2.1 | Module versions | `Apps` search `union_*` | All 4 at `19.0.1.0.0`, "Installed" |
| 2.2 | SQL constraints exist | `psql -d sindicato -c "\d affiliation_affiliate"` | `affiliation_affiliate_uid_unique` and `affiliation_affiliate_unique_affiliation_number` UNIQUE constraints present |
| 2.3 | SQL functions exist (post_init_hook) | `psql -d sindicato -c "\df mapState"` (and `translateState`, `calculateInconsistencies`, `calcInconsByType`) | 4 PL/pgSQL functions exist |
| 2.4 | Home action | Log out, log in as admin | Home screen shows Affiliates list |
| 2.5 | Server actions | On Affiliates list, select records → Action menu | "Enviar Email" / mass mail action present |

---

## 3. Affiliate CRUD (`union_affiliation`)

### Create
| ID | Test | Steps | Expected |
|---|---|---|---|
| 3.1 | Create affiliate (valid) | Affiliates list → Create. uid=`12345678`, name=Test, state=New | Record created; partner auto-created (partner form accessible via "Ver Compañía/Contacto") |
| 3.2 | uid not numeric | Create with uid=`ABC123` | ValidationError "El campo ID debe contener únicamente números." |
| 3.3 | uid leading zero | Create with uid=`01234567` | ValidationError "El campo ID no puede comenzar con cero." |
| 3.4 | duplicate uid | Create two affiliates with uid=`12345678` | Second fails with unique constraint error |
| 3.5 | duplicate affiliation_number | Set two affiliates to affiliation_number=`99` | Second fails with unique constraint error |
| 3.6 | state advanced without type | Create with state=Affiliated but no "Tipo de relación laboral" | ValidationError (type required) |
| 3.7 | type required only when advanced | Create state=New, no type | OK (no error) |

### Update / State machine
| ID | Test | Steps | Expected |
|---|---|---|---|
| 3.8 | Edit allowed fields | Open Juan Perez (New) → edit personal data | Save OK |
| 3.9 | uid readonly when advanced | Open Maria Garcia (Affiliated) → uid field | Readonly (not editable) |
| 3.10 | log tracking | Change Maria's quote via Set Contributor | "Log" field on Affiliate logs page appends "field quote changed from ... to ..." |
| 3.11 | seniority_years | Open Maria Garcia → Employment info | seniority_years computed (>0 given seniority 2023-03-15) |

### Unlink
| ID | Test | Steps | Expected |
|---|---|---|---|
| 3.12 | Delete affiliate (New state) | Delete Juan Perez | Affiliate + linked partner deleted (delegated inheritance cleanup) |
| 3.13 | Delete affiliate with constraint | Try deleting Maria Garcia (has positions/contributions/children) | Blocked (ondelete=restrict on related models) or warns |

### _name_search
| ID | Test | Steps | Expected |
|---|---|---|---|
| 3.14 | Search by uid | Affiliates search: type `10000002` | Maria Garcia found |
| 3.15 | Search by personal_id | Search: type `30234567` | Maria Garcia found |
| 3.16 | Search by name | Search: type `Maria` | Maria Garcia found |

---

## 4. Affiliate State Machine (`union_affiliation`)

> **Important:** The state buttons are gated by `group_affiliation_change_state` (change state) and `group_affiliation_change_quote` (quote). Verify you have these groups.

### Affiliation flow (config default: `affiliation_start = on_confirm`)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 4.1 | Affiliate (Juan, New) | Open Juan → click **Affiliatear** | State → Pending suscribe; quote → No |
| 4.2 | Confirm affiliation | With state=pending_suscribe → click **Confirmar afiliación** | Opens affiliation number wizard; state → Affiliated, quote → Sí |
| 4.3 | Sequence used | After confirming, check affiliation_number | Assigned from `next_affiliation_number_seq` (increments) |

### Affiliation flow (config `affiliation_start = on_affiliate`)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 4.4 | Reconfigure | Configuration → Affiliation configuration → `affiliation_start` = On affiliate | Saved |
| 4.5 | Affiliate (Ana, Not affiliated) | Ana → Affiliatear | Opens wizard immediately (affiliation number entry); state → pending_suscribe after wizard confirm |
| 4.6 | Restore default | Set `affiliation_start` back to On confirm | Saved |

### Disaffiliation
| ID | Test | Steps | Expected |
|---|---|---|---|
| 4.7 | Disaffiliate (Carlos, Affiliated) | Carlos → **Desafiliar** | State → pending_unsuscribe |
| 4.8 | Confirm disaffiliation | Carlos (pending_unsuscribe) → **Confirmar desafiliación** | State → Disaffiliated; quote → No; disaffiliation_date set (if config on_confirm) |

### Other transitions
| ID | Test | Steps | Expected |
|---|---|---|---|
| 4.9 | Archive (from Affiliated) | Maria → **Archivar** | State → Historical; quote toggles off |
| 4.10 | Set Contributor (Affiliated) | Maria → **Establecer Cotizante** | quote toggles |
| 4.11 | Archive permission | Log in as user WITHOUT `group_affiliation_admin` → Archive | UserError "Admin affiliation permission is required to archive records." |

### Affiliation periods
| ID | Test | Steps | Expected |
|---|---|---|---|
| 4.12 | Open period via action | Affiliate (Juan) → opens affiliation_number/period wizard | Period record created (from_date set) |
| 4.13 | Two open periods blocked | Try opening a second affiliation period for same affiliate | "There is already an open period!" |
| 4.14 | Edit closed period | Close a period (to_date + closed=True), then try editing it | "You can't edit a closed period!" |

---

## 5. Affiliate Configuration (`union_affiliation`)

| ID | Test | Steps | Expected |
|---|---|---|---|
| 5.1 | Singleton form | Union → Configuration → Affiliation configuration | Single form (create/delete disabled), res_id=1 |
| 5.2 | Name i18n | With es_AR active, open config | Name shows "Configuración" |
| 5.3 | next_affiliation_number sync | Set next_affiliation_number=50, save | `ir.sequence next_affiliation_number_seq` number_next_actual becomes 50 |
| 5.4 | sequence toggle | Uncheck enable_affiliation_number_sequence → save | Wizard's affiliation_number becomes editable (affiliation_number_edition) |
| 5.5 | All 4 module sections | Open config | Sections: affiliation_start/set_disaffiliation_date; affiliation number config; **Requests' configuration** (create_user_from_request); **Contribution's configuration** (create_user_from_contribution); **School Position's configuration** (create_user_from_position) |

---

## 6. Workplace Hierarchy (`union_affiliation`)

| ID | Test | Steps | Expected |
|---|---|---|---|
| 6.1 | Create workplace | Lugares de trabajo → Create (name, code) | Saved; level=1; complete_name=name |
| 6.2 | Create child | Create with parent=Seccional Central | level=2; complete_name="Seccional Central / X" |
| 6.3 | Recursion blocked | Set a workplace's parent to its own descendant | ValidationError "You cannot create a recursive workplace hierarchy." |
| 6.4 | Unique name/code | Create workplace with code=SEC01 (exists) | ValidationError |
| 6.5 | complete_name recompute | Rename a parent workplace | Child complete_names update (stored recursive compute) |
| 6.6 | name_search by code | Workplace search: type `ESC01` | Escuela Tecnica found |
| 6.7 | Affiliate count | Open Escuela Tecnica | affiliate_count reflects Maria/Carlos (main_workplace_id) |

### Delete wizard (new from 16.0)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 6.8 | Delete workplace with dependents | Escuela Tecnica → **Eliminar** (button) | Delete wizard opens showing impact: descendants + affected affiliates count |
| 6.9 | Confirm delete | Wizard → **Sí, eliminar** | Workplace + descendants deleted; returns to list with active filter |
| 6.10 | Direct unlink blocked | From list, try deleting a workplace via checkbox → Delete (not the form button) | ValidationError directing to use the Delete button |
| 6.11 | Cancel wizard | Open wizard → **Cancelar** | Nothing deleted; wizard closes |

---

## 7. Positions (`union_school_position`)

### CRUD & fields
| ID | Test | Steps | Expected |
|---|---|---|---|
| 7.1 | Create position | Positions → Create. affiliate=Maria, type=Docente, character=Titular | Saved |
| 7.2 | sector field (new) | Create position with sector="Educacion" | sector saved; appears in form + list |
| 7.3 | hs_amount required for hours | Type=Docente (in_hours=True) with hs_amount=0 | ValidationError "The hours amount must be greater than zero..." |
| 7.4 | hs_amount must be empty for non-hours | Type=Directivo (in_hours=False) with hs_amount=10 | ValidationError "must be empty for positions that are not in hours" |
| 7.5 | date_to after date_from | date_from=2024-01-01, date_to=2023-01-01 | ValidationError "The end date must be later..." |
| 7.6 | registration_date future | registration_date=2099-01-01 | ValidationError "The registration date cannot be in the future." |

### Featured (new from 16.0)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 7.7 | Set featured action | Select position(s) → Action → **Set Featured** | featured=True; list row decorated (highlighted) |
| 7.8 | Unset featured action | Select position(s) → Action → **Unset Featured** | featured=False |

### Workplace levels compute
| ID | Test | Steps | Expected |
|---|---|---|---|
| 7.9 | 3-level hierarchy | Open P-002 (workplace=Oficina de Personal) | workplace_level1="Seccional Central", level2="Departamento Administracion", level3="Oficina de Personal" |
| 7.10 | No workplace | Open P-005 (no workplace) | All levels "Sin lugar de trabajo" |
| 7.11 | Label correctness | Model field workplace_level2 | string = "Workplace Level 2" (regression: was duplicated Level 1) |

### Search/group-by
| ID | Test | Steps | Expected |
|---|---|---|---|
| 7.12 | Filter Featured | Search → filter "Featured" | Only featured positions |
| 7.13 | Group by sector | Search → Group By → Sector | Positions grouped by sector |
| 7.14 | Group by workplace levels | Search → Group By → Workplace Level 1/2/3 | Hierarchical grouping works |
| 7.15 | Group by affiliate state | Search → Group By → Affiliate State | Grouped (Affiliated, New, ...) |
| 7.16 | Search by uid | Positions search: type `10000002` | Maria Garcia's positions found |

### _compute_display_name
| ID | Test | Steps | Expected |
|---|---|---|---|
| 7.17 | Display name | Position list/man y2o | Shows "TypeName, AffiliateName" |

---

## 8. Affiliate Position Extensions (`union_school_position`)

| ID | Test | Steps | Expected |
|---|---|---|---|
| 8.1 | Cargos page in affiliate form | Open Maria Garcia → **Cargos** notebook page | Lists her positions (P-001, P-002) with type/character/workplace/dedication/hours/dates |
| 8.2 | has_featured_position (new) | Maria has P-001 featured → open her search filter "Tiene cargo destacado" | Maria appears (True) |
| 8.3 | has_featured_position False | Juan Perez (no featured positions) → filter "Tiene cargo destacado" | Juan NOT in results |
| 8.4 | position_type_ids | Maria's affiliate form/filters | position_type_ids = Docente + Administrativo |
| 8.5 | position_registration_date (new) | Affiliates search → Group By → "Fecha de registro (Cargos)" | Dates from positions' registration_date appear as groupable records |
| 8.6 | Deduplicated dates | Verify in `school_position.registration.date` model | One record per unique date (no dupes) |

---

## 9. Benefit Requests (`union_benefit_request`)

### Workflow (full state machine)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.1 | Create request | Requests → Create. partner=Maria (partner), type=Solicitud de Bolsones | State=Draft |
| 9.2 | Submit Request | Open draft → **Solicitar** | State=Requested; request_date set today |
| 9.3 | Authorize | Requested → **Autorizar** (needs admin group) | State=Authorized |
| 9.4 | Finalize | Authorized → **Finalizar** | State=Finalized |
| 9.5 | Reject | Requested → **Rechazar** | State=Rejected |
| 9.6 | Cancel | Any active → **Cancelar** | State=Canceled |
| 9.7 | Return to draft (finalized/canceled) | Finalized → **Volver a borrador** (admin) | State=Draft |
| 9.8 | Return to draft non-admin (finalized) | Log in as non-admin → Volver a borrador on finalized | ValidationError "Only users with admin permissions..." |

### Amount validation (type with "Importes" group = Solicitud de Bolsones)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.9 | Requested amount <= 0 | Draft (Bolsones type) with requested_amount=0 → Solicitar | ValidationError "Requested amount must be major to zero" |
| 9.10 | Authorized amount <= 0 | Requested (Bolsones) with authorized_amount=0 → Autorizar | ValidationError |
| 9.11 | Paid amount > authorized | Authorized (Bolsones), paid_amount > authorized_amount → Finalizar | ValidationError |
| 9.12 | full_doc required | Finalize with require_full_doc=True and full_doc=False | ValidationError "The documentation must be completed" |

### hide_* fields (group-driven visibility)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.13 | Bolsones type shows Amounts page | Open draft (Bolsones) | "Importes" notebook page visible (has Importes group) |
| 9.14 | Simple type hides everything | Open draft (Solicitud Simple - no groups) | No Importes/Bolsones/Notas pages |
| 9.15 | Notas type shows Notes | Open (Solicitud de Notas) | Notes page visible |

### who_apply / meet_reqs
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.16 | everybody type allows anyone | Solicitud de Bolsones (everybody) → authorize | OK regardless of affiliate state |
| 9.17 | affiliates-only + state check | Solicitud de Notas (affiliates, state=Affiliated, quote=True) on a Non-affiliated applicant | authorize raises ValidationError (state mismatch) |
| 9.18 | Non-affiliate applicant | Create request with a plain partner (not an affiliate) | Allowed when who_apply=everybody |

### Chatter / tracking (new tracking=True)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.19 | Field change logged | Change expedient on a request → save | Chatter message "<b>Expediente/resolución</b> changed from ... to ..." |
| 9.20 | State change logged | Request → Authorize | Chatter shows state change |
| 9.21 | last_state/last_change_state | After a state change, inspect fields | last_state holds previous state label; last_change_state = today |
| 9.22 | Suggested recipients | Open request chatter → suggest recipients | Partner (applicant) suggested |

### Search / display
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.23 | State column in list | Requests list | State column visible |
| 9.24 | Group by state | Search → Group By → State | Grouped |
| 9.25 | display_name | m2o on request | "Type - ApplicantName" |

### Benefit requests in affiliate form
| ID | Test | Steps | Expected |
|---|---|---|---|
| 9.26 | Solicitudes page | Open a partner that is an affiliate → Solicitudes page | Their benefit requests listed (inline: request_date, type, expedient, full_doc, state) |

---

## 10. School Benefits (`union_benefit_request`)

| ID | Test | Steps | Expected |
|---|---|---|---|
| 10.1 | School benefit types | Union → Requests → School benefit types | 14 types present (Nacimiento, Inicial..., Primario...) |
| 10.2 | Create school benefit | School benefits → Create. partner, type, child | Saved |
| 10.3 | Child domain | In a school benefit for Maria, child field | Only Maria's children (Sofia, Diego) selectable |
| 10.4 | Child ownership constraint | Try selecting a child not belonging to the applicant | ValidationError "The child must belong to the affiliate" |
| 10.5 | delivered toggle | Edit a school benefit's delivered | Only editable when request in new/requested/authorized |
| 10.6 | display_name | School benefit display | "partner,benefit_type" |

---

## 11. Contributions (`union_contribution`)

### CRUD
| ID | Test | Steps | Expected |
|---|---|---|---|
| 11.1 | Create contribution | Contributions → Create. affiliate, date, amount, code | Saved; display_name = "AffiliateName,YYYY-MM-DD" |
| 11.2 | date=False display_name (regression) | In a new unsaved contribution, display_name | No crash (fix b2d4397) |
| 11.3 | Code display_name | Contribution code m2o | Shows description (not code) |
| 11.4 | Search by code description | Contributions search: type `Extraordinario` | EXT code found |
| 11.5 | Group by affiliate/code/date | Search → Group By | 3 group options (Afiliado, Código de Aporte, Fecha) |
| 11.6 | Admin-only audit fields | As admin, contribution list | create_uid/create_date/write_uid/write_date visible |

### Contributions in affiliate form
| ID | Test | Steps | Expected |
|---|---|---|---|
| 11.7 | Aportes page | Open Maria Garcia → **Aportes** page | Her contributions listed (date desc) |

---

## 12. Inconsistencies (`union_contribution`)

### Query wizard
| ID | Test | Steps | Expected |
|---|---|---|---|
| 12.1 | Open query wizard | Union → Contributions → **Query inconsistencies** | Wizard form opens (target=new) |
| 12.2 | Required fields | Query with empty from/to | ValidationError (required) |
| 12.3 | from_date <= to_date | from > to | ValidationError |
| 12.4 | Run "No cotizante con aportes" | contribute=True, not_contribute=False, date range covering demo contributions | Results list opens; affiliates with quote=False but contributions appear |
| 12.5 | Run "Cotizante sin aportes" | not_contribute=True | Affiliated quote=True affiliates without contributions in range appear |
| 12.6 | Filter by affiliate type | Select type filter in wizard | Results restricted to that type |
| 12.7 | No inconsistencies | Empty date range / no matches | ValidationError "There aren't inconsistencies" |
| 12.8 | translateState SQL used | Inspect result descriptions | "Cotizante - <translated state>" present (e.g. "Cotizante - Nuevo") |

### Result list actions
| ID | Test | Steps | Expected |
|---|---|---|---|
| 12.9 | Group by description | Results → Group By → Descripción | Grouped by inconsistency type |
| 12.10 | Group by affiliate state/type/quote | Results → Group By | affiliate_state, affiliate_type_id, quote options |
| 12.11 | display_name | Result record | "Inconsistencia: <AffiliateName>" |

### Set/Unset quote (server actions)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 12.12 | Set quote | Select an inconsistency where affiliate is Affiliated & quote=False → Action → **Cambiar a Cotizante** | Affiliate quote becomes True; message posted "Estado cotizante cambiado a Cotizante desde Inconsistencias." |
| 12.13 | Unset quote | Select where quote=True → Action → **Cambiar a No Cotizante** | Affiliate quote becomes False; message posted |
| 12.14 | Set quote on non-affiliated | Select where affiliate state != Affiliated → Cambiar a Cotizante | ValidationError "Solo se puede cambiar el estado cotizante si el/la afiliado/a ... se encuentra en estado Afiliado/a." |

### Change state wizard
| ID | Test | Steps | Expected |
|---|---|---|---|
| 12.15 | Open wizard | Select inconsistency(ies) → Action → wizard (server action) | Wizard opens with the selected inconsistencies |
| 12.16 | Same-state validation | Pick a new_state equal to affiliate's current state | ValidationError "ya se encuentra en el estado seleccionado" |
| 12.17 | Change to affiliated | new_state=Affiliated, affiliate type provided | Affiliate becomes Affiliated; quote=True; message posted; wizard closes |
| 12.18 | Change to pending_suscribe | new_state=Pending suscribe | Runs affiliate_() flow (opens/confirms affiliation number wizard programmatically) |
| 12.19 | Change to historical | new_state=Historical | archive_() called; state=Historical |
| 12.20 | affiliate_type required | new_state=Affiliated on affiliate without type, no type provided | ValidationError (type required) |
| 12.21 | affiliate_type_id prefill | Provide affiliate_type_id in wizard | Written to affiliate before state change |

---

## 13. Search Views & Filters (Odoo 19 `<group>` removal)

> **Migration check:** In Odoo 19, search views must NOT contain `<group>` tags (removed during migration). All filters should render at root level.

| ID | Test | Steps | Expected |
|---|---|---|---|
| 13.1 | Affiliate search view loads | Open Affiliates list → search bar | No server error; all filters + group-by visible at root level |
| 13.2 | Position search view loads | Open Positions list → search | No `<group>` error; sector/workplace group-bys present |
| 13.3 | Benefit request search loads | Open Requests → search | No error; state/type/date group-bys present |
| 13.4 | Inconsistencies result search loads | Open Inconsistencies list → search | Group-by filters present (description/status/state/type/quote) |
| 13.5 | Contribution search loads | Open Contributions → search | No error; affiliate/code/date group-bys present |
| 13.6 | Inherited search (school_position on affiliate) | Open Affiliates search → verify | "Tiene cargo destacado", "Tipo de cargo", "Fecha de registro (Cargos)" present (inherited XPath `//search` works) |

---

## 14. Import Flows (create-from-import, config-gated)

> **Prerequisite:** These flows trigger when importing via base_import with context `import_file`. The auto-create branches only activate when the corresponding config flag is enabled.

### Position import (`union_school_position`)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 14.1 | Import resolves existing affiliate | Import positions CSV with import_uid=10000002 (Maria exists) | affiliate_id resolved to Maria |
| 14.2 | Auto-create disabled | import_uid=99999999 (unknown), config create_user_from_position=OFF | ValidationError "Affiliate does not exist in the database..." |
| 14.3 | Auto-create enabled | Set create_user_from_position=ON; import unknown uid | New affiliate auto-created (state=New, uid=imported); position linked |
| 14.4 | Invalid uid in import | import_uid=ABC123 with auto-create ON | ValidationError "El campo ID debe contener únicamente números." |
| 14.5 | Leading-zero uid in import | import_uid=01234567 with auto-create ON | ValidationError "El campo ID no puede comenzar con cero." |
| 14.6 | Restore config | Set create_user_from_position back to OFF | — |

### Benefit request import (`union_benefit_request`)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 14.7 | Import resolves existing | import_uid=10000002 | partner_id = Maria's partner |
| 14.8 | Auto-create disabled | unknown uid, create_user_from_request=OFF | ValidationError |
| 14.9 | Auto-create enabled | create_user_from_request=ON; unknown uid + import_name | Affiliate auto-created; request linked to new partner |
| 14.10 | Restore config | Set back OFF | — |

### Contribution import (`union_contribution`)
| ID | Test | Steps | Expected |
|---|---|---|---|
| 14.11 | Import resolves by uid | import_uid=10000002 | affiliate resolved |
| 14.12 | Import resolves by personal_id | import_personal_id=30234567 (no uid) | Maria resolved by personal_id |
| 14.13 | Import resolves by vat | import_vat (if Maria has CUIL/vat) | Resolved by vat |
| 14.14 | Auto-create disabled | unknown all fields, create_user_from_contribution=OFF | ValidationError |
| 14.15 | Auto-create enabled | create_user_from_contribution=ON; unknown uid + import_name | Affiliate auto-created |
| 14.16 | Invalid uid | import_uid=ABC123 | ValidationError "El campo ID debe contener únicamente números." |

---

## 15. Security / Permissions

| ID | Test | Steps | Expected |
|---|---|---|---|
| 15.1 | Read-only group | Create user with only read groups for each module | Can view lists/forms, cannot create/edit |
| 15.2 | Write group | Add write group | Can create/edit, cannot delete for restricted models (e.g. affiliation_period write=R-only) |
| 15.3 | Admin group | Add admin group | Full CRUD |
| 15.4 | change_state group | Without it, state buttons hidden | Affiliate state buttons not shown |
| 15.5 | change_quote group | Without it, Set Contributor hidden | Not shown |
| 15.6 | Emails menu | Without group_affiliation_emails | "Affiliate emails" menu hidden |
| 15.7 | Archive/unarchive permission | Non-admin tries archive | UserError (already tested 4.11) |
| 15.8 | change_state_wizard access | Wizard requires group_affiliation_change_state | Non-member cannot open wizard |
| 15.9 | base.group_user read on positions | Plain internal user (no union groups) opens Positions | Read access (internal read rules present) |
| 15.10 | Menu gating | Without read groups, Union menu hidden | Not visible |

---

## 16. Cross-Module Integration

| ID | Test | Steps | Expected |
|---|---|---|---|
| 16.1 | Affiliate → Positions | Maria form → Cargos page → open a position | Position form opens with affiliate prefilled |
| 16.2 | Affiliate → Contributions | Maria form → Aportes page → open a contribution | Contribution form opens with affiliate prefilled |
| 16.3 | Affiliate → Benefit requests | Maria form → Solicitudes page | Her requests listed |
| 16.4 | Partner → Affiliate | Partner form → "Ver Afiliado" stat button (if is_affiliate) | Opens affiliate form |
| 16.5 | Partner → Benefit requests | Partner form → Solicitudes page | Requests for that partner |
| 16.6 | Inconsistency → Affiliate | Result record → affiliate → open | Affiliate form opens |
| 16.7 | Inconsistency related fields | Result record | affiliate_state, affiliate_type_id, quote mirror the affiliate (stored related) |
| 16.8 | Deletion cascades | Delete an affiliate with no dependents | Partner also deleted; no orphan records |

---

## 17. Edge Cases & Regressions

| ID | Test | Steps | Expected |
|---|---|---|---|
| 17.1 | date=False display_name (contribution) | Create contribution via `New` (unsaved) | display_name doesn't crash |
| 17.2 | duplicate uid on write | Change an affiliate's uid to an existing one | SQL unique constraint fires |
| 17.3 | _check_uid on write | Change uid to `0...` or non-numeric | ValidationError |
| 17.4 | workplace without parent_path | Create workplace, verify level compute | level=1, no crash |
| 17.5 | position without registration_date | Create position, verify affiliate.position_registration_date_ids | Empty, no crash |
| 17.6 | affiliate without positions | has_featured_position / position_type_ids / registration_dates | Empty/False, no crash |
| 17.7 | config flags default OFF | All 3 create_user_from_* flags | Default False (visible in config form) |
| 17.8 | _compute_display_name date=False in result | Inconsistency result for affiliate | No crash |

---

## 18. Session Summary Template

Use this at the end to record overall results.

```
Module                 | Tests Run | PASS | FAIL | Notes
------------------------+-----------+------+------+----------------------------
union_affiliation      |           |      |      |
union_school_position  |           |      |      |
union_benefit_request  |           |      |      |
union_contribution     |           |      |      |
Cross-module           |           |      |      |
Import flows           |           |      |      |
Security               |           |      |      |
------------------------+-----------+------+------+----------------------------
TOTAL                  |           |      |      |
```

---

## Appendix A: Quick DB Verification Queries

Run from host: `docker compose exec db psql -U odoo -d sindicato -c "<SQL>"`

```sql
-- SQL constraints present
SELECT conname, contype FROM pg_constraint
WHERE conrelid = 'affiliation_affiliate'::regclass AND contype = 'u';

-- SQL functions from post_init_hook
SELECT proname FROM pg_proc WHERE proname IN
('mapState','translateState','calculateInconsistencies','calcInconsByType');

-- Demo data counts
SELECT 'affiliates' AS what, count(*) FROM affiliation_affiliate
UNION ALL SELECT 'positions', count(*) FROM school_position_position
UNION ALL SELECT 'contributions', count(*) FROM contribution_affiliate_contribution
UNION ALL SELECT 'benefit_requests', count(*) FROM benefit_request_benefit_request
UNION ALL SELECT 'workplaces', count(*) FROM union_workplace
UNION ALL SELECT 'children', count(*) FROM affiliation_affiliate_child;

-- Registration date dedup check
SELECT date, count(*) FROM school_position_registration_date GROUP BY date HAVING count(*) > 1;
```

## Appendix B: Re-running the Automated Suite

From the supermodule root:

```bash
docker compose exec web odoo \
  --addons-path=/mnt/custom-addons,/usr/lib/python3/dist-packages/odoo/addons \
  --db_host=db --db_user=odoo --db_password=odoo \
  -d sindicato --test-enable \
  --test-tags=/union_affiliation,/union_benefit_request,/union_contribution,/union_school_position \
  -u union_affiliation,union_benefit_request,union_contribution,union_school_position \
  --stop-after-init --http-port 8099 --log-level=info
```

Expect: `0 failed, 0 error(s)` (73 tests).
