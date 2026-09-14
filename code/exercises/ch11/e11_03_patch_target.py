"""Exercise 11.3 -- name the target the calling code actually reads.

`invoice.gross_bound` was written as

    from rates import vat_rate_percent
    ...
    net_pence * vat_rate_percent() // 100

The test beside this file patches whatever string PATCH_TARGET names and
then asserts the substitution took effect. The string below is the one
almost everybody writes first, and it does nothing at all.

Change it to the name `gross_bound` resolves when it calls. One string.
"""

PATCH_TARGET = "rates.vat_rate_percent"
