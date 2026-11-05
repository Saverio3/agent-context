from . import _bk, _rules
NAME = "Brain: place cells / cognitive map"
LOSSLESS = False
DESCRIPTION = (_rules.place_cells.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.place_cells)
