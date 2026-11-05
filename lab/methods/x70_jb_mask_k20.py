from ..core import STUB
NAME = "Curve: JetBrains masking, keep last 20"
LOSSLESS = False
DESCRIPTION = "JetBrains-style masking with a different window, to draw its savings-vs-misses curve."

def policy(ctx):
    tool_idx = [i for i, (r, _) in enumerate(ctx) if r == "tool"]
    old = set(tool_idx[:-20]) if len(tool_idx) > 20 else set()
    return [STUB if i in old and len(c) > 48 else c for i, (_, c) in enumerate(ctx)]
