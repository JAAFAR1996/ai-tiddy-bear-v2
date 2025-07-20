# E712 Boolean Comparison Fixes

# ❌ WRONG - These trigger E712 errors:
if some_condition:
    pass

if not some_condition:
    pass

if config.enabled:
    pass

if not config.disabled:
    pass

# ✅ CORRECT - Pythonic way (preferred):
if some_condition:
    pass

if not some_condition:
    pass

if config.enabled:
    pass

if not config.disabled:
    pass

# ✅ ALTERNATIVE - Explicit comparison (if you need to be very explicit):
if some_condition is True:
    pass

if some_condition is False:
    pass

if config.enabled is True:
    pass

if config.disabled is False:
    pass

# Common patterns in test files:

# ❌ WRONG:
assert result.success
assert result.enabled == False
assert coppa_config.parental_consent_required

# ✅ CORRECT (Pythonic):
assert result.success
assert not result.enabled
assert coppa_config.parental_consent_required

# ✅ ALTERNATIVE (Explicit):
assert result.success is True
assert result.enabled is False
assert coppa_config.parental_consent_required is True

# For test assertions, you might also use:
assert result.success
assert not result.enabled
# or
assertTrue(result.success)
assertFalse(result.enabled)
