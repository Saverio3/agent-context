from . import _bk, _rules
NAME = "Brain: amygdala surprise tagging"
LOSSLESS = False
DESCRIPTION = (_rules.amygdala.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.amygdala)
