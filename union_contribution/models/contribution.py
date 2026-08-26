import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AffiliateContribution(models.Model):
    _name = "contribution.affiliate_contribution"
    _description = "Union affiliates contribution entity"

    affiliate_id = fields.Many2one(
        comodel_name="affiliation.affiliate",
        string="Affiliate",
        required=True,
        ondelete="restrict",
    )
    date = fields.Date(string="Date", required=True)
    contrib_amount = fields.Float("Amount", required=True)
    contribution_code_id = fields.Many2one(
        comodel_name="contribution.affiliate_contribution_code",
        string="Code",
        required=True,
        ondelete="restrict",
    )
    # The next fields are to manage the importation process
    # All need be stored, because are necessary for the import process
    import_name = fields.Char(string="Import name")
    import_uid = fields.Char(string="Import uid")
    import_vat = fields.Char(string="Import vat")
    import_personal_id = fields.Char(string="Import personal ID")

    uid = fields.Integer(related="affiliate_id.uid", store=False)
    personal_id = fields.Char(related="affiliate_id.personal_id", store=False)

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("import_file"):
            vals_list = [self._prepare_import_vals(vals) for vals in vals_list]
        res = super(AffiliateContribution, self).create(vals_list)
        return res

    def write(self, vals):
        res = super(AffiliateContribution, self).write(vals)
        return res

    def on_import_error(self, _line, _error):
        _logger.warning("Import row error: %s | %s", _error.get("record"), _error.get("message"))

    def _compute_display_name(self):
        for record in self:
            date_str = record.date.strftime("%Y-%m-%d") if record.date else ""
            name = "%s,%s" % (record.affiliate_id.name or "", date_str)
            record.display_name = _("%s") % (name)

    def _clean_data_affiliate(self, vals):
        for key in ("import_name", "import_uid", "import_vat", "import_personal_id"):
            vals.pop(key, None)

    def _prepare_import_vals(self, vals):
        """Resolve or create affiliate during contribution import.

        Expected import keys are: import_uid, import_name, import_vat, import_personal_id.
        """
        import_uid = vals.get("import_uid")
        try:
            uid_int = int(import_uid)
        except (TypeError, ValueError):
            raise ValidationError(_("El campo ID debe contener un número entero válido."))
        if uid_int <= 0:
            raise ValidationError(_("El campo ID debe ser un número positivo."))

        import_name = vals.get("import_name")
        import_vat = vals.get("import_vat")
        import_personal_id = vals.get("import_personal_id")

        # If affiliate is already resolved by import mapping, just clear helper fields.
        if vals.get("affiliate_id"):
            self._clean_data_affiliate(vals)
            return vals

        affiliate_model = self.env["affiliation.affiliate"]
        affiliate = affiliate_model.browse()

        if import_uid:
            affiliate = affiliate_model.search([("uid", "=", uid_int)], limit=1)

        if not affiliate and import_personal_id:
            affiliate = affiliate_model.search([("personal_id", "=", import_personal_id)], limit=1)

        if not affiliate and import_vat:
            affiliate = affiliate_model.search([("vat", "=", import_vat)], limit=1)

        if not affiliate and import_name:
            affiliate = affiliate_model.search([("name", "=", import_name)], limit=1)

        if not affiliate:
            conf = self.env["affiliation.affiliation_configuration"].search([], limit=1)
            can_create = bool(conf and conf.create_user_from_contribution)
            if not can_create:
                raise ValidationError(
                    _(
                        "Affiliate not found for contribution import. "
                        "Enable 'Create user on contribution import' in affiliation configuration "
                        "or import with an existing affiliate."
                    )
                )

            if not import_uid:
                raise ValidationError(
                    _("Missing import_uid. It is required to create affiliates from contributions import.")
                )

            affiliate_vals = {
                "uid": uid_int,
                "state": "new",
                "name": import_name or str(uid_int),
            }
            if import_vat:
                affiliate_vals["vat"] = import_vat
            if import_personal_id:
                affiliate_vals["personal_id"] = import_personal_id

            affiliate = affiliate_model.create(affiliate_vals)

        vals["affiliate_id"] = affiliate.id
        self._clean_data_affiliate(vals)
        return vals
