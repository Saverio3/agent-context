from . import _bk, _rules
NAME = "Curve: frame + hide old outputs after 10 steps"
LOSSLESS = False
DESCRIPTION = "Same frame as the cross-field methods; old outputs fully hidden after 10 steps. Gives the trade-off curve."

def policy(ctx):
    return _bk.run(ctx, _rules.mask_k(10), keep=1)
