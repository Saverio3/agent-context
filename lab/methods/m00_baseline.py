NAME = "Baseline (re-read everything)"
LOSSLESS = True
DESCRIPTION = "What agents do today: every earlier message is re-read in full on every step."

def policy(ctx):
    return [c for _, c in ctx]
