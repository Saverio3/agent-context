from . import riskkit
NAME = "R6 Lean guards (new)"
LOSSLESS = False
DESCRIPTION = "Working set + sticky unfold only: the two guards aimed at the most common miss (recent file views), keeping the rest aggressive."

def policy(ctx):
    return riskkit.fold(ctx, working_set=6, sticky=2)
