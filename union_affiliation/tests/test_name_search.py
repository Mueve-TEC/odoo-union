from lxml import etree
from odoo.tests import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


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

    def test_affiliate_name_search_superscript_digit_does_not_crash(self):
        """Superscripts pass isdigit() but int() rejects them with ValueError."""
        result = self.Affiliate.name_search("\u00b2")
        self.assertIsInstance(result, list)

    def test_affiliate_name_search_domain_excludes_record(self):
        result = self.Affiliate.name_search("Domain Search Affiliate", domain=[("id", "!=", self.affiliate.id)])
        self.assertNotIn(self.affiliate.id, [record[0] for record in result])

    def test_affiliate_child_name_search_accepts_domain(self):
        result = self.Child.name_search("DSC-456", domain=[("id", "=", self.child.id)])
        self.assertEqual([record[0] for record in result], [self.child.id])

    # ─── search view fields and filter domains ────────────────────────────────

    def _search_view(self, xmlid):
        return self.env.ref(xmlid)

    def test_search_view_filter_domains_accept_text_and_numbers(self):
        """Every filter_domain must survive a text and a numeric term."""
        for xmlid in (
            "union_affiliation.union_affiliation_affiliate_search",
            "union_affiliation.union_affiliation_affiliate_child_search",
        ):
            view = self._search_view(xmlid)
            model = self.env[view.model].sudo()
            for node in etree.fromstring(view.arch).xpath("//field[@filter_domain]"):
                expr = node.get("filter_domain")
                for term in ("CARLEVARO", "1234"):
                    domain = safe_eval(
                        expr,
                        {"self": term, "raw_value": term, "context": {}, "uid": self.env.uid},
                    )
                    model.search(domain, limit=1)

    def test_affiliate_search_view_uses_uid_search_field(self):
        """The integer uid field is not used directly in the search view."""
        root = etree.fromstring(self._search_view("union_affiliation.union_affiliation_affiliate_search").arch)
        names = root.xpath("//field/@name")
        self.assertIn("uid_search", names)
        self.assertNotIn("uid", names)

    def test_uid_search_with_free_text(self):
        """Free text must not be cast to int and must not match."""
        result = self.Affiliate.sudo().search([("uid_search", "ilike", "CARLEVARO")])
        self.assertNotIn(self.affiliate.id, result.ids)

    def test_uid_search_with_uid(self):
        result = self.Affiliate.sudo().search([("uid_search", "ilike", "90909090")])
        self.assertIn(self.affiliate.id, result.ids)

    def test_uid_search_with_cuit_sized_uid(self):
        """CUIT-sized uids cannot be typed in an integer search field (int4)."""
        cuit_affiliate = self.Affiliate.sudo().create(
            {"uid": 27203742296, "name": "CUIT Search Affiliate", "state": "new"}
        )
        result = self.Affiliate.sudo().search([("uid_search", "ilike", "27203742296")])
        self.assertIn(cuit_affiliate.id, result.ids)

    def test_uid_search_equality_and_membership_operators(self):
        equality = self.Affiliate.sudo().search([("uid_search", "=", "90909090")])
        self.assertIn(self.affiliate.id, equality.ids)
        self.assertFalse(self.Affiliate.sudo().search([("uid_search", "=", "CARLEVARO")]))
        excluded = self.Affiliate.sudo().search([("uid_search", "not in", ["CARLEVARO", "90909090"])])
        self.assertNotIn(self.affiliate.id, excluded.ids)

    def test_plain_relational_search_field_accepts_text(self):
        """A m2o search field without filter_domain also receives free text."""
        self.Affiliate.sudo().search([("main_workplace_id", "ilike", "CARLEVARO")], limit=1)
