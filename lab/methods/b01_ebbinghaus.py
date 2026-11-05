from . import _bk, _rules
NAME = "Brain: Ebbinghaus spaced repetition"
LOSSLESS = False
DESCRIPTION = (_rules.ebbinghaus.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.ebbinghaus)
