from . import riskkit
NAME = "R4 Sticky unfold (new)"
LOSSLESS = False
DESCRIPTION = "When the agent's last 2 messages use 3+ names from a folded output, that output is shown again in full: proactive fetch-back."

def policy(ctx):
    return riskkit.fold(ctx, sticky=2)
