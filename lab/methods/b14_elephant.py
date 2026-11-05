from . import _bk, _rules
NAME = "Elephant: landmark locations"
LOSSLESS = False
DESCRIPTION = (_rules.elephant_landmarks.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.elephant_landmarks)
