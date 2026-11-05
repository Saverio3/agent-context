from ..core import STUB
NAME = "Observation masking (JetBrains 2025)"
LOSSLESS = False
DESCRIPTION = "Tool outputs older than the last 5 are replaced by a short placeholder. Published baseline to beat."
KEEP = 5

def policy(ctx):
    tool_idx = [i for i, (r, _) in enumerate(ctx) if r == "tool"]
    old = set(tool_idx[:-KEEP]) if len(tool_idx) > KEEP else set()
    return [STUB if i in old and len(c) > 4 * 12 else c for i, (_, c) in enumerate(ctx)]
