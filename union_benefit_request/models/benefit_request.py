from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BenefitRequest(models.Model):
    _name = "benefit_request.benefit_request"
    _description = "Benefit request for partners"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    request_type_id = fields.Many2one(
        comodel_name="benefit_request.request_type",
        string="Type",
        required=True,
        ondelete="restrict",
        tracking=True,
    )

    # Not related to the affiliate table: some applicants are not affiliates.
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Applicant",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    # The next two fields only will be used to filters
    affiliate_uid = fields.Char(string="Affiliate UID", compute="_compute_uid", store=True)
    affiliate_personal_id = fields.Char(string="Personal ID", compute="_compute_personal_id", store=True)

    # Field for import process - maps to affiliate by UID
    import_uid = fields.Char(string="Legajo")
    import_name = fields.Char(string="Import Name")
    import_vat = fields.Char(string="Import VAT")
    import_personal_id = fields.Char(string="Import Personal ID")

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("authorized", "Authorized"),
            ("rejected", "Rejected"),
            ("finalized", "Finalized"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )
    request_date = fields.Date(string="Request date", required=True, default=fields.Date.today(), tracking=True)
    last_change_state = fields.Date(string="Last change of state")
    last_state = fields.Char(string="Last state")
    full_doc = fields.Boolean(string="Full documentation", default=False, tracking=True)
    expedient = fields.Char(string="Expedient/resolution", tracking=True)
    observations = fields.Text(string="Observations", tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    responsible = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    school_benefit_ids = fields.One2many(
        comodel_name="benefit_request.school_benefit",
        inverse_name="benefit_request_id",
        string="School benefits",
    )
    requested_amount = fields.Float(string="Requested amount", tracking=True)
    authorized_amount = fields.Float(string="Authorized amount", tracking=True)
    paid_amount = fields.Float(string="Paid amount", tracking=True)

    hide_school_benefits = fields.Boolean(compute="_onchange_request_type")
    hide_amounts = fields.Boolean(compute="_onchange_request_type")
    hide_notes = fields.Boolean(compute="_onchange_request_type")

    survey_user_input_id = fields.Many2one(comodel_name="survey.user_input")

    email = fields.Char(related="partner_id.email", store=False)

    @api.onchange("request_type_id")
    def _onchange_request_type(self):
        _groups = self.request_type_id.request_group_ids.mapped("name")
        self.hide_notes = False if "Notas" in _groups else True
        self.hide_amounts = False if "Importes" in _groups else True
        self.hide_school_benefits = False if "Bolsones" in _groups else True

        if self.request_type_id.who_apply == "affiliates":
            sql = "SELECT partner_id FROM affiliation_affiliate"
            self.env.cr.execute(sql)
            ids = list(map(lambda x: x["partner_id"], self.env.cr.dictfetchall()))
            return {"domain": {"partner_id": [("id", "in", ids)]}}
        return {"domain": {"partner_id": False}}

    @api.depends("request_type_id")
    def _compute_hides(self):
        _groups = self.request_type_id.request_group_ids.mapped("name")
        self.hide_notes = False if "Notas" in _groups else True
        self.hide_amounts = False if "Importes" in _groups else True
        self.hide_school_benefits = False if "Bolsones" in _groups else True

    def request(self):
        self._compute_hides()
        if not self.hide_amounts:
            if self.requested_amount <= 0:
                raise ValidationError(_("Requested amount must be major to zero"))  # traducir
        if not self.hide_school_benefits:
            if len(self.school_benefit_ids) < 1:
                raise ValidationError(_("There must be at least one school benefit"))  # traducir

        self.state = "requested"

        self.request_date = fields.Date.today()

    def authorize(self):
        self._compute_hides()
        if not self.hide_amounts:
            if self.authorized_amount <= 0:
                raise ValidationError(_("Authorized amount must be major to zero"))
        if not self.hide_school_benefits:
            if len(self.school_benefit_ids) < 1:
                raise ValidationError(_("There must be at least one school benefit"))
        if self.request_type_id.meet_reqs(self.partner_id):
            self.state = "authorized"

    def reject(self):
        self.state = "rejected"

    def finalize(self):
        self._compute_hides()
        if not self.hide_amounts:
            if self.paid_amount <= 0 or self.paid_amount > self.authorized_amount:
                raise ValidationError(_("The paid amount must be major to 0 and minor to authorized amount"))
        if self.request_type_id.require_full_doc and not self.full_doc:
            raise ValidationError(_("The documentation must be completed"))
        self.state = "finalized"

    def cancel(self):
        self.state = "canceled"

    def set_to_draft(self):
        # Check if user has admin permissions for finalized or canceled states
        if self.state in ["finalized", "canceled"]:
            if not self.env.user.has_group("union_benefit_request.group_benefit_request_admin"):
                raise ValidationError(
                    _("Only users with admin permissions can return finalized or canceled requests to draft state")
                )
        self.state = "draft"

    def write(self, vals):
        if "state" in vals:
            state_selection = dict(self._fields["state"]._description_selection(self.env))
            for record in self:
                vals.setdefault("last_state", state_selection.get(record.state, record.state))
                vals.setdefault("last_change_state", fields.Date.today())

        if "partner_id" in vals:
            self.message_unsubscribe([self.partner_id.id])
            self.message_subscribe([vals["partner_id"]])

        _groups = self.request_type_id.request_group_ids.mapped("name")
        if _groups:
            vals["hide_notes"] = False if "Notas" in _groups else True
            vals["hide_amounts"] = False if "Importes" in _groups else True
            vals["hide_school_benefits"] = False if "Bolsones" in _groups else True

        return super(BenefitRequest, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if "import_file" in self.env.context:
            for vals in vals_list:
                if "import_uid" in vals:
                    affiliate = self.env["affiliation.affiliate"].search([("uid", "=", vals["import_uid"])])
                    if len(affiliate.ids):
                        affiliate = affiliate[0]
                    else:
                        conf = self.env["affiliation.affiliation_configuration"].browse(1)
                        if conf.create_user_from_request:
                            new_uid = vals.get("import_uid")
                            import_name = vals.get("import_name")

                            if not new_uid or not import_name:
                                error_msg = _(
                                    "Cannot create affiliate for request import."
                                    " Missing import_name or ID (import_uid)."
                                    " Please ensure the imported data includes both"
                                    " affiliate Name and ID."
                                )
                                raise ValidationError(error_msg)
                            if not str(new_uid).isdigit():
                                raise ValidationError(_("El campo ID debe contener únicamente números."))
                            if str(new_uid)[0] == "0":
                                raise ValidationError(_("El campo ID no puede comenzar con cero."))

                            new_affiliate_data = {
                                "uid": new_uid,
                                "name": import_name,
                                "state": "new",
                            }
                            if "import_vat" in vals:
                                new_affiliate_data.update({"vat": vals["import_vat"]})
                            if "import_personal_id" in vals:
                                new_affiliate_data.update({"personal_id": vals["import_personal_id"]})

                            affiliate = self.env["affiliation.affiliate"].create(new_affiliate_data)
                        else:
                            error_msg = _(
                                "Affiliate does not exist in the database (UID: %s, Personal ID: %s), "
                                "and the option to auto-create them during import is disabled in the configuration."
                            ) % (
                                vals.get("import_uid", "N/A"),
                                vals.get("import_personal_id", "N/A"),
                            )
                            raise ValidationError(error_msg)

                    vals["partner_id"] = affiliate.partner_id.id
                    for key in ("import_name", "import_uid", "import_vat", "import_personal_id"):
                        vals.pop(key, None)

        for vals in vals_list:
            if "state" not in vals:
                vals.update({"state": "draft"})

        res = super(BenefitRequest, self).create(vals_list)
        for record in res:
            if record.partner_id:
                record.message_subscribe([record.partner_id.id])
        res._compute_hides()
        return res

    def _compute_display_name(self):
        for record in self:
            name = "%s - %s" % (record.request_type_id.name, record.partner_id.name)
            record.display_name = _("%s") % (name)

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = [("request_type_id", operator, name)]
        if "import_file" in self.env.context:
            _date, _type, _name = name.split(",")
            domain = [
                ("request_date", "=", _date),
                ("request_type_id", operator, _type),
            ]
            partner = self.env["res.partner"].search([("name", operator, _name)], limit=limit)
            if partner:
                domain = domain + [("partner_id", "=", partner[0].id)]
        else:
            partner = self.env["res.partner"].search([("name", operator, name)], limit=limit)
            if partner:
                domain = ["|", domain[0], ("partner_id", "=", partner[0].id)]

        recs = self.search(domain + args, limit=limit)
        return [(r.id, r.display_name) for r in recs]

    @api.depends("partner_id")
    def _compute_uid(self):
        for record in self:
            if record.partner_id.id:
                affiliate = record.env["affiliation.affiliate"].search([("partner_id", "=", record.partner_id.id)])
                if len(affiliate.ids):
                    record.affiliate_uid = affiliate[0].uid

    @api.depends("partner_id")
    def _compute_personal_id(self):
        for record in self:
            if record.partner_id.id:
                affiliate = record.env["affiliation.affiliate"].search([("partner_id", "=", record.partner_id.id)])
                if len(affiliate.ids):
                    record.affiliate_personal_id = affiliate[0].personal_id

    def _message_get_suggested_recipients(
        self,
        reply_discussion=False,
        reply_message=None,
        no_create=True,
        primary_email=False,
        additional_partners=None,
    ):
        self.ensure_one()
        recipients = super()._message_get_suggested_recipients(
            reply_discussion=reply_discussion,
            reply_message=reply_message,
            no_create=no_create,
            primary_email=primary_email,
            additional_partners=additional_partners,
        )

        if not self.partner_id:
            return recipients

        already_present = any(r.get("partner_id") == self.partner_id.id for r in recipients)

        if not already_present:
            recipients.append(
                {
                    "partner_id": self.partner_id.id,
                    "name": self.partner_id.name,
                    "email": self.partner_id.email_normalized,
                    "create_values": {},
                }
            )

        return recipients
