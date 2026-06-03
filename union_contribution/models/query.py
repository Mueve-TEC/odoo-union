# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Query(models.Model):
    _name = "inconsistencies.query"
    _description = "Query of inconsistency of Affiliate's state"

    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)
    query_date = fields.Date(
        string="Query date", readonly=True, required=True, default=fields.Date.today()
    )
    description = fields.Char(string="Description", required=True)
    contribute = fields.Boolean(
        string="Contribute",
        help="Include people who contributed and should not have contributed",
        required=True,
    )
    not_contribute = fields.Boolean(
        string="Doesn't contribute",
        help="Include people who didn't contribute and should have contributed",
        required=True,
    )
    affiliate_type_ids = fields.Many2many(
        comodel_name="affiliation.affiliate_type", string="Tipos de relación laboral"
    )
    contribution_code_ids = fields.Many2many(
        comodel_name="contribution.affiliate_contribution_code",
        relation="inc_query_contrib_code_rel",
        column1="query_id",
        column2="code_id",
        string="Códigos de aportes",
    )

    @api.depends("from_date", "to_date")
    def query_inconsistencies(self):
        if self.from_date >= self.to_date:
            raise ValidationError(_("To date should be major to from date"))

        result = False

        type_filter = ""
        type_params = []
        if self.affiliate_type_ids:
            type_filter = " AND a.affiliate_type_id IN %s"
            type_params.append(tuple(self.affiliate_type_ids.ids))

        code_filter = ""
        code_params = []
        if self.contribution_code_ids:
            code_filter = " AND c.contribution_code_id IN %s"
            code_params.append(tuple(self.contribution_code_ids.ids))

        base_params = [self.from_date, self.to_date, self.description] + type_params

        if self.not_contribute:
            # Cotizante sin aportes
            status_str = "Cotizante sin aportes"
            sql1 = f"""
                INSERT INTO inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description)
                SELECT a.id, %s, %s, %s, now(), %s
                FROM affiliation_affiliate a
                WHERE a.quote = TRUE {type_filter}
                  AND a.id NOT IN (
                      SELECT DISTINCT(c.affiliate_id)
                      FROM contribution_affiliate_contribution c
                      WHERE c.date BETWEEN %s AND %s {code_filter}
                  )
            """
            self.env.cr.execute(
                sql1,
                [status_str]
                + base_params
                + [self.from_date, self.to_date]
                + code_params,
            )
            if self.env.cr.rowcount > 0:
                result = True

        if self.contribute:
            # No cotizante con aportes
            status_str = "No cotizante con aportes"
            sql2 = f"""
                INSERT INTO inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description)
                SELECT a.id, %s, %s, %s, now(), %s
                FROM affiliation_affiliate a
                WHERE a.quote = FALSE {type_filter}
                  AND a.id IN (
                      SELECT DISTINCT(c.affiliate_id)
                      FROM contribution_affiliate_contribution c
                      WHERE c.date BETWEEN %s AND %s {code_filter}
                  )
            """
            self.env.cr.execute(
                sql2,
                [status_str]
                + base_params
                + [self.from_date, self.to_date]
                + code_params,
            )
            if self.env.cr.rowcount > 0:
                result = True

        # Inconsistencies of state vs quote
        sql3 = f"""
            INSERT INTO inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description)
            SELECT a.id, 'Cotizante - ' || COALESCE(translateState(a.state), a.state), %s, %s, now(), %s
            FROM affiliation_affiliate a  
            WHERE a.quote = TRUE AND a.state != 'affiliated' {type_filter}
        """
        self.env.cr.execute(sql3, base_params)
        if self.env.cr.rowcount > 0:
            result = True

        sql4 = f"""
            INSERT INTO inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description)
            SELECT a.id, 'No Cotizante - Afiliado', %s, %s, now(), %s
            FROM affiliation_affiliate a  
            WHERE a.quote = FALSE AND a.state = 'affiliated' {type_filter}
        """
        self.env.cr.execute(sql4, base_params)
        if self.env.cr.rowcount > 0:
            result = True

        if not result:
            raise ValidationError(_("There aren't inconsistencies between that dates"))

        # Populate stored related fields bypassing the ORM cache sync gap
        self.env.cr.execute(
            """
            UPDATE inconsistencies_result ir
            SET affiliate_type_id = a.affiliate_type_id,
                affiliate_state = a.state
            FROM affiliation_affiliate a
            WHERE ir.affiliate_id = a.id
            AND ir.description = %s
        """,
            (self.description,),
        )

        return {
            "type": "ir.actions.act_window",
            "name": "Gestión de cambios",
            "res_model": "inconsistencies.result",
            "views": [[False, "tree"]],
            "domain": [["description", "=", self.description]],
        }
