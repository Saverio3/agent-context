from ..core import STUB, salient
from . import m06_echo
NAME = "Echo retention + drop unechoed outputs"
LOSSLESS = False
DESCRIPTION = "Echo retention, and old outputs with zero echoed lines become a pointer entirely."

def policy(ctx):
    v = m06_echo.policy(ctx)
    return [STUB if (x is not c and x.count("\n") <= 2 and "lines stored]" in x) else x for x, (_, c) in zip(v, ctx)]
