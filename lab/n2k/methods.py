"""Ways for agents to send each other messages. Each method walks the conversation in order and
returns, per message: tokens sent, plus tokens pulled on demand, plus how many of the receiver's
references to earlier content it could not see (misses).

Assumption for pull methods: the receiver asks for an item when its next reply mentions it
(a file name or a function/class name). That is optimistic: a live test must confirm agents ask.
"""
import difflib
import json
import re

from ..core import salient, toks
from .parse import code_blocks, functions

PULL_REQ = 15            # tokens for a "send me X" request
PREAMBLE = re.compile(r"^\[.*?\]\n", re.S)


def clean(text):
    """Remove the role system prompt ChatDev logs at the top of each message (cacheable, not a message)."""
    return PREAMBLE.sub("", text, count=1)


def _diff(old, new):
    d = "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=1))
    return d


class Base:
    name, desc = "", ""

    def run(self, msgs):
        """msgs: [(speaker, text)] -> (tokens, misses, refs)"""
        self.files, self.paras = {}, set()
        total = misses = refs = 0
        known = set()            # everything the receivers have already been shown (they keep it)
        for k, (spk, text) in enumerate(msgs):
            text = clean(text)
            visible, hidden = self.encode(text)
            total += toks(visible)
            if k + 1 < len(msgs):
                reply = clean(msgs[k + 1][1])
                pulled, ptoks = self.pull(reply)
                total += ptoks
                known |= salient(visible) | salient(pulled)
                used = salient(reply) & salient(hidden)
                refs += len(salient(reply) & salient(text))
                misses += len(used - known)
        return total, misses, refs

    def pull(self, reply):
        return "", 0


class Plain(Base):
    name = "Plain text (today)"
    desc = "Every message sent in full, including full copies of every code file each time."

    def encode(self, text):
        return text, ""


class JsonA2A(Base):
    name = "JSON envelope (A2A-style)"
    desc = "Same content wrapped in a JSON message object, as agent-to-agent standards do."

    def encode(self, text):
        return json.dumps({"kind": "message", "role": "agent", "parts": [{"kind": "text", "text": text}]}), ""


class RefsDiffs(Base):
    name = "Refs + diffs (Pilot 2)"
    desc = "A file sent before unchanged becomes a short reference; a changed file is sent as only its changes."

    def encode(self, text):
        out, last, hidden = [], 0, []
        for fname, code, a, b in code_blocks(text):
            out.append(text[last:a])
            old = self.files.get(fname)
            if old == code:
                out.append(f"[{fname}: unchanged]"); hidden.append(code)
            elif old is not None and len(_diff(old, code)) < len(code):
                out.append(f"[{fname}: changes]\n{_diff(old, code)}"); hidden.append(code)
            else:
                out.append(text[a:b])
            self.files[fname] = code
            last = b
        out.append(text[last:])
        return "".join(out), "\n".join(hidden)


class Dedup(RefsDiffs):
    name = "Refs + diffs + repeated-paragraph refs"
    desc = "Also: any paragraph already sent earlier (task text, requirements, instructions) becomes a reference."

    def encode(self, text):
        vis, hid = super().encode(text)
        out, hidden = [], [hid]
        for p in re.split(r"\n\s*\n", vis):
            if len(p) > 120 and p in self.paras:
                out.append("[see earlier]"); hidden.append(p)
            else:
                out.append(p); self.paras.add(p)
        return "\n\n".join(out), "\n".join(hidden)


class MenuPull(Dedup):
    name = "Need-to-know: menu + pull"
    desc = ("Code is never pushed. The sender lists a menu line per file (name, size, what it defines). "
            "The receiver pulls a file only when it needs it; it gets just the changes if it has an older copy.")

    def encode(self, text):
        self.pending = {}
        out, last, hidden = [], 0, []
        for fname, code, a, b in code_blocks(text):
            out.append(text[last:a])
            names = list(functions(code))[:12]
            out.append(f"[{fname}: {code.count(chr(10))} lines; defines {', '.join(names) or '-'}]")
            self.pending[fname] = code; hidden.append(code)
            last = b
        out.append(text[last:])
        vis, hid = Dedup.encode(self, "".join(out)) if False else self._dedup("".join(out))
        return vis, "\n".join(hidden + [hid])

    def _dedup(self, text):
        out, hidden = [], []
        for p in re.split(r"\n\s*\n", text):
            if len(p) > 120 and p in self.paras:
                out.append("[see earlier]"); hidden.append(p)
            else:
                out.append(p); self.paras.add(p)
        return "\n\n".join(out), "\n".join(hidden)

    def pull(self, reply):
        got, cost = [], 0
        for fname, code in getattr(self, "pending", {}).items():
            names = functions(code)
            if fname in reply or any(re.search(rf"\b{re.escape(n)}\b", reply) for n in names):
                old = self.files.get(fname)
                send = _diff(old, code) if old is not None and old != code else ("" if old == code else code)
                got.append(code); cost += PULL_REQ + toks(send)
                self.files[fname] = code
        return "\n".join(got), cost


class TreePull(MenuPull):
    name = "Need-to-know tree (fractal): file → function"
    desc = ("Two zoom levels. The menu shows file names and function names; the receiver pulls single "
            "functions it mentions, not whole files (whole file only if it names the file itself).")

    def pull(self, reply):
        got, cost = [], 0
        for fname, code in getattr(self, "pending", {}).items():
            fns = functions(code)
            if fname in reply and not fns:
                got.append(code); cost += PULL_REQ + toks(code); continue
            for n, body in fns.items():
                if re.search(rf"\b{re.escape(n)}\b", reply):
                    got.append(body); cost += PULL_REQ + toks(body)
        return "\n".join(got), cost


class Skeleton(MenuPull):
    name = "Low-pass skeleton (epicycloid) + pull"
    desc = ("Send the 'shape' of each file: imports, class and function signature lines, first docstring line. "
            "Function bodies (the fast-changing detail) are pulled only when mentioned.")

    def encode(self, text):
        self.pending = {}
        out, last, hidden = [], 0, []
        for fname, code, a, b in code_blocks(text):
            out.append(text[last:a])
            keep = [l for l in code.splitlines()
                    if re.match(r"\s*(def |class |async def |import |from |function )", l)]
            out.append(f"{fname} (skeleton)\n" + "\n".join(keep))
            self.pending[fname] = code; hidden.append(code)
            last = b
        out.append(text[last:])
        vis, hid = self._dedup("".join(out))
        return vis, "\n".join(hidden + [hid])

    pull = TreePull.pull


ALL = [Plain(), JsonA2A(), RefsDiffs(), Dedup(), MenuPull(), TreePull(), Skeleton()]
