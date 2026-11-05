from . import _bk, _rules
NAME = "Brain: sleep consolidation"
LOSSLESS = False
DESCRIPTION = (_rules.sleep_consolidation.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.sleep_consolidation)
