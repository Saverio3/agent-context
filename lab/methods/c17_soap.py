from . import _bk, _rules
NAME = "Medicine: SOAP vital findings"
LOSSLESS = False
DESCRIPTION = (_rules.soap.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.soap)
