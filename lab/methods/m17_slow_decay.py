from . import riskkit
NAME = "R2 Slow decay (new)"
LOSSLESS = False
DESCRIPTION = "Instead of folding abruptly at 3 steps, outputs aged 3-8 steps keep up to 20 relevant lines; only older ones shrink to 8."

def policy(ctx):
    return riskkit.fold(ctx, mid=8, mid_lines=20)
