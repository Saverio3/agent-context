from . import _bk, _rules
NAME = "Stats: exponential forgetting"
LOSSLESS = False
DESCRIPTION = (_rules.exp_decay.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.exp_decay)
