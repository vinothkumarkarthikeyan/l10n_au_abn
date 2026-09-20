# 🇦🇺 Odoo Australian ABN & ACN Validation (`l10n_au_abn`)

> Community module for validating Australian Business Numbers (ABN) and Australian Company Numbers (ACN) in Odoo contacts, using the official ATO and ASIC algorithms.

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-purple.svg)](https://www.odoo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)

---

## The Problem

Australian businesses are required to validate ABN and ACN numbers for invoicing, BAS reporting, and ATO compliance. Odoo's core `l10n_au` module provides chart of accounts and tax codes, but **does not validate ABN/ACN numbers** on contact records — allowing users to enter invalid identifiers that cause downstream compliance issues.

## What This Module Does

| Feature | Description |
|---------|-------------|
| **ABN Validation** | Validates using the official [ATO weighted modulus 89 algorithm](https://abr.business.gov.au/Help/AbnFormat) |
| **ACN Validation** | Validates using the [ASIC check-digit algorithm](https://asic.gov.au/for-business/registering-a-company/steps-to-register-a-company/australian-company-numbers/) |
| **Auto-Formatting** | Formats ABN as `XX XXX XXX XXX` and ACN as `XXX XXX XXX` as the user types |
| **Duplicate Detection** | SQL constraint prevents the same ABN/ACN from being assigned to multiple contacts |
| **Search & Filter** | Search contacts by ABN/ACN; filter to find companies missing ABN |
| **Demo Data** | Pre-loaded with real Australian company ABNs (Qantas, Woolworths) for testing |
| **30+ Unit Tests** | Comprehensive test coverage for all validation logic and edge cases |

## Screenshots

After installing, the contact form shows:

```
┌─────────────────────────────────────┐
│  Contact: Qantas Airways Limited    │
│  ─────────────────────────────────  │
│  Australian Tax Identifiers         │
│  ABN: [ 16 009 661 901 ]           │
│  ACN: [ 009 661 901     ]           │
└─────────────────────────────────────┘
```

If an invalid ABN is entered:
```
⚠️ Invalid Australian Business Number (ABN): '12345678901'.
   An ABN must be exactly 11 digits and pass the ATO modulus 89 check.
   Please verify at https://abr.business.gov.au/
```

## Installation

```bash
# Clone this module into your Odoo addons directory
git clone https://github.com/vinothkumarkarthikeyan/l10n_au_abn.git

# Add the parent directory to Odoo's addons path
python odoo-bin --addons-path=addons,/path/to/l10n_au_abn -d mydb

# Install via Odoo UI:
# Settings → Apps → Search "ABN" → Install
```

## How the ABN Algorithm Works

The ATO uses a **weighted modulus 89** check:

```python
def validate_abn(abn: str) -> bool:
    """
    1. Subtract 1 from the first digit
    2. Multiply each digit by weights: [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    3. Sum all products
    4. Valid if sum % 89 == 0
    """
    weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    digits = [int(d) for d in abn]
    digits[0] -= 1
    return sum(d * w for d, w in zip(digits, weights)) % 89 == 0
```

**Example** — Qantas ABN `16 009 661 901`:
```
Digits:   1  6  0  0  9  6  6  1  9  0  1
Step 1:   0  6  0  0  9  6  6  1  9  0  1   (subtract 1 from first digit)
Weights: 10  1  3  5  7  9 11 13 15 17 19
Products: 0  6  0  0 63 54 66 13 135  0 19
Sum: 356
356 ÷ 89 = 4 remainder 0 ✅ Valid!
```

## Module Structure

```
l10n_au_abn/
├── __manifest__.py           # Module metadata & dependencies
├── __init__.py               # Root package init
├── models/
│   ├── __init__.py
│   └── res_partner.py        # ORM model: ABN/ACN fields + validation
├── views/
│   └── res_partner_views.xml # XML views: form, list, search
├── security/
│   └── ir.model.access.csv   # Access control rules
├── demo/
│   └── demo_partners.xml     # Demo data with real Australian ABNs
├── tests/
│   ├── __init__.py
│   └── test_abn_validation.py # 30+ unit tests
└── README.md
```

## Running Tests

```bash
python odoo-bin -d test_db --test-enable --test-tags l10n_au_abn \
    --addons-path=addons,/path/to/l10n_au_abn \
    --stop-after-init
```

## Future Enhancements

- [ ] **ABR API Integration** — Look up company details from ABN via the [Australian Business Register API](https://abr.business.gov.au/abrxmlsearch/)
- [ ] **ABA Bank File Generation** — Generate ABA payment files for Australian bank transfers
- [ ] **GST Registration Status** — Check if a business is registered for GST via ABR lookup
- [ ] **ARBN Support** — Australian Registered Body Number validation for foreign companies

## Contributing

Contributions welcome! Please:
1. Fork this repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Follow [Odoo's coding guidelines](https://www.odoo.com/documentation/17.0/developer/reference/guidelines.html)
4. Write tests for new functionality
5. Submit a Pull Request

## License

This module is licensed under [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.en.html), consistent with the Odoo Community Association (OCA) standard.

## Author

**Vinoth Kumar Karthikeyan**
- GitHub: [@vinothkumarkarthikeyan](https://github.com/vinothkumarkarthikeyan)
- LinkedIn: [vinothkarthikeyan21](https://linkedin.com/in/vinothkarthikeyan21)
