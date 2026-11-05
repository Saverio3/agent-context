from . import _bk, _rules
NAME = "Radiology: windowing around hits"
LOSSLESS = False
DESCRIPTION = (_rules.radiology_window.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.radiology_window)
