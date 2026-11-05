from . import _bk, _rules
NAME = "Brain: 7 chunks (Miller)"
LOSSLESS = False
DESCRIPTION = (_rules.chunking.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.chunking)
