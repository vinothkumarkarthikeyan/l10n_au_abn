# -*- coding: utf-8 -*-
"""
Australian Business Number (ABN) and Australian Company Number (ACN)
validation for Odoo contacts (res.partner).

Implements the official ATO weighted modulus algorithm for ABN validation
and the ASIC algorithm for ACN validation.

References:
    - ABN: https://abr.business.gov.au/Help/AbnFormat
    - ACN: https://asic.gov.au/for-business/registering-a-company/steps-to-register-a-company/australian-company-numbers/
"""

import re
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extend res.partner with Australian Business Number (ABN) and
    Australian Company Number (ACN) fields including validation."""

    _inherit = "res.partner"

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    l10n_au_abn = fields.Char(
        string="ABN",
        size=14,  # 11 digits + 3 spaces when formatted
        help="Australian Business Number (11 digits). "
             "Validated using the official ATO modulus algorithm.",
        tracking=True,
        copy=False,
    )
    l10n_au_acn = fields.Char(
        string="ACN",
        size=11,  # 9 digits + 2 spaces when formatted
        help="Australian Company Number (9 digits). "
             "Validated using the ASIC check-digit algorithm.",
        tracking=True,
        copy=False,
    )
    l10n_au_abn_formatted = fields.Char(
        string="ABN (Formatted)",
        compute="_compute_abn_formatted",
        store=True,
        help="ABN displayed in standard format: XX XXX XXX XXX",
    )
    l10n_au_acn_formatted = fields.Char(
        string="ACN (Formatted)",
        compute="_compute_acn_formatted",
        store=True,
        help="ACN displayed in standard format: XXX XXX XXX",
    )

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------
    @api.depends("l10n_au_abn")
    def _compute_abn_formatted(self):
        """Format ABN as XX XXX XXX XXX for display."""
        for partner in self:
            abn = self._sanitise_number(partner.l10n_au_abn)
            if abn and len(abn) == 11:
                partner.l10n_au_abn_formatted = (
                    f"{abn[:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"
                )
            else:
                partner.l10n_au_abn_formatted = False

    @api.depends("l10n_au_acn")
    def _compute_acn_formatted(self):
        """Format ACN as XXX XXX XXX for display."""
        for partner in self:
            acn = self._sanitise_number(partner.l10n_au_acn)
            if acn and len(acn) == 9:
                partner.l10n_au_acn_formatted = (
                    f"{acn[:3]} {acn[3:6]} {acn[6:9]}"
                )
            else:
                partner.l10n_au_acn_formatted = False

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------
    @api.constrains("l10n_au_abn")
    def _check_abn(self):
        """Validate ABN using the official ATO weighted modulus algorithm.

        Algorithm (from ATO):
            1. Subtract 1 from the first digit of the ABN.
            2. Multiply each digit by its corresponding weighting factor:
               [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
            3. Sum all products.
            4. Divide the sum by 89.
            5. If the remainder is 0, the ABN is valid.
        """
        for partner in self:
            if not partner.l10n_au_abn:
                continue
            abn = self._sanitise_number(partner.l10n_au_abn)
            if not abn:
                continue
            if not self._validate_abn(abn):
                raise ValidationError(
                    f"Invalid Australian Business Number (ABN): "
                    f"'{partner.l10n_au_abn}'.\n\n"
                    f"An ABN must be exactly 11 digits and pass the "
                    f"ATO modulus 89 check. Please verify the number "
                    f"at https://abr.business.gov.au/"
                )

    @api.constrains("l10n_au_acn")
    def _check_acn(self):
        """Validate ACN using the ASIC check-digit algorithm.

        Algorithm (from ASIC):
            1. Multiply each of the first 8 digits by its weighting factor:
               [8, 7, 6, 5, 4, 3, 2, 1]
            2. Sum all products.
            3. Divide the sum by 10 to get the remainder.
            4. Subtract the remainder from 10 — if result is 10, use 0.
            5. The result should equal the 9th (check) digit.
        """
        for partner in self:
            if not partner.l10n_au_acn:
                continue
            acn = self._sanitise_number(partner.l10n_au_acn)
            if not acn:
                continue
            if not self._validate_acn(acn):
                raise ValidationError(
                    f"Invalid Australian Company Number (ACN): "
                    f"'{partner.l10n_au_acn}'.\n\n"
                    f"An ACN must be exactly 9 digits and pass the "
                    f"ASIC check-digit algorithm. Please verify the "
                    f"number at https://connectonline.asic.gov.au/"
                )

    _sql_constraints = [
        (
            "l10n_au_abn_unique",
            "UNIQUE(l10n_au_abn)",
            "This ABN is already registered to another contact. "
            "Each ABN must be unique.",
        ),
        (
            "l10n_au_acn_unique",
            "UNIQUE(l10n_au_acn)",
            "This ACN is already registered to another contact. "
            "Each ACN must be unique.",
        ),
    ]

    # -------------------------------------------------------------------------
    # ONCHANGE — real-time formatting as user types
    # -------------------------------------------------------------------------
    @api.onchange("l10n_au_abn")
    def _onchange_abn(self):
        """Sanitise and auto-format ABN as user types."""
        if self.l10n_au_abn:
            sanitised = self._sanitise_number(self.l10n_au_abn)
            if sanitised and len(sanitised) == 11:
                self.l10n_au_abn = (
                    f"{sanitised[:2]} {sanitised[2:5]} "
                    f"{sanitised[5:8]} {sanitised[8:11]}"
                )

    @api.onchange("l10n_au_acn")
    def _onchange_acn(self):
        """Sanitise and auto-format ACN as user types."""
        if self.l10n_au_acn:
            sanitised = self._sanitise_number(self.l10n_au_acn)
            if sanitised and len(sanitised) == 9:
                self.l10n_au_acn = (
                    f"{sanitised[:3]} {sanitised[3:6]} {sanitised[6:9]}"
                )

    # -------------------------------------------------------------------------
    # VALIDATION LOGIC — static methods for testability
    # -------------------------------------------------------------------------
    @staticmethod
    def _sanitise_number(value):
        """Remove all non-digit characters from the input string.

        Args:
            value: Raw input string (may contain spaces, dashes, etc.)

        Returns:
            String containing only digits, or empty string if input is falsy.
        """
        if not value:
            return ""
        return re.sub(r"\D", "", value)

    @staticmethod
    def _validate_abn(abn):
        """Validate an Australian Business Number (ABN).

        Uses the official ATO weighted modulus 89 algorithm.

        Args:
            abn: String of exactly 11 digits (sanitised, no spaces).

        Returns:
            True if the ABN is valid, False otherwise.

        Example:
            >>> ResPartner._validate_abn("51824753556")
            True
            >>> ResPartner._validate_abn("12345678901")
            False
        """
        if not abn or len(abn) != 11 or not abn.isdigit():
            return False

        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        digits = [int(d) for d in abn]

        # Step 1: Subtract 1 from the first digit
        digits[0] -= 1

        # Step 2-3: Multiply by weights and sum
        total = sum(d * w for d, w in zip(digits, weights))

        # Step 4-5: Check divisibility by 89
        return total % 89 == 0

    @staticmethod
    def _validate_acn(acn):
        """Validate an Australian Company Number (ACN).

        Uses the ASIC check-digit algorithm.

        Args:
            acn: String of exactly 9 digits (sanitised, no spaces).

        Returns:
            True if the ACN is valid, False otherwise.

        Example:
            >>> ResPartner._validate_acn("000000019")
            True
            >>> ResPartner._validate_acn("123456789")
            False
        """
        if not acn or len(acn) != 9 or not acn.isdigit():
            return False

        weights = [8, 7, 6, 5, 4, 3, 2, 1]
        digits = [int(d) for d in acn]

        # Multiply first 8 digits by weights and sum
        total = sum(d * w for d, w in zip(digits[:8], weights))

        # Calculate check digit
        remainder = total % 10
        check_digit = (10 - remainder) % 10

        # Compare with the 9th digit
        return digits[8] == check_digit
