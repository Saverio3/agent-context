from . import _bk, _rules
NAME = "Curve: frame + hide old outputs after 2 steps"
LOSSLESS = False
DESCRIPTION = "Same frame as the cross-field methods; old outputs fully hidden after 2 steps. Gives the trade-off curve."

def policy(ctx):
    return _bk.run(ctx, _rules.mask_k(2), keep=1)
