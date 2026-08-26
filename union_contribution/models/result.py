from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AffiliationConfiguration(models.Model):
    _name = "inconsistencies.result"
    _description = "Result of inconsistencies query about Affiliate's state"

    from_date = fields.Date(string="From", readonly=True)
    to_date = fields.Date(string="To", readonly=True)
    query_date = fields.Date(string="Query date", readonly=True)
    description = fields.Char(string="Description", readonly=True)
    affiliate_id = fields.Many2one(
        comodel_name="affiliation.affiliate",
        string="Affiliate",
        required=True,
        ondelete="cascade",
    )
    status = fields.Char(string="Status", readonly=True)
    affiliate_state = fields.Selection(related="affiliate_id.state", string="Affiliate State", store=True)
    affiliate_type_id = fields.Many2one(related="affiliate_id.affiliate_type_id", string="Employment Type", store=True)
    quote = fields.Boolean(related="affiliate_id.quote", string="Cotizante", store=True)

    def action_set_quote(self):
        if not self.env.user.has_group("union_contribution.group_inconsistencies_write"):
            raise UserError(_("You don't have permission to change the contributor state from Inconsistencies."))
        affiliates_processed = set()
        for rec in self:
            if rec.affiliate_id.id in affiliates_processed:
                continue
            affiliates_processed.add(rec.affiliate_id.id)

            aff = rec.affiliate_id.sudo()
            if aff.state != "affiliated":
                raise ValidationError(
                    _(
                        "Solo se puede cambiar el estado cotizante si el/la"
                        ' afiliado/a %s se encuentra en estado "Afiliado/a".'
                    )
                    % aff.name
                )

            if not aff.quote:
                aff.write({"quote": True})
                aff.message_post(body=_("Estado cotizante cambiado a Cotizante desde Inconsistencias."))

    def action_unset_quote(self):
        if not self.env.user.has_group("union_contribution.group_inconsistencies_write"):
            raise UserError(_("You don't have permission to change the contributor state from Inconsistencies."))
        affiliates_processed = set()
        for rec in self:
            if rec.affiliate_id.id in affiliates_processed:
                continue
            affiliates_processed.add(rec.affiliate_id.id)

            aff = rec.affiliate_id.sudo()
            if aff.state != "affiliated":
                raise ValidationError(
                    _(
                        "Solo se puede cambiar el estado cotizante si el/la"
                        ' afiliado/a %s se encuentra en estado "Afiliado/a".'
                    )
                    % aff.name
                )

            if aff.quote:
                aff.write({"quote": False})
                aff.message_post(body=_("Estado cotizante cambiado a No Cotizante desde Inconsistencias."))

    def _compute_display_name(self):
        for record in self:
            record.display_name = _("Inconsistencia: %s") % (
                record.affiliate_id.name if record.affiliate_id else record.id
            )


class ChangeStateWizard(models.TransientModel):
    _name = "inconsistencies.change_state_wizard"
    _description = "Change Affiliate State Wizard"

    inconsistency_ids = fields.Many2many("inconsistencies.result", string="Inconsistencias", required=True)

    @api.model
    def _get_new_state_selection(self):
        schema = self.env["affiliation.affiliate"].fields_get(["state"])
        return schema.get("state", {}).get("selection", [])

    new_state = fields.Selection(selection="_get_new_state_selection", string="Nuevo Estado", required=True)
    change_date = fields.Date(
        string="Fecha Efectiva",
        default=fields.Date.context_today,
        required=True,
        readonly=True,
    )
    affiliate_type_id = fields.Many2one(
        comodel_name="affiliation.affiliate_type",
        string="Tipo de relación laboral",
        help="Seleccione el tipo de relación laboral. Requerido para cambiar a estados"
        ' distintos de "No afiliado/a" o "New" si el/la afiliado/a no tiene uno asignado.',
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ChangeStateWizard, self).default_get(fields_list)
        if self.env.context.get("active_model") == "inconsistencies.result" and self.env.context.get("active_ids"):
            res["inconsistency_ids"] = [(6, 0, self.env.context.get("active_ids"))]
        return res

    @api.constrains("new_state", "inconsistency_ids")
    def _check_new_state(self):
        for rec in self:
            for inc in rec.inconsistency_ids:
                if inc.affiliate_id.state == rec.new_state:
                    raise ValidationError(
                        _("El/La afiliado/a %s ya se encuentra en el estado seleccionado.") % inc.affiliate_id.name
                    )

    def action_confirm(self):
        self.ensure_one()

        new_state_selection = dict(self.fields_get(["new_state"])["new_state"]["selection"])
        new_state_str = new_state_selection.get(self.new_state, self.new_state)

        affiliate_state_selection = dict(self.env["affiliation.affiliate"].fields_get(["state"])["state"]["selection"])
        affiliates_processed = set()

        for inc in self.inconsistency_ids:
            affiliate = inc.affiliate_id
            if affiliate.id in affiliates_processed:
                continue
            affiliates_processed.add(affiliate.id)

            current_state_str = affiliate_state_selection.get(affiliate.state, affiliate.state)

            body = _("Cambio de estado desde Inconsistencias: de %s a %s.") % (
                current_state_str,
                new_state_str,
            )
            affiliate.message_post(body=body)

            if self.affiliate_type_id:
                affiliate.write({"affiliate_type_id": self.affiliate_type_id.id})

            self.env.invalidate_all()

            if self.new_state == "pending_suscribe":
                action = affiliate.affiliate_()
                if isinstance(action, dict) and action.get("res_model") == "affiliation.affiliation_number":
                    wiz = self.env[action["res_model"]].browse(action.get("res_id"))
                    wiz.with_context(**action.get("context", {})).confirm()
            elif self.new_state == "affiliated":
                action = affiliate.confirm_affiliation_()
                if isinstance(action, dict) and action.get("res_model") == "affiliation.affiliation_number":
                    wiz = self.env[action["res_model"]].browse(action.get("res_id"))
                    wiz.with_context(**action.get("context", {})).confirm()
            elif self.new_state == "pending_unsuscribe":
                affiliate.disaffiliate_()
            elif self.new_state == "disaffiliated":
                affiliate.confirm_dissafiliation_()
            elif self.new_state == "historical":
                affiliate.archive_()
            else:
                affiliate.write({"state": self.new_state})

        return {"type": "ir.actions.act_window_close"}
