"""Engine for the 'ideas from other fields' round (b*, c*, d*, e*, f*, g*, x* methods). Not a method.

Common frame for every method, so only the forgetting rule differs:
  - instructions, task and the agent's own notes are always kept (R3: notes cause most misses)
  - superseded copies of a file become a pointer (version collapse)
  - recent outputs are shown in full (capping them caused most of the remaining misses)
  - for each OLD tool output, the method's rule returns: "full", or a list of lines to keep
Everything hidden stays in storage (fetch-back is charged by the scorer).
"""
import math
import re
from collections import Counter, defaultdict

from ..core import STUB, salient, toks
from . import m02_collapse
from .riskkit import cap, first

ERR = re.compile(r"Error|Exception|Traceback|FAIL|failed|assert", re.I)
SIG = re.compile(r"^\s*(?:\d+[:|]\s*)?\s*(def |class |async def |function |@|import |from )")
NUM = re.compile(r"^\s*\d+[:|]")
VITAL = re.compile(r"Error|Exception|Traceback|FAIL|PASS|passed|failed|assert|\d+ (?:passed|failed)|^[+-][^+-]", re.I)


class Item:
    """One old tool output, with everything a rule may want to look at."""
    __slots__ = ("i", "c", "lines", "age", "kind", "file", "ment", "last_ment", "first_seen_step", "ctxinfo")


class Ctx:
    """Facts about the run so far, computed once per model call."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.step_of, s = {}, 0
        for i, (r, _) in enumerate(ctx):
            if r == "assistant":
                s += 1
            self.step_of[i] = s
        self.now = s
        self.asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
        self.task = set()
        self.echoed = set()
        self.name_steps = defaultdict(list)      # name -> agent steps that mentioned it
        for i, (r, c) in enumerate(ctx):
            if r == "task":
                self.task |= salient(c)
            if r in ("assistant", "task"):
                sal = salient(c)
                self.echoed |= sal
                if r == "assistant":
                    for n in sal:
                        self.name_steps[n].append(self.step_of[i])
        self.df = Counter()                       # in how many messages each name appears
        for _, c in ctx:
            self.df.update(salient(c))
        self.M = max(1, len(ctx))
        self._first = {}

    def mentions_after(self, names, step):
        return sum(1 for n in names for s in self.name_steps.get(n, ()) if s > step)

    def last_mention(self, names):
        return max((s for n in names for s in self.name_steps.get(n, ())), default=-1)

    def idf(self, line):
        return sum(math.log(self.M / self.df[n]) for n in salient(line) if self.df[n])

    def first_seen(self):
        """step at which each name was first seen anywhere in the run"""
        if not self._first:
            for i, (_, c) in enumerate(self.ctx):
                for n in salient(c):
                    self._first.setdefault(n, self.step_of[i])
        return self._first


def kind_of(c):
    if m02_collapse._key(c):
        return "file"
    if ERR.search(c):
        return "error"
    if re.search(r"Found \d+ match|No matches|grep|find ", c[:300]):
        return "search"
    return "other"


LN = re.compile(r"^\s*(\d+)(?::|\t| \|)", re.M)


def collapse_strict(ctx):
    """Version collapse that only hides an older file view when a later view of the same file shows
    (almost) the same line numbers, or the identical text. Different windows of one file stay visible."""
    views = []
    for i, (r, c) in enumerate(ctx):
        if r == "tool":
            k = m02_collapse._key(c)
            views.append((i, k, set(int(x) for x in LN.findall(c)) if k else set(), c))
    latest_text = {c: i for i, _, _, c in views}
    stale = set()
    for a, (i, k, ln, c) in enumerate(views):
        if len(c) <= 48:
            continue
        if latest_text[c] != i:
            stale.add(i); continue
        if not k:
            continue
        for j, k2, ln2, _ in views[a + 1:]:
            if k2 == k and (not ln or (ln2 and len(ln & ln2) >= 0.8 * len(ln))):
                stale.add(i); break
    return [STUB if i in stale else c for i, (_, c) in enumerate(ctx)]


def run(ctx, rule, keep=3):
    """Apply `rule(item, C)` to every old tool output. rule -> "full" | list[str] | None (= one line)."""
    C = Ctx(ctx)
    base = collapse_strict(ctx)
    out = []
    for i, (v, (r, c)) in enumerate(zip(base, ctx)):
        age = C.now - C.step_of[i]
        if r != "tool":
            out.append(v); continue
        if v is STUB:
            out.append(STUB); continue
        if age < keep:
            out.append(c); continue
        it = Item()
        it.i, it.c, it.lines, it.age = i, c, c.splitlines(), age
        it.kind, it.file = kind_of(c), m02_collapse._key(c)
        names = salient(c)
        it.ment = C.mentions_after(names, C.step_of[i])
        it.last_ment = C.last_mention(names)
        it.first_seen_step = C.step_of[i]
        dec = rule(it, C)
        if dec == "full":
            out.append(c)
        else:
            kept = [l for l in (dec or []) if l.strip()]
            body = ["[out] " + first(c)] + [l for l in kept if l.strip() != first(c)]
            out.append("\n".join(body + ["[rest stored]"]))
    return out


def echo(it, C, n=8):
    return [l for l in it.lines[1:] if salient(l) & C.echoed][:n]
