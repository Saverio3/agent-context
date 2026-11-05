from . import _bk, _rules
NAME = "Control: feedback controller"
LOSSLESS = False
DESCRIPTION = (_rules.controller.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.controller)
