from . import _bk, _rules
NAME = "Data eng: delta-encoded file views"
LOSSLESS = False
DESCRIPTION = (_rules.file_delta.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.file_delta)
