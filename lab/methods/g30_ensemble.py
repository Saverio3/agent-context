from . import _bk, _rules
NAME = "Ours: ensemble vote"
LOSSLESS = False
DESCRIPTION = (_rules.ensemble_vote.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.ensemble_vote)
