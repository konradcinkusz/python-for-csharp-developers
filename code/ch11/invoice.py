"""Two ways of reaching the same function, and they patch differently.

`from rates import vat_rate_percent` binds the function object into THIS
module's namespace at import time. `import rates` binds the module, and the
attribute is looked up on it at call time. Both call the same function
today; only the second one still calls whatever `rates.vat_rate_percent` is
by the time the call happens.

That difference is the whole of chapter 11's headline trap, and the two
functions below exist so a test can prove it rather than assert it.
"""

import rates
from rates import vat_rate_percent


def gross_bound(net_pence: int) -> int:
    """Uses the name this module bound at import time.

    The patch target is `invoice.vat_rate_percent`.
    """
    return net_pence + net_pence * vat_rate_percent() // 100


def gross_qualified(net_pence: int) -> int:
    """Looks the name up on the module at call time.

    The patch target is `rates.vat_rate_percent`.
    """
    return net_pence + net_pence * rates.vat_rate_percent() // 100
