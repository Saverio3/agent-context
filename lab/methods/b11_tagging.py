from . import _bk, _rules
NAME = "Brain: synaptic tag and capture"
LOSSLESS = False
DESCRIPTION = (_rules.synaptic_tagging.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.synaptic_tagging)
