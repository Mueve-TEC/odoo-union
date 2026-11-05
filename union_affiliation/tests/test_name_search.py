from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNameSearchDomain(TransactionCase):
    """Regression: Odoo 19 name_search uses ``domain`` instead of ``args``.

    The web client sends ``domain=`` when filtering a relational field. An
    override still declaring ``args`` raised
    ``TypeError: unexpected keyword argument 'domain'``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Workplace = cls.env["union.workplace"]
        cls.Affiliate = cls.env["affiliation.affiliate"]
        cls.Child = cls.env["affiliation.affiliate_child"]
        cls.workplace_a = cls.Workplace.sudo().create({"name": "Domain WP Alpha", "code": "DWPA"})
        cls.workplace_b = cls.Workplace.sudo().create({"name": "Domain WP Beta", "code": "DWPB"})
        cls.affiliate = cls.Affiliate.sudo().create(
            {
                "uid": 90909090,
                "name": "Domain Search Affiliate",
                "personal_id": "DS-123",
                "state": "new",
            }
        )
        cls.child = cls.Child.sudo().create({"name": "Domain Search Child", "personal_id": "DSC-456"})

    def test_workplace_name_search_accepts_domain(self):
        result = self.Workplace.name_search("Domain WP", domain=[("id", "=", self.workplace_a.id)])
        self.assertEqual([record[0] for record in result], [self.workplace_a.id])

    def test_workplace_name_search_by_code_with_domain(self):
        result = self.Workplace.name_search("DWPB", operator="=", domain=[("id", "!=", self.workplace_a.id)])
        self.assertEqual([record[0] for record in result], [self.workplace_b.id])

    def test_affiliate_name_search_by_uid_with_domain(self):
        result = self.Affiliate.name_search("90909090", domain=[("id", "=", self.affiliate.id)])
        self.assertEqual([record[0] for record in result], [self.affiliate.id])

    def test_affiliate_name_search_by_personal_id_with_domain(self):
        result = self.Affiliate.name_search("DS-123", domain=[("id", "=", self.affiliate.id)])
        self.assertEqual([record[0] for record in result], [self.affiliate.id])

    def test_affiliate_name_search_domain_excludes_record(self):
        result = self.Affiliate.name_search("Domain Search Affiliate", domain=[("id", "!=", self.affiliate.id)])
        self.assertNotIn(self.affiliate.id, [record[0] for record in result])

    def test_affiliate_child_name_search_accepts_domain(self):
        result = self.Child.name_search("DSC-456", domain=[("id", "=", self.child.id)])
        self.assertEqual([record[0] for record in result], [self.child.id])
