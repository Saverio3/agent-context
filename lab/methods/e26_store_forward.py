from . import _bk, _rules
NAME = "Space: store-and-forward priority"
LOSSLESS = False
DESCRIPTION = (_rules.store_forward.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.store_forward)
