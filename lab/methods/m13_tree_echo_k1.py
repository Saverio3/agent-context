from . import m12_tree_echo
NAME = "Tree + echo, only last step in full (new)"
LOSSLESS = False
DESCRIPTION = "Same as Tree + echo, but only the most recent step stays in full (more aggressive)."

def policy(ctx):
    return m12_tree_echo.fold(ctx, keep=1)
