# AUDIT — odoo-union 19.0 modules

> **Scope:** exhaustive audit of `union_affiliation`, `union_benefit_request`,
> `union_contribution`, `union_school_position` after the 16.0→19.0 migration
> (branch `19.0`, post push `b404e8c`).
> **Method:** static review of all models/views/security/wizards + runtime
> probes on the `sindicato` DB (Odoo 19.0-20260803).
> **Status codes:** 🔴 critical · 🟠 security · 🟡 correctness · 🔵 performance · ⚪ quality
> Every finding lists **file:line** and a concrete **Fix**.

---

## 0. Executive summary

| Severity | Count | Theme |
|---|---|---|
| 🔴 Critical | 5 | Runtime crashes on reachable paths (`notify_danger` missing API, hardcoded user id, IndexError in constraint, split() crash, singleton assumptions in constrains) |
| 🟠 Security | 6 | Group-less ACLs, sudo info-leak, ungated server actions, write-group DELETE, raw-SQL onchange (all ✅ FIXED) |
| 🟡 Correctness | 9 | Stale computed names, dead fallback code, double-delete risk, overlap-constraint gaps, unused wizard field, no-op override, orphan model |
| 🔵 Performance | 4 | N+1 stored computes, side-effectful compute, recursive descendant walk, FK indexes |
| ⚪ Quality | 8 | Duplication (mixin candidates), config-access inconsistencies, license mismatch, leftover scaffolding |

Automated suite status: **116/116 pass** (P0 + security fixes add 41 regression tests), pre-commit **18/18 green** — none of
the 🔴 items are covered by tests (each entry below names the test that would
have caught it).

---

## 1. 🔴 Critical bugs

### 1.1 `notify_danger()` does not exist ✅ FIXED in Odoo 19 → AttributeError on every failed import row
- **Where:** `union_school_position/models/position.py:219` y
  `union_contribution/models/contribution.py:45` (`on_import_error`).
- **Proof:** `grep -rn notify_danger /usr/lib/python3/dist-packages/odoo/` → NOT FOUND.
  Any CSV row error during import crashes the whole wizard with
  `AttributeError: 'res.users' object has no attribute 'notify_danger'`
  instead of reporting the bad row.
- **Why tests missed it:** no test drives `on_import_error`.
- **Fix:** delete the notification entirely — `base_import` already reports
  failing rows natively; optionally add `_logger.warning("Import error line %s: %s", line, error["message"])`. If a UI toast is desired, use the
  standard `raise UserError` per-row flow or mail thread message.
- **Regression test:** call `on_import_error(line, {"record": "0", "message": "x"})` — must not raise.

### 1.2 Hardcoded `responsible = 2` ✅ FIXED when creating benefit requests from surveys
- **Where:** `union_benefit_request/models/survey_user.py:40`.
- **Proof:** `base.user_admin` id = 2 *in this DB*, but ids are not portable
  (fresh DBs/demo data/migrations can differ); on any other DB this assigns
  an arbitrary/missing user → IntegrityError or wrong ownership.
- **Fix:** `"responsible": self.env.ref("base.user_admin").id` or better,
  `default=lambda s: s.env.user` semantics decided by product.
- **Test:** create survey input as non-admin user; assert request.responsible == expected ref.

### 1.3 `_check_uid` raises raw `IndexError` ✅ FIXED instead of ValidationError on empty uid
- **Where:** `union_affiliation/models/affiliate.py:_check_uid`
  (`if record.uid[0] == "0"` runs even when `record.uid` falsy).
- **Proof:** shell probe `aff.write({'uid': ''})` → `IndexError: string index out of range`.
  Reachable via RPC/write bypassing required-field UX, or imports.
- **Fix:** guard: `if record.uid and record.uid[0] == "0":` (and consider
  raising ValidationError when uid empty given field is required).
- **Test:** write empty uid → expect ValidationError, not IndexError.

### 1.4 `name_search` crash on malformed import lookup strings ✅ FIXED
- **Where:** `union_benefit_request/models/benefit_request.py:241`
  `_date, _type, _name = name.split(",")` → ValueError unless exactly ≥3 parts;
  also crashes with >3 parts (unpack).
- **Trigger:** importing requests where the M2O display string contains a
  comma in the partner name (legal reasons: “Garcia, Maria”).
- **Fix:** `parts = (name.split(",") + ["", "", ""])[:3]` or match the
  documented format defensively and fall back to normal domain.
- **Test:** `name_search("2026-01-01,Solicitud Simple,Garcia, Maria", context={"import_file": True})`.

### 1.5 Constrains written for singleton but run on recordsets ✅ FIXED
- **Where:**
  - `union_affiliation/models/affiliate_type.py:_check_name` (uses `self.name`, `self.id`)
  - `union_affiliation/models/affiliation_period.py:_check_dates/_check_affiliation_number/_check_from_date/_check_to_date` (same pattern)
- **Impact:** batch operations (imports! `create(vals_list)` of >1, list
  edits) raise `ExpectedSingleton`; also `_check_from_date`'s loop raises on
  the FIRST other record even when others are unrelated rows found by the
  inverted-span domain (see 2.4).
- **Fix:** wrap bodies in `for rec in self:` and exclude `rec` inside the loop;
  correct the overlap domains to the classic interval test:
  `("from_date", "<", rec.to_date), ("to_date", ">", rec.from_date)` with
  `("id", "!=", rec.id)` (handles both containment directions).
- **Test:** `create([{...},{...}])` two types at once; overlapping periods in
  both directions.

---

## 2. 🟠 Security

### 2.1 Global read/write ACLs on benefit requests (no group) ✅ FIXED
- **Where:** `union_benefit_request/security/ir.model.access.csv:3-4`
  (`write_benefit_request` & `read_benefit_request` with EMPTY `group_id`:
  `1,1,1,0` and `1,0,0,0`).
- **Impact:** ANY internal user can create/edit every request regardless of
  the module groups; combined with Odoo-19 warnings already logged at upgrade
  (“Rule … has no group, deprecated”). The `group_*` structure exists but is
  effectively decorative except for admin/unlink and menus/buttons.
- **Fix:** assign rows to `group_benefit_request_read` / `..._write`;
  decide whether creation should be write-group or a dedicated creator group.
  Coordinate with data migration if some users relied on open access.
- **Audit step after fix:** `\d` + login-as-minimal-user matrix from TESTING.md §15.

### 2.2 `sudo()` in workplace `name_search` leaks restricted data ✅ FIXED
- **Where:** `union_affiliation/models/workplace.py:125`
  `for workplace in workplaces.sudo()`.
- **Impact:** users without `group_affiliation_read` still resolve workplace
  display names via M2O dropdowns elsewhere (info disclosure, minor but
  unnecessary).
- **Fix:** drop `.sudo()`; if some caller needs it, scope the sudo to the
  specific internal flow with a context flag.

### 2.3 Sensitive server actions without group gating (Odoo 19 removed `groups_id`) ✅ FIXED
- **Where:** `action_set_quote_server` / `action_unset_quote_server`
  (`union_contribution/views/result_views.xml`) and featured actions
  (`position_views.xml`). Since `groups_id` was removed from
  `ir.actions.server` in 19 (migration fix 304d5e4), visibility now depends
  only on model ACLs.
- **Impact:** quote toggling mutates `affiliation.affiliate.quote` — effective
  gate becomes “has write on inconsistencies.result AND write on affiliate”,
  which is broader than the old `group_inconsistencies_write` intent.
- **Fix (pattern):** keep actions but guard in Python:
  ```python
  def action_set_quote(self):
      if not self.env.user.has_group("union_contribution.group_inconsistencies_write"):
          raise UserError(_("Not allowed"))
      ...
  ```
  Same pattern recommended for `action_set_featured/unset`.

### 2.4 Record rules deprecated form (no group) — cleanup debt ✅ FIXED
- Upgrade logs flagged “Rule Write/Read for benefit_request… no group”.
  After fixing 2.1, remove/replace those rules; empty-group rules are slated
  for removal upstream. ✅ Resolved by 2.1 (ACLs now scoped to groups; upgrade
  no longer emits the no-group warning) — verified 0 group-less ACL rows remain.

---

## 2b. 🟠 Security — additional findings (odoo-security skill)

> The `odoo-security` skill audit surfaced two further issues beyond §2.1–2.4.
> Both fixed and covered by `tests/test_security.py` in each module.

### 2.5 Write groups granted `perm_unlink` (DELETE) ✅ FIXED
- **Where:** every `*_write` row in the four modules'
  `security/ir.model.access.csv` (rows were `1,1,1,1`).
- **Impact:** "Overly permissive perms" — non-manager (`*_write`) groups
  could delete affiliates, positions, contributions, benefit requests, etc.
- **Fix:** set `perm_unlink=0` on all `*_write` rows (delete stays on
  `admin_*` rows only). Matches TESTING.md §15.2 ("Write group: …cannot
  delete for restricted models"). Verified 0 `write_*` rows retain unlink.
- **Regression test:** `test_affiliation_write_user_cannot_delete`,
  `test_write_user_cannot_delete_position`.

### 2.6 Raw SQL in `_onchange_request_type` bypassed ACLs ✅ FIXED
- **Where:** `union_benefit_request/models/benefit_request.py`
  (`SELECT partner_id FROM affiliation_affiliate` in the onchange).
- **Impact:** raw SQL returned every affiliate partner regardless of the
  user's access rules (information disclosure for write users lacking
  `group_affiliation_read`).
- **Fix:** replaced with
  `self.env["affiliation.affiliate"].search([]).partner_id.ids`
  so the domain respects ACLs.

---

## 3. 🟡 Correctness

### 3.1 Stored workplace-level labels go stale on rename
- **Where:** `position.py:82` depends
  `("workplace_id","workplace_id.level","workplace_id.parent_path")` —
  `workplace_id.name` missing; same in
  `affiliate.py:164` for `main_workplace_level*`.
- **Impact:** renaming “Escuela Tecnica” leaves old text frozen in all stored
  `workplace_levelX` / `main_workplace_levelX` until some other trigger
  recomputes. Group-bys then show ghost names.
- **Fix:** add `"workplace_id.name"` / `"main_workplace_id.name"` to the
  `@api.depends` (rename triggers recompute of dependents through the M2O).
- **Test:** rename workplace → assert stored fields updated.

### 3.2 Contribution-import fallbacks are dead code (uid validated first)
- **Where:** `contribution.py:_prepare_import_vals` — `isdigit()` check runs
  before the personal_id/vat/name lookups; a row without uid always raises.
- **Already documented** in `import_tests/README.md §5`.
- **Fix:** move validations into the branches that consume uid:
  ```python
  import_uid = vals.get("import_uid")
  if import_uid:
      if not str(import_uid).isdigit(): raise ...
      ...search...
  ```
  Then extend `contributions_existing.csv` with personal_id/vat/name-only rows.

### 3.3 `Affiliate.unlink()` manually deletes partner — double-delete risk
- **Where:** `affiliate.py:219-223` (TODO left from WIP).
- **Risk:** with `_inherits`, ORM already cascades; explicit
  `partner_id.unlink()` first can hit restrict rules twice or reorder events.
  Runtime probe pending — treat as suspect.
- **Fix:** try removing the explicit unlink; if some orphan-partner case
  motivated it, solve with `ondelete=cascade` audit instead.
- **Test:** delete affiliate with positions/contributions restrictions and a
  clean one; assert partner gone only once and no orphan partners remain
  (`SELECT count(*) FROM res_partner p LEFT JOIN affiliation_affiliate a ON a.partner_id=p.id WHERE a.id IS NULL AND p.id > X` style check in test).

### 3.4 `_get_current_period()` fragile ordering/None handling
- `affiliate.py`: sorts by `id` desc, indexes `[0]` conditionally, compares
  `not _period.closed` on possibly-empty recordset path returning `False` —
  callers like `action_disaffiliate` then do `.id` on False → traceback path
  if no open period exists.
- **Fix:** rewrite:
  ```python
  def _get_current_period(self):
      return self.affiliation_period_ids.filtered(lambda p: not p.closed).sorted("from_date", reverse=True)[:1]
  ```
  and guard callers for empty result with UserError.
- **Test:** disaffiliate an affiliate with zero periods → UserError, not crash.

### 3.5 `ChangeStateWizard.change_date` collected but never used
- `result.py`: field is required+readonly, displayed, ignored by
  `action_confirm`. Either apply as `to_date`/period date or drop from view.
- **Fix:** wire into period close/open dates or remove field+column.

### 3.6 `base_import.do` override is a no-op with misleading comment
- `contribution/models/base_import.py` claims “Clean logs” but only calls super.
- **Fix:** delete the override (and its file) or implement what the comment promises.

### 3.7 `school_position.tag` is an orphan model
- Defined + ACLs, zero views, zero relations, never imported anywhere else.
- **Fix:** remove model+ACLs, or wire a `tag_ids` m2m on position if planned.

### 3.8 `hide_*` writes in `BenefitRequest.write()` are silently discarded
- Probe: `req.write({'hide_notes': True})` → no effect (non-stored compute,
  no inverse). Lines writing `vals["hide_notes"] = ...` are dead weight and
  mislead readers.
- **Fix:** drop those three lines from `write()`; `_compute_hides` +
  onchange cover UI/state.
- Related smell (3.9): compute method `_onchange_request_type` doubles as
  onchange and RETURNS a domain dict — computes must return None. Split:
  pure `_compute_hides` for the fields + separate `@api.onchange` returning
  the partner domain.

### 3.9 Duplicate `open-period` enforcement layers
- `create()` checks `_are_any_open` while constraints also police overlaps —
  but `_are_any_open` ignores `from_date`, so closing yesterday and opening
  today passes, while creating two same-day periods errors via constraint
  with a different message. Unify: single source of truth (constraint) and
  keep `create()` check only for the friendlier business message, aligned
  semantics.

---

## 4. 🔵 Performance

### 4.1 N+1 searches inside stored computes
- `_compute_uid` / `_compute_personal_id` (`benefit_request.py`) run one
  affiliate `search` per request row, stored → fires on every partner change
  and during recompute sweeps.
- **Fix:** single search: map partner_ids → affiliates in one query
  (`read_group`/`search([('partner_id','in',...)])`), or make them
  non-stored related-through-partner helpers if filter usage allows
  (`related="partner_id.affiliate_id.uid"`? not directly — keep compute but
  batch).

### 4.2 Side-effectful compute creates real records
- `_compute_position_registration_dates` creates
  `school_position.registration.date` rows inside a stored compute (sudo).
  Computes may run speculatively (flush/order), polluting the table with
  dates from discarded drafts.
- **Fix options:** (a) move materialization to `write/create` of position
  registration_date changes; (b) keep compute pure (M2M of transient values
  isn't possible) → pragmatic: keep but dedupe-guard + document, or switch
  grouping to a plain `registration_date` group-by on positions via
  related field on affiliate using a non-stored helper view. Decide with
  product; minimum: add exists-check (already there) + periodic cleanup cron.

### 4.3 `_get_all_descendants` recursion = query per level
- Workplace tree walks children recursively; deep trees multiply queries and
  `parent_path` already enables set-based: `search([("parent_path","like", f"{self.parent_path}%")])`.
- Same for delete-wizard impact counting.
- **Fix:** replace recursion with parent_path prefix search.

### 4.4 Missing explicit indexes on hot FK/search columns
- Candidates: `school_position.position.affiliate_id/type_id/workplace_id`,
  `contribution.affiliate_id/contribution_code_id/date`,
  `affiliation_period.affiliate_id/from_date/to_date`,
  `benefit_request.partner_id/request_type_id/state`.
- **Fix:** `index=True` on the high-cardinality FKs used by group-bys/lists;
  measure with `EXPLAIN` before/after on sindicato-sized data.

### 4.5 Minor
- `seniority_years` recomputes per read (non-stored, date-dependent) — fine
  for forms; avoid using it in big list views or make stored+cron-refreshed
  if reports need it.

---

## 5. ⚪ Code quality & consistency

### 5.1 Mixin extraction for triplicated uid-validation + duplicated `on_import_error`
- Identical blocks in `position.create`, `benefit_request.create`,
  `contribution._prepare_import_vals`; near-identical `on_import_error` x2.
- **Proposal:** `union_base` (new micro-module) or a `models/mixins.py` in
  `union_affiliation` with:
  ```python
  class UnionImportMixin(models.AbstractModel):
      _name = "union.import.mixin"
      def _validate_union_uid(self, uid): ...   # digits/no-leading-zero -> ValidationError
      def _resolve_or_create_affiliate(self, vals, flag_field): ...
  ```
  Kills R0801 (currently disabled in pylint config) and guarantees the 3.2
  fix lands once, not thrice.

### 5.2 Config access style drift: `browse(1)` vs `search(limit=1)`
- 6× `browse(1)` (affiliate.py x5, wizard) vs `search([], limit=1)`
  (contribution). If the singleton ever gets res_id ≠ 1 (multi-company
  future), half the flows break silently.
- **Fix:** one helper on the model:
  ```python
  @api.model
  def _get_config(self):
      return self.search([], limit=1)
  ```

### 5.3 Two parallel change-tracking systems on Affiliate
- Manual `log` Text + `_log_change_field` coexists with mail.thread tracking.
  Benefit_request was already migrated to `tracking=True` (commit e43f463);
  finish the job: mark affiliate tracked fields `tracking=True`, keep `log`
  read-only historical, stop appending.
- **Also:** `_log_change_field` builds messages with `%` of possibly-False
  many2one display names — covered by its formatter but verify after switch.

### 5.4 Licensing inconsistency
- `union_affiliation` = AGPL-3; other three = GPL-3. Same author, same repo.
- **Fix:** align (AGPL-3 recommended for OCA-adjacent reuse) + add
  `LICENSE` file at repo root if missing.

### 5.5 Leftover scaffolding/comments
- `union_*/models/models.py` (commented stubs, loaded but empty),
  commented `_compute_closed` block in affiliation_period, commented
  controllers replaced earlier ✓ (keep stub docstrings).
- **Fix:** delete `models.py` files + their imports; drop dead comment block.

### 5.6 Menu ordering ties
- All three school_position submenus use sequence=10 → renderer-dependent
  order. Set 10/20/30.

### 5.7 `default_home_action.xml` forces home action for ALL users
- Global `ir.default` on `res.users.action_id` overrides personal prefs and
  affects non-sindicato users too (portal/backend mix in prod DBs).
- **Fix:** scope via `company_id`/group conditions or move to a
  `load_branding_message`-style opt-in; at minimum document behavior.

### 5.8 i18n hygiene
- Several user-facing literals bypass `_()` (e.g., some raise messages in
  contribution auto-create path are wrapped ✓, but view `string=` attributes
  rely on po which is fine). Post-regen sweep: `grep -rn 'ValidationError(_'`
  coverage is good; next target: default strings in demo data (es content in
  XML is fine as data).
- Keep `po-pretty-format` disabled decision documented (already in config).

---

## 6. Odoo-19 compliance spot-check (all green ✅)

- `models.Constraint` (not `_sql_constraints`) ✔ verified in DB
- `<list>` tags, no `attrs=`, search views without `<group>` ✔
- `@api.model_create_multi` on all custom creates ✔
- No `groups_id` on actions ✔ (guards moved to Python pending, see 2.3)
- `_compute_display_name` everywhere; `date=False` guarded ✔
- Translation files regenerated from 19.0 sources ✔ (Phase 4.1 closed)
- pre-commit adhoc stack green 18/18 ✔

---

## 7. Testing gaps (map directly to findings)

| Missing test | Would have caught |
|---|---|
| Import-error path (`on_import_error`) | 1.1 notify_danger crash |
| Survey→request flow as non-admin | 1.2 responsible=2 |
| Empty/edge uid writes | 1.3 IndexError |
| Comma-bearing partner names in import ctx | 1.4 split crash |
| Multi-record creates hitting constrains | 1.5 ExpectedSingleton family |
| Workplace rename propagation | 3.1 stale levels |
| Contribution import without uid (fallbacks) | 3.2 dead code |
| Delete affiliate w/ & w/o dependents + orphan check | 3.3 |
| Disaffiliate with no open period | 3.4 |
| Wizard end-to-end incl. change_date semantics | 3.5 |
| Minimal-user ACL matrix (login as read-only group) | 2.1/2.2/2.3 |
| Period overlap both directions | 1.5/3.9 |

Suggested harness additions: one `HttpCase` smoke (open affiliate form,
discuss thread loads — would have caught the earlier suggested-recipients
TypeError too) and `TransactionCase` batches above tagged
`post_install,'union'`.

---

## 8. Recommended execution order

1. **P0 (crash/security):** 1.1, 1.2, 2.1, 1.3 — small diffs, ship together
   with their regression tests.
2. **P1 (correctness):** 1.4, 1.5 (+3.9 alignment), 3.1, 3.2 (with mixin 5.1
   to do it once), 3.4.
3. **P2 (hardening/perf):** 3.3 probe-and-fix, 2.2, 2.3 guards, 4.1–4.4.
4. **P3 (quality):** 5.x cleanups, 3.5–3.8 decisions with product, docs
   (TESTING.md §15 matrix refresh after ACL change).

Estimate: P0 ≈ half-day incl. tests; P1 ≈ 1–2 days (mixin included);
P2/P3 incremental.
