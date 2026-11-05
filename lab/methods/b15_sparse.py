from . import _bk, _rules
NAME = "Brain: sparse coding"
LOSSLESS = False
DESCRIPTION = (_rules.sparse_coding.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.sparse_coding)
