"""Parse ChatDev logs into agent-to-agent messages: (speaker, text)."""
import re

HDR = re.compile(r"^\[\d{4}-[\d-]+ [\d:]+ INFO\] (.*)$")
SPEAKER = re.compile(r"^([A-Z][A-Za-z ]{1,40}): (.*)$", re.S)
BILLED = re.compile(r"prompt_tokens: (\d+)")


def parse(path):
    text = open(path, errors="ignore").read()
    entries, cur = [], None
    for line in text.splitlines(keepends=True):
        m = HDR.match(line)
        if m:
            if cur: entries.append(cur)
            cur = [m.group(1) + "\n"]
        elif cur is not None:
            cur.append(line)
    if cur: entries.append(cur)
    msgs = []
    for e in entries:
        body = "".join(e)
        m = SPEAKER.match(body)
        if not m or m.group(1) in ("System", "User"):
            continue
        content = m.group(2)
        # drop the log's own header line ("**Programmer<->CTO on : Coding, turn 0**")
        content = re.sub(r"^\*\*[^\n]*\*\*\n", "", content)
        if content.strip() and not content.startswith("**[Start Chat]**") or "Codes:" in content:
            msgs.append((m.group(1), content.strip()))
    billed = sum(int(x) for x in BILLED.findall(text))
    return msgs, billed


CODE = re.compile(r"(?m)^([\w./-]+\.\w{1,5})\s*\n```[\w+-]*\n(.*?)```", re.S)
DEF = re.compile(r"(?m)^\s*(?:def|class|function|async def)\s+([A-Za-z_]\w*)")


def code_blocks(text):
    """[(filename, code, start, end)] for ChatDev 'name.py\n```python ...```' blocks."""
    return [(m.group(1), m.group(2), m.start(), m.end()) for m in CODE.finditer(text)]


def functions(code):
    """Split code into {name: body} at def/class lines (top-level and methods)."""
    lines = code.splitlines()
    starts = [(i, DEF.match(l).group(1)) for i, l in enumerate(lines) if DEF.match(l)]
    out = {}
    for k, (i, name) in enumerate(starts):
        j = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        out[name] = "\n".join(lines[i:j])
    return out
