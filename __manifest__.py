{
    "name": "Australia - ABN Validation",
    "version": "17.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Australian Business Number (ABN) and ACN validation for contacts",
    "description": """
        Australian Business Number (ABN) & Australian Company Number (ACN) Validation
        ===============================================================================

        This module adds ABN and ACN fields to the contact (res.partner) model with
        real-time validation using the official ATO (Australian Taxation Office)
        weighted modulus algorithm.

        Features:
        - ABN field with automatic formatting (XX XXX XXX XXX)
        - ACN field with automatic formatting (XXX XXX XXX)
        - Server-side validation using official ATO algorithm
        - ABN Lookup integration-ready (ABR API endpoint)
        - Duplicate ABN detection across contacts
        - Search and filter contacts by ABN/ACN
        - Proper Australian localisation (l10n_au) dependency

        Author: Vinoth Kumar Karthikeyan
        GitHub: https://github.com/vinothkumarkarthikeyan
    """,
    "author": "Vinoth Kumar Karthikeyan",
    "website": "https://github.com/vinothkumarkarthikeyan/l10n_au_abn",
    "license": "LGPL-3",
    "depends": ["base", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
    ],
    "demo": [
        "demo/demo_partners.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
