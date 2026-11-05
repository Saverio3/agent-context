from . import _bk, _rules
NAME = "Space: progressive transmission"
LOSSLESS = False
DESCRIPTION = (_rules.progressive.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.progressive)
