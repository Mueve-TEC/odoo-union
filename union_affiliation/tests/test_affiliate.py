from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged
from psycopg2.errors import UniqueViolation


@tagged("post_install", "-at_install")
class TestAffiliate(TransactionCase):
    """Tests for affiliation.affiliate: SQL constraints, uid validation,
    seniority_years, _name_search, and _compute_name on configuration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Affiliate = cls.env["affiliation.affiliate"]
        cls.affiliate_type = cls.env["affiliation.affiliate_type"].create({"name": "Test Type", "enabled": True})

    def _create_affiliate(self, uid="12345678", name="Test Affiliate", **kw):
        vals = {"uid": uid, "name": name, "state": "new"}
        vals.update(kw)
        return self.Affiliate.sudo().create(vals)

    # ─── SQL CONSTRAINT: uid_unique ──────────────────────────────────────────

    def test_uid_unique_constraint(self):
        """models.Constraint uid_unique prevents duplicate uid."""
        self._create_affiliate(uid="11111111")
        with self.assertRaises(UniqueViolation):
            with self.env.cr.savepoint():
                self._create_affiliate(uid="11111111", name="Other")

    def test_affiliation_number_unique_constraint(self):
        """models.Constraint unique_affiliation_number prevents duplicates."""
        aff1 = self._create_affiliate(uid="22222222")
        aff1.write({"affiliation_number": 1001})
        aff2 = self._create_affiliate(uid="33333333")
        with self.assertRaises(UniqueViolation):
            with self.env.cr.savepoint():
                aff2.write({"affiliation_number": 1001})

    # ─── _check_uid Python constraint ─────────────────────────────────────────

    def test_uid_must_be_digits(self):
        """uid containing non-digit characters raises ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_affiliate(uid="12A45678")

    def test_uid_cannot_start_with_zero(self):
        """uid starting with '0' raises ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_affiliate(uid="01234567")

    def test_uid_valid_all_digits(self):
        """uid with all digits and non-zero start is accepted."""
        aff = self._create_affiliate(uid="98765432")
        self.assertEqual(aff.uid, "98765432")

    # ─── _check_affiliate_type_id constraint ──────────────────────────────────

    def test_affiliate_type_required_for_non_new_states(self):
        """affiliate_type_id is required when state is not 'new' or 'not_affiliated'."""
        with self.assertRaises(ValidationError):
            self._create_affiliate(uid="44444444", state="affiliated")

    def test_affiliate_type_not_required_for_new(self):
        """state 'new' does not require affiliate_type_id."""
        aff = self._create_affiliate(uid="55555555", state="new")
        self.assertEqual(aff.state, "new")

    # ─── seniority_years compute ──────────────────────────────────────────────

    def test_seniority_years_computed(self):
        """seniority_years computes years from seniority date to today."""
        from datetime import date

        aff = self._create_affiliate(uid="66666666")
        aff.write({"seniority": date(2020, 1, 1)})
        self.assertGreaterEqual(aff.seniority_years, 4)

    def test_seniority_years_zero_when_no_seniority(self):
        """seniority_years is 0 when seniority date is not set."""
        aff = self._create_affiliate(uid="77777777")
        self.assertEqual(aff.seniority_years, 0)

    # ─── _name_search override ────────────────────────────────────────────────

    def test_name_search_by_uid(self):
        """_name_search finds affiliates by uid."""
        self._create_affiliate(uid="88888888", name="John Doe")
        results = self.Affiliate.sudo()._name_search("88888888")
        self.assertTrue(results, "Should find affiliate by uid")

    def test_name_search_by_personal_id(self):
        """_name_search finds affiliates by personal_id."""
        self._create_affiliate(uid="99999999", name="Jane Roe", personal_id="12345")
        results = self.Affiliate.sudo()._name_search("12345")
        self.assertTrue(results, "Should find affiliate by personal_id")

    def test_name_search_by_name(self):
        """_name_search finds affiliates by name."""
        self._create_affiliate(uid="10101010", name="Unique Search Name")
        results = self.Affiliate.sudo()._name_search("Unique Search")
        self.assertTrue(results, "Should find affiliate by name")

    # ─── _compute_name on affiliation_configuration ───────────────────────────

    def test_configuration_compute_name_es(self):
        """affiliation_configuration._compute_name returns Spanish label."""
        config = self.env["affiliation.affiliation_configuration"].sudo()
        config_es = config.with_context(lang="es_AR")
        record = config_es.browse(1)
        record._compute_name()
        self.assertIn("Configuraci", record.name or "")

    # ─── index on uid / affiliation_number ───────────────────────────────────

    def test_uid_index_exists(self):
        """Verify that the uid_unique index exists on the affiliate table."""
        self.env.cr.execute(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'affiliation_affiliate' AND indexname LIKE '%uid%'"
        )
        indexes = [r[0] for r in self.env.cr.fetchall()]
        self.assertTrue(any("uid" in i for i in indexes))

    # ─── _check_uid edge cases (P0 regression) ────────────────────────────────

    def test_uid_empty_string_raises_validation_error(self):
        """Writing an empty uid must raise ValidationError, not IndexError.

        Regression: `record.uid[0] == '0'` ran before any falsy guard and
        crashed with IndexError on '' (empty string bypasses the NOT NULL
        column check because it is not NULL).
        """
        aff = self._create_affiliate(uid="70777001")
        with self.assertRaises(ValidationError):
            aff.write({"uid": ""})

    def test_batch_create_types_does_not_crash(self):
        """Batch create of affiliate types must not hit ExpectedSingleton.

        Regression: _check_name read self.name/self.id without a loop.
        """
        AffiliateType = self.env["affiliation.affiliate_type"]
        records = AffiliateType.create(
            [{"name": "Audit Batch A", "enabled": True}, {"name": "Audit Batch B", "enabled": True}]
        )
        self.assertEqual(len(records), 2)

    def test_batch_create_duplicate_name_raises_validation_error(self):
        """Duplicate names in a batch raise ValidationError (not ValueError)."""
        AffiliateType = self.env["affiliation.affiliate_type"]
        with self.assertRaises(ValidationError):
            AffiliateType.create([{"name": "Audit Dup X", "enabled": True}, {"name": "Audit Dup X", "enabled": True}])
