from . import riskkit
NAME = "R1 Working set (new)"
LOSSLESS = False
DESCRIPTION = "Tree + echo + cap, but the latest view of any file the agent touched in its last 6 steps is never folded. Targets file-view misses."

def policy(ctx):
    return riskkit.fold(ctx, working_set=6)
