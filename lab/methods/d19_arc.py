from . import _bk, _rules
NAME = "Computing: ARC cache"
LOSSLESS = False
DESCRIPTION = (_rules.arc_cache.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.arc_cache)
