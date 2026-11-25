from datetime import date

from lxml import etree
from odoo.tests import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestNameSearchDomain(TransactionCase):
    """Regression: Odoo 19 name_search uses ``domain`` instead of ``args``."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RequestType = cls.env["benefit_request.request_type"]
        cls.BenefitRequest = cls.env["benefit_request.benefit_request"]
        cls.SchoolBenefitType = cls.env["benefit_request.school_benefit_type"]
        cls.partner = cls.env["res.partner"].create({"name": "Domain Search Partner"})
        cls.request_type = cls.RequestType.create({"name": "Domain Request Type", "who_apply": "everybody"})
        cls.request_a = cls.BenefitRequest.sudo().create(
            {
                "partner_id": cls.partner.id,
                "request_type_id": cls.request_type.id,
                "request_date": date(2026, 1, 1),
            }
        )
        cls.request_b = cls.BenefitRequest.sudo().create(
            {
                "partner_id": cls.partner.id,
                "request_type_id": cls.request_type.id,
                "request_date": date(2026, 2, 2),
            }
        )
        cls.school_type_a = cls.SchoolBenefitType.sudo().create({"name": "Domain School Alpha"})
        cls.school_type_b = cls.SchoolBenefitType.sudo().create({"name": "Domain School Beta"})

    def test_benefit_request_name_search_by_type_with_domain(self):
        result = self.BenefitRequest.name_search("Domain Request Type", domain=[("id", "=", self.request_a.id)])
        self.assertEqual([record[0] for record in result], [self.request_a.id])

    def test_benefit_request_name_search_by_partner_with_domain(self):
        result = self.BenefitRequest.name_search("Domain Search Partner", domain=[("id", "=", self.request_b.id)])
        self.assertEqual([record[0] for record in result], [self.request_b.id])

    def test_benefit_request_import_name_search_accepts_domain(self):
        probe = f"2026-01-01,{self.request_type.name},{self.partner.name}"
        result = self.BenefitRequest.with_context(import_file=True).name_search(
            probe, domain=[("id", "=", self.request_a.id)]
        )
        self.assertEqual([record[0] for record in result], [self.request_a.id])

    def test_school_benefit_type_name_search_accepts_domain(self):
        result = self.SchoolBenefitType.name_search("Domain School", domain=[("id", "=", self.school_type_b.id)])
        self.assertEqual([record[0] for record in result], [self.school_type_b.id])

    # ─── search view fields and filter domains ────────────────────────────────

    def _filter_domain(self, view_xmlid, field_name, term):
        view = self.env.ref(view_xmlid)
        node = etree.fromstring(view.arch).xpath(f"//field[@name='{field_name}']")[0]
        return safe_eval(
            node.get("filter_domain"),
            {"self": term, "raw_value": term, "context": {}, "uid": self.env.uid},
        )

    def test_search_view_filter_domains_accept_text_and_numbers(self):
        """Every filter_domain must survive a text and a numeric term."""
        for xmlid in (
            "union_benefit_request.union_benefit_request_search",
            "union_benefit_request.school_benefit_search",
        ):
            view = self.env.ref(xmlid)
            model = self.env[view.model].sudo()
            for node in etree.fromstring(view.arch).xpath("//field[@filter_domain]"):
                expr = node.get("filter_domain")
                for term in ("CARLEVARO", "1234"):
                    domain = safe_eval(
                        expr,
                        {"self": term, "raw_value": term, "context": {}, "uid": self.env.uid},
                    )
                    model.search(domain, limit=1)

    def test_search_filter_domains_match_partner_and_type(self):
        for field_name, term in (
            ("partner_id", self.partner.name),
            ("request_type_id", self.request_type.name),
        ):
            domain = self._filter_domain("union_benefit_request.union_benefit_request_search", field_name, term)
            self.assertIn(self.request_a, self.BenefitRequest.sudo().search(domain))
