from . import _bk, _rules
NAME = "Data eng: LSM-tree tiers"
LOSSLESS = False
DESCRIPTION = (_rules.lsm_tiers.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.lsm_tiers)
