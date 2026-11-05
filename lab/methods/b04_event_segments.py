from . import _bk, _rules
NAME = "Brain: event segmentation"
LOSSLESS = False
DESCRIPTION = (_rules.event_segments.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.event_segments)
