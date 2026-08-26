from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliationPeriod(TransactionCase):
    """Regression tests for affiliation.affiliation_period constraints.

    Covers the P0 audit findings: singleton-unsafe constrains and the
    interval-overlap containment gap (an outer period containing an inner
    one was allowed by the old endpoint-only checks).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Period = cls.env["affiliation.affiliation_period"]

    def _make_affiliate(self, uid):
        return (
            self.env["affiliation.affiliate"].sudo().create({"uid": uid, "name": f"Period Test {uid}", "state": "new"})
        )

    def test_containment_overlap_blocked(self):
        """An outer period containing an inner one must be rejected.

        Regression: old _check_from_date/_check_to_date only matched
        endpoint-inside ranges, so [Feb-Mar] + [Jan-Dec] coexisted.
        """
        aff = self._make_affiliate(70888001)
        self.Period.create(
            {
                "affiliate_id": aff.id,
                "affiliation_number": 940001,
                "from_date": "2026-02-01",
                "to_date": "2026-03-31",
                "closed": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.Period.create(
                {
                    "affiliate_id": aff.id,
                    "affiliation_number": 940002,
                    "from_date": "2026-01-01",
                    "to_date": "2026-12-31",
                }
            )

    def test_open_period_overlaps_any_later_period(self):
        """A still-open period (no to_date) blocks any overlapping new one."""
        aff = self._make_affiliate(70888002)
        self.Period.create(
            {
                "affiliate_id": aff.id,
                "affiliation_number": 941001,
                "from_date": "2026-05-01",
            }
        )
        with self.assertRaises(ValidationError):
            self.Period.create(
                {
                    "affiliate_id": aff.id,
                    "affiliation_number": 941002,
                    "from_date": "2026-06-01",
                    "to_date": "2026-06-30",
                    "closed": True,
                }
            )

    def test_non_overlapping_periods_allowed(self):
        """Back-to-back periods (end == next start) are valid."""
        aff = self._make_affiliate(70888003)
        self.Period.create(
            {
                "affiliate_id": aff.id,
                "affiliation_number": 942001,
                "from_date": "2026-01-01",
                "to_date": "2026-06-30",
                "closed": True,
            }
        )
        period = self.Period.create(
            {
                "affiliate_id": aff.id,
                "affiliation_number": 942002,
                "from_date": "2026-07-01",
                "to_date": "2026-12-31",
                "closed": True,
            }
        )
        self.assertTrue(period.id)

    def test_batch_create_closed_periods_does_not_crash(self):
        """Batch create must not hit ExpectedSingleton in constrains."""
        aff = self._make_affiliate(70888004)
        records = self.Period.create(
            [
                {
                    "affiliate_id": aff.id,
                    "affiliation_number": 943001,
                    "from_date": "2027-01-01",
                    "to_date": "2027-01-31",
                    "closed": True,
                },
                {
                    "affiliate_id": aff.id,
                    "affiliation_number": 943002,
                    "from_date": "2027-02-01",
                    "to_date": "2027-02-28",
                    "closed": True,
                },
            ]
        )
        self.assertEqual(len(records), 2)

    def test_duplicate_affiliation_number_raises_validation_error(self):
        """Duplicate numbers raise ValidationError even in a batch create."""
        aff = self._make_affiliate(70888005)
        other = self._make_affiliate(70888006)
        self.Period.create(
            {
                "affiliate_id": aff.id,
                "affiliation_number": 944001,
                "from_date": "2026-01-01",
                "closed": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.Period.create(
                [
                    {
                        "affiliate_id": other.id,
                        "affiliation_number": 944001,
                        "from_date": "2027-01-01",
                        "closed": True,
                    },
                    {
                        "affiliate_id": other.id,
                        "affiliation_number": 944099,
                        "from_date": "2027-02-01",
                        "closed": True,
                    },
                ]
            )

    def test_dates_order_validation_error(self):
        """from_date >= to_date raises ValidationError (singleton-safe)."""
        aff = self._make_affiliate(70888007)
        with self.assertRaises(ValidationError):
            self.Period.create(
                {
                    "affiliate_id": aff.id,
                    "affiliation_number": 945001,
                    "from_date": "2026-12-31",
                    "to_date": "2026-01-01",
                    "closed": True,
                }
            )
