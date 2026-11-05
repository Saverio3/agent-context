from . import riskkit
NAME = "R3 Keep the agent's notes (new)"
LOSSLESS = False
DESCRIPTION = "Tree + echo + cap, but the agent's own old messages are never shortened (only tool outputs fold)."

def policy(ctx):
    return riskkit.fold(ctx, keep_notes=True)
