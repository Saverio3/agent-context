from . import riskkit
NAME = "R5 All guards combined (new)"
LOSSLESS = False
DESCRIPTION = "Working set + slow decay + keep notes + sticky unfold + error lines always kept, on top of tree + echo + cap."

def policy(ctx):
    return riskkit.fold(ctx, working_set=6, mid=8, mid_lines=20, keep_notes=True, sticky=2, keep_errors=True)
