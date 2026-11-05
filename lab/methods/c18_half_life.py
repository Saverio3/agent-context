from . import _bk, _rules
NAME = "Medicine: drug half-life per kind"
LOSSLESS = False
DESCRIPTION = (_rules.half_life.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.half_life)
