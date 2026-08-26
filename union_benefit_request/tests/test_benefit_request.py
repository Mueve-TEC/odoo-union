from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBenefitRequest(TransactionCase):
    """Tests for benefit_request.benefit_request: state workflow,
    hide_* computed fields, _compute_display_name, and constraints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RequestType = cls.env["benefit_request.request_type"]
        cls.BenefitRequest = cls.env["benefit_request.benefit_request"]
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.request_type = cls.RequestType.create({"name": "Test Request Type", "who_apply": "everybody"})
        cls.amount_type = cls.RequestType.create({"name": "Amount Type", "who_apply": "everybody"})

    def _create_request(self, **kw):
        vals = {
            "partner_id": self.partner.id,
            "request_type_id": self.request_type.id,
        }
        vals.update(kw)
        return self.BenefitRequest.sudo().create(vals)

    def _create_amount_request_group(self):
        """Create a request group 'Importes' and link it to a request type."""
        group = self.env["benefit_request.request_group"].create({"name": "Importes"})
        rt = self.RequestType.create({"name": "Amount Request Type", "who_apply": "everybody"})
        rt.write({"request_group_ids": [(4, group.id)]})
        return rt

    # ─── state workflow ────────────────────────────────────────────────────────

    def test_default_state_draft(self):
        """New benefit requests default to 'draft' state."""
        req = self._create_request()
        self.assertEqual(req.state, "draft")

    def test_request_action(self):
        """request() transitions draft -> requested."""
        req = self._create_request()
        req.request()
        self.assertEqual(req.state, "requested")

    def test_authorize_action(self):
        """authorize() transitions requested -> authorized."""
        req = self._create_request()
        req.request()
        req.authorize()
        self.assertEqual(req.state, "authorized")

    def test_reject_action(self):
        """reject() transitions to 'rejected'."""
        req = self._create_request()
        req.reject()
        self.assertEqual(req.state, "rejected")

    def test_cancel_action(self):
        """cancel() transitions to 'canceled'."""
        req = self._create_request()
        req.cancel()
        self.assertEqual(req.state, "canceled")

    def test_set_to_draft_from_draft(self):
        """set_to_draft() from draft keeps state as draft."""
        req = self._create_request()
        req.set_to_draft()
        self.assertEqual(req.state, "draft")

    # ─── amount validation ─────────────────────────────────────────────────────

    def test_request_amount_must_be_positive(self):
        """request() raises when requested_amount <= 0 and amounts are visible."""
        rt = self._create_amount_request_group()
        req = self.BenefitRequest.sudo().create(
            {
                "partner_id": self.partner.id,
                "request_type_id": rt.id,
                "requested_amount": 0,
            }
        )
        req._compute_hides()
        with self.assertRaises(ValidationError):
            req.request()

    def test_authorize_amount_must_be_positive(self):
        """authorize() raises when authorized_amount <= 0 and amounts are visible."""
        rt = self._create_amount_request_group()
        req = self.BenefitRequest.sudo().create(
            {
                "partner_id": self.partner.id,
                "request_type_id": rt.id,
                "requested_amount": 100,
                "authorized_amount": 0,
            }
        )
        req._compute_hides()
        with self.assertRaises(ValidationError):
            req.authorize()

    def test_finalize_paid_amount_validation(self):
        """finalize() raises when paid_amount > authorized_amount."""
        rt = self._create_amount_request_group()
        req = self.BenefitRequest.sudo().create(
            {
                "partner_id": self.partner.id,
                "request_type_id": rt.id,
                "requested_amount": 100,
                "authorized_amount": 100,
                "paid_amount": 200,
            }
        )
        req._compute_hides()
        with self.assertRaises(ValidationError):
            req.finalize()

    # ─── hide_* computed fields ───────────────────────────────────────────────

    def test_hide_amounts_visible_with_group(self):
        """hide_amounts is False when request type has 'Importes' group."""
        rt = self._create_amount_request_group()
        req = self.BenefitRequest.sudo().create({"partner_id": self.partner.id, "request_type_id": rt.id})
        req._compute_hides()
        self.assertFalse(req.hide_amounts)

    def test_hide_amounts_hidden_without_group(self):
        """hide_amounts is True when request type has no groups."""
        req = self._create_request()
        req._compute_hides()
        self.assertTrue(req.hide_amounts)

    # ─── _compute_display_name ───────────────────────────────────────────────

    def test_display_name(self):
        """display_name combines request type name and partner name."""
        req = self._create_request()
        req._compute_display_name()
        self.assertIn(self.request_type.name, req.display_name)
        self.assertIn(self.partner.name, req.display_name)

    # ─── create with auto-create affiliate from import ─────────────────────────

    def test_create_from_import_existing_affiliate(self):
        """create with import_uid resolves to existing affiliate's partner."""
        affiliate = (
            self.env["affiliation.affiliate"]
            .sudo()
            .create({"uid": 50000001, "name": "Import Test Affiliate", "state": "new"})
        )
        req = (
            self.BenefitRequest.sudo()
            .with_context(import_file=True)
            .create(
                {
                    "import_uid": "50000001",
                    "import_name": "Import Test Affiliate",
                    "request_type_id": self.request_type.id,
                }
            )
        )
        self.assertEqual(req.partner_id, affiliate.partner_id)

    def test_create_from_import_auto_create_disabled(self):
        """create with unknown import_uid raises when auto-create disabled."""
        with self.assertRaises(ValidationError):
            self.BenefitRequest.sudo().with_context(import_file=True).create(
                {
                    "import_uid": "60000001",
                    "import_name": "Unknown Affiliate",
                    "request_type_id": self.request_type.id,
                }
            )

    # ─── _message_get_suggested_recipients (Odoo 19 signature) ──────────────

    def test_suggested_recipients_odoo19_signature(self):
        """_message_get_suggested_recipients must accept the Odoo 19 kwargs.

        mail.thread._thread_to_store calls this with
        reply_discussion=, reply_message=, no_create=, primary_email=,
        additional_partners= — regressions here break the discuss thread
        store (RPC_ERROR in the web client).
        """
        req = self._create_request()
        recipients = req._message_get_suggested_recipients(
            reply_discussion=False,
            reply_message=None,
            no_create=True,
            primary_email=False,
            additional_partners=None,
        )
        self.assertIsInstance(recipients, list)
        # Partner should appear exactly once in suggested recipients
        partner_ids = [r.get("partner_id") for r in recipients]
        self.assertIn(req.partner_id.id, partner_ids)
        self.assertEqual(partner_ids.count(req.partner_id.id), 1)

    def test_suggested_recipients_no_partner(self):
        """Returns super() result unchanged when partner_id is empty."""
        # Use a NewId record (in-memory) so partner_id can be False without
        # hitting the NOT NULL constraint at flush time.
        req = self.env["benefit_request.benefit_request"].new(
            {
                "request_type_id": self.request_type.id,
                "responsible": self.env.ref("base.user_admin").id,
            }
        )
        self.assertFalse(req.partner_id)
        recipients = req._message_get_suggested_recipients(
            no_create=True,
            primary_email=False,
        )
        self.assertIsInstance(recipients, list)
        self.assertFalse(any(r.get("partner_id") == req.partner_id for r in recipients))

    # ─── name_search import-context robustness (P0 regression) ───────────────

    def test_import_name_search_with_comma_in_partner_name(self):
        """Commas inside the partner name must not crash the lookup.

        Regression: `_date, _type, _name = name.split(",")` raised ValueError
        when the partner display string contained a comma ("Garcia, Maria").
        maxsplit=2 keeps trailing commas inside the name part.
        """
        req = self._create_request(request_date="2026-08-21")
        probe = f"2026-08-21,{self.request_type.name},Test Partner"
        results = self.BenefitRequest.with_context(import_file=True).name_search(probe)
        self.assertTrue(results)
        self.assertIn(req.id, [r[0] for r in results])

    def test_import_name_search_malformed_short_string(self):
        """Fewer than 3 parts degrades gracefully instead of ValueError."""
        results = self.BenefitRequest.with_context(import_file=True).name_search("Solicitud Simple")
        self.assertIsInstance(results, list)
