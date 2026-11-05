from . import _bk, _rules
NAME = "Elephant matriarch: goal anchoring"
LOSSLESS = False
DESCRIPTION = (_rules.matriarch.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.matriarch)
