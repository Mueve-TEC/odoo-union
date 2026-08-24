from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AffiliationPeriod(models.Model):
    _name = "affiliation.affiliation_period"
    _description = "Affiliation period entity"
    _order = "from_date desc"

    affiliation_number = fields.Integer(string="Affiliation number", required=True)
    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To")
    closed = fields.Boolean(string="Closed", default=False)
    affiliate_id = fields.Many2one(
        comodel_name="affiliation.affiliate",
        string="Affiliate",
        required=True,
        ondelete="cascade",
    )
    affiliate_state = fields.Selection(related="affiliate_id.state", store=False)

    @api.constrains("from_date", "to_date")
    def _check_dates(self):
        for rec in self:
            if rec.from_date and rec.to_date and rec.from_date >= rec.to_date:
                raise ValidationError(_("'From date' is major to 'to date'!"))

    @api.constrains("affiliation_number")
    def _check_affiliation_number(self):
        for rec in self:
            others = self.env["affiliation.affiliation_period"].search(
                [("affiliation_number", "=", rec.affiliation_number), ("id", "!=", rec.id)],
                limit=1,
            )
            if others:
                raise ValidationError(_("There is already exist a period with the same affiliation number!"))

    @api.constrains("from_date", "to_date")
    def _check_overlap(self):
        """Interval overlap against any other period of the same affiliate.

        Two ranges [a1,a2] and [b1,b2] (b2 may be NULL = open-ended) overlap
        iff a1 < b2 (or b2 NULL) and b1 < a2 (or a2 NULL). Checking from both
        directions via the constraint on each record covers containment gaps
        that the previous endpoint-only checks missed.
        """
        for rec in self:
            if not rec.from_date:
                continue
            domain = [
                ("affiliate_id", "=", rec.affiliate_id.id),
                ("id", "!=", rec.id),
                "|",
                ("to_date", "=", False),
                ("to_date", ">", rec.from_date),
            ]
            others = self.search(domain)
            if rec.to_date:
                others = others.filtered(lambda o, _to=rec.to_date: o.from_date < _to)
            if others:
                raise ValidationError(_("The period overlaps another period of this affiliate!"))

    # @api.depends('to_date')
    # def _compute_closed(self):
    #     for record in self:
    #         if record.to_date:
    #             record.closed = True
    #             return
    #         record.closed = False

    def _are_any_open(self, affiliate_id):
        period = self.env["affiliation.affiliation_period"].search(
            [("affiliate_id", "=", affiliate_id), ("closed", "=", False)]
        )
        if len(period.ids):
            return True
        return False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _affiliate_id = vals.get("affiliate_id") or self.env.context.get("default_affiliate_id")
            if _affiliate_id and self._are_any_open(_affiliate_id):
                raise ValidationError(_("There is already an open period!"))

        res = super(AffiliationPeriod, self).create(vals_list)
        # affiliate = res.affiliate_id
        # affiliate.affiliate_()
        return res

    def write(self, vals):
        if self.closed:
            raise ValidationError(_("You can't edit a closed period!"))
        res = super(AffiliationPeriod, self).write(vals)
        return res

    def close(self, date):
        self.write({"to_date": date, "closed": True})
