# Notes on the 16.0 → 19.0 migration (odoo-union)

> Compact hand-over distilled from the exhaustive `migration.md` that lived in
> the supermodule `soltec-localdev-odoo19` and was deleted in its `19.0`
> cleanup — full original: `git show ffe54b7:migration.md` there. Verified
> against this tree **2026-09-22**.

## Status: content port DONE

The hybrid port (18.0 cherry-picks + 16.0 gap-fills; plan Phases 0–5) was
executed on branch `19.0-upgrade` and merged to `19.0` via PR #45 (`e916a48`,
currently `origin/19.0` tip):

- `name_get` → `_compute_display_name` everywhere (0 `name_get` left)
- `@api.model_create_multi` on `benefit_request` / `position` creates
- `affiliation_configuration.py` + views in all three consumer modules —
  the config files the 18.0 WIP forgot
  (`create_user_from_{request,position,contribution}`)
- 16.0-only features present: `work_id` / `delegation_id` / `seniority_years`,
  `sector`, `featured` / `has_featured_position`, `workplace_level1/2/3`,
  `position_registration_date`, inconsistencies `affiliate_type_ids` /
  `contribution_code_ids` / `quote` / `ChangeStateWizard`, SQL constraints as
  Odoo-19 `models.Constraint`
- i18n `es_AR.po` **regenerated** from 19.0 sources (never merge PO files by
  hand)
- versions bumped for the feature ports (`union_affiliation` `19.0.1.2.0`,
  with `migrations/19.0.1.2.0/pre-migrate.py` guarding the uid Char→int
  column change; the other three at `19.0.1.1.0`), `pyproject.toml` present,
  dead `demo/demo.xml` gone

## If you ever port more from `16.0` / `18.0`

`origin/16.0` still has **54 commits by SHA not in `19.0`** — most were
ported *by content* (re-applied, cherry-picked, or rewritten), so:

- **Diff by content, not SHA.** `git log origin/19.0..origin/16.0` is
  misleading; grep the 19.0 tree for the feature first.
- **Do NOT port** (explicit rejections from the analysis):

  | Commit      | Why                                                                                                            |
  | ----------- | -------------------------------------------------------------------------------------------------------------- |
  | `f3e2d0a` (18.0) | rolls `user_ids` back to `users` — 19.0 correctly uses `user_ids` (`511804e`); porting regresses the Odoo 17+ API |
  | `656ac09` (18.0) | version bump to 18.x — pointless on 19.0                                                                         |
  | `1a0b96f` (18.0) | `_message_get_suggested_recipients` for affiliate — already present via `62aa134`                                |

- API reminders when touching 16.0-era code: `<tree>` → `<list>`,
  `attrs=` → inline `invisible`, `@api.model create(vals)` →
  `model_create_multi(vals_list)`, `post_init_hook(cr, registry)` → `(env)`,
  `res.groups.users` → `user_ids`.
- The 18.0 WIP `d1392b8` is **broken standalone** (references config fields
  whose model files it never added) — use it only as a reference, and port it
  together with the `affiliation_configuration.py` files.

## Validation checklist (run after any cross-branch port)

1. Fresh DB: install all 4 modules; `post_init_hook` (SQL functions) runs.
2. Import flows: cargos, solicitudes, aportes — exercise
   create-affiliate-from-import + config flags (fixtures:
   `import_tests/*.csv`).
3. Inconsistencias query + `ChangeStateWizard` + set/unset quote server
   actions.
4. Chatter / `_message_get_suggested_recipients` on affiliate **and**
   benefit_request.
5. `ruff check && ruff format` clean (`pyproject.toml`).
