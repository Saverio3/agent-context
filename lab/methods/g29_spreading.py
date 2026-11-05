from . import _bk, _rules
NAME = "Ours: spreading activation"
LOSSLESS = False
DESCRIPTION = (_rules.spreading_activation.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.spreading_activation)
