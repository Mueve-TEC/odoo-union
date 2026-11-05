from datetime import date

from odoo.tests import TransactionCase, tagged


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
