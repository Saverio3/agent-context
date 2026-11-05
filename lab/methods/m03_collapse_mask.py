from ..core import STUB
from . import m01_mask, m02_collapse
NAME = "Version collapse + masking"
LOSSLESS = False
DESCRIPTION = "Both of the above together."

def policy(ctx):
    a, b = m01_mask.policy(ctx), m02_collapse.policy(ctx)
    return [STUB if (x is STUB or y is STUB) else c for x, y, (_, c) in zip(a, b, ctx)]
