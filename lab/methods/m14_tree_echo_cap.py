from . import m12_tree_echo
NAME = "Tree + echo + cap long fresh outputs (new)"
LOSSLESS = False
DESCRIPTION = ("Tree + echo, and even recent outputs longer than 120 lines show only the first 60 and last 40 lines "
               "(the rest stored). Targets huge logs and file dumps that dominate OpenHands runs.")
HEAD, TAIL = 60, 40

def policy(ctx):
    out = []
    for v, (r, c) in zip(m12_tree_echo.fold(ctx), ctx):
        if v is c and r == "tool":
            lines = c.splitlines()
            if len(lines) > HEAD + TAIL + 20:
                v = "\n".join(lines[:HEAD] + [f"[... {len(lines) - HEAD - TAIL} lines stored ...]"] + lines[-TAIL:])
        out.append(v)
    return out
