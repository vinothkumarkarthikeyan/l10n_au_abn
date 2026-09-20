# -*- coding: utf-8 -*-
"""
Unit tests for Australian Business Number (ABN) and Australian Company
Number (ACN) validation logic.

These tests verify the core validation algorithms independently of
the Odoo ORM to ensure correctness of the mathematical checks.

For ORM-integrated tests (constraint validation, onchange, etc.),
see TestABNConstraints which uses Odoo's TransactionCase.
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

from ..models.res_partner import ResPartner


class TestABNAlgorithm(TransactionCase):
    """Test the ABN validation algorithm (ATO weighted modulus 89)."""

    # -----------------------------------------------------------------
    # VALID ABNs — real, publicly available Australian Business Numbers
    # -----------------------------------------------------------------
    def test_valid_abn_qantas(self):
        """Qantas Airways Limited — ABN 16 009 661 901."""
        self.assertTrue(ResPartner._validate_abn("16009661901"))

    def test_valid_abn_woolworths(self):
        """Woolworths Group Limited — ABN 88 000 014 675."""
        self.assertTrue(ResPartner._validate_abn("88000014675"))

    def test_valid_abn_ato(self):
        """Australian Taxation Office — ABN 51 824 753 556."""
        self.assertTrue(ResPartner._validate_abn("51824753556"))

    def test_valid_abn_telstra(self):
        """Telstra Corporation — ABN 33 051 775 556."""
        self.assertTrue(ResPartner._validate_abn("33051775556"))

    def test_valid_abn_bhp(self):
        """BHP Group Limited — ABN 49 004 028 077."""
        self.assertTrue(ResPartner._validate_abn("49004028077"))

    # -----------------------------------------------------------------
    # INVALID ABNs
    # -----------------------------------------------------------------
    def test_invalid_abn_wrong_check(self):
        """ABN with incorrect check digit should fail."""
        self.assertFalse(ResPartner._validate_abn("12345678901"))

    def test_invalid_abn_too_short(self):
        """ABN with fewer than 11 digits should fail."""
        self.assertFalse(ResPartner._validate_abn("1234567890"))

    def test_invalid_abn_too_long(self):
        """ABN with more than 11 digits should fail."""
        self.assertFalse(ResPartner._validate_abn("123456789012"))

    def test_invalid_abn_non_numeric(self):
        """ABN containing letters should fail."""
        self.assertFalse(ResPartner._validate_abn("1234567890A"))

    def test_invalid_abn_empty(self):
        """Empty string should return False."""
        self.assertFalse(ResPartner._validate_abn(""))

    def test_invalid_abn_none(self):
        """None should return False."""
        self.assertFalse(ResPartner._validate_abn(None))

    def test_invalid_abn_all_zeros(self):
        """All zeros should fail (not a valid ABN)."""
        self.assertFalse(ResPartner._validate_abn("00000000000"))

    def test_invalid_abn_all_ones(self):
        """All ones should fail."""
        self.assertFalse(ResPartner._validate_abn("11111111111"))


class TestACNAlgorithm(TransactionCase):
    """Test the ACN validation algorithm (ASIC check-digit)."""

    # -----------------------------------------------------------------
    # VALID ACNs — from ASIC published examples and real companies
    # -----------------------------------------------------------------
    def test_valid_acn_asic_example_1(self):
        """ASIC published example — ACN 000 000 019."""
        self.assertTrue(ResPartner._validate_acn("000000019"))

    def test_valid_acn_asic_example_2(self):
        """ASIC published example — ACN 000 250 000."""
        self.assertTrue(ResPartner._validate_acn("000250000"))

    def test_valid_acn_asic_example_3(self):
        """ASIC published example — ACN 000 500 005."""
        self.assertTrue(ResPartner._validate_acn("000500005"))

    def test_valid_acn_asic_example_4(self):
        """ASIC published example — ACN 999 999 999."""
        # This is the boundary case
        self.assertTrue(ResPartner._validate_acn("999999999"))

    # -----------------------------------------------------------------
    # INVALID ACNs
    # -----------------------------------------------------------------
    def test_invalid_acn_wrong_check(self):
        """ACN with wrong check digit should fail."""
        self.assertFalse(ResPartner._validate_acn("123456789"))

    def test_invalid_acn_too_short(self):
        """ACN with fewer than 9 digits should fail."""
        self.assertFalse(ResPartner._validate_acn("12345678"))

    def test_invalid_acn_too_long(self):
        """ACN with more than 9 digits should fail."""
        self.assertFalse(ResPartner._validate_acn("1234567890"))

    def test_invalid_acn_empty(self):
        """Empty string should return False."""
        self.assertFalse(ResPartner._validate_acn(""))

    def test_invalid_acn_none(self):
        """None should return False."""
        self.assertFalse(ResPartner._validate_acn(None))


class TestABNSanitisation(TransactionCase):
    """Test the number sanitisation helper."""

    def test_sanitise_with_spaces(self):
        """Spaces should be stripped."""
        self.assertEqual(
            ResPartner._sanitise_number("51 824 753 556"),
            "51824753556",
        )

    def test_sanitise_with_dashes(self):
        """Dashes should be stripped."""
        self.assertEqual(
            ResPartner._sanitise_number("51-824-753-556"),
            "51824753556",
        )

    def test_sanitise_with_mixed(self):
        """Mixed separators should all be stripped."""
        self.assertEqual(
            ResPartner._sanitise_number("51 824-753.556"),
            "51824753556",
        )

    def test_sanitise_empty(self):
        """Empty string should return empty string."""
        self.assertEqual(ResPartner._sanitise_number(""), "")

    def test_sanitise_none(self):
        """None should return empty string."""
        self.assertEqual(ResPartner._sanitise_number(None), "")


class TestABNConstraints(TransactionCase):
    """Test ORM-level constraints (require Odoo database)."""

    def test_create_partner_with_valid_abn(self):
        """Creating a partner with a valid ABN should succeed."""
        partner = self.env["res.partner"].create({
            "name": "Test Company Pty Ltd",
            "is_company": True,
            "l10n_au_abn": "51 824 753 556",
        })
        self.assertTrue(partner.id)
        self.assertEqual(partner.l10n_au_abn, "51 824 753 556")

    def test_create_partner_with_invalid_abn_raises(self):
        """Creating a partner with an invalid ABN should raise."""
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Bad ABN Company",
                "is_company": True,
                "l10n_au_abn": "12345678901",
            })

    def test_create_partner_with_valid_acn(self):
        """Creating a partner with a valid ACN should succeed."""
        partner = self.env["res.partner"].create({
            "name": "Test ACN Company",
            "is_company": True,
            "l10n_au_acn": "000 000 019",
        })
        self.assertTrue(partner.id)

    def test_create_partner_with_invalid_acn_raises(self):
        """Creating a partner with an invalid ACN should raise."""
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Bad ACN Company",
                "is_company": True,
                "l10n_au_acn": "123456789",
            })

    def test_abn_formatted_computed(self):
        """Formatted ABN should be computed correctly."""
        partner = self.env["res.partner"].create({
            "name": "Formatted Test",
            "l10n_au_abn": "51824753556",
        })
        self.assertEqual(partner.l10n_au_abn_formatted, "51 824 753 556")

    def test_acn_formatted_computed(self):
        """Formatted ACN should be computed correctly."""
        partner = self.env["res.partner"].create({
            "name": "Formatted ACN Test",
            "l10n_au_acn": "000000019",
        })
        self.assertEqual(partner.l10n_au_acn_formatted, "000 000 019")

    def test_no_abn_is_allowed(self):
        """Partners without ABN should be created without errors."""
        partner = self.env["res.partner"].create({
            "name": "No ABN Contact",
        })
        self.assertTrue(partner.id)
        self.assertFalse(partner.l10n_au_abn)
