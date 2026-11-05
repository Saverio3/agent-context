from . import _bk, _rules
NAME = "Stats: Beta-Binomial need estimate"
LOSSLESS = False
DESCRIPTION = (_rules.bayes.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.bayes)
