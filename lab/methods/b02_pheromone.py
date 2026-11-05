from . import _bk, _rules
NAME = "Ants: pheromone trails"
LOSSLESS = False
DESCRIPTION = (_rules.pheromone.__doc__ or "").strip() + " Frame: agent notes kept, superseded copies -> pointer, recent outputs full."

def policy(ctx):
    return _bk.run(ctx, _rules.pheromone)
