"""Reference solution for exercise 11.3.

`invoice` bound the function into its own namespace at import, so the name
the call resolves is `invoice.vat_rate_percent`, and that is what has to be
replaced. Patching `rates.vat_rate_percent` rebinds a name nobody reads.
"""

PATCH_TARGET = "invoice.vat_rate_percent"
