"""Turn the downloaded RoboCup pages and sheets into one match table: data/humanoid/matches.csv
columns: league, year, source, order, home, away, home_goals, away_goals, pens"""
import csv, glob, html, io, os, re

SCORE = re.compile(r"^(\d{1,2})\s*:\s*(\d{1,2})(?:\s*\[(\d+)\s*:\s*(\d+)\])?$")
BAD = re.compile(r"^(match\s*#?\d*|qf\d|sf\d|pi\d|f\d?|final|finals|semi|quarter|play|round|seeding|consolation|"
                 r"group|game|\d+(st|nd|rd|th)|third|3rd|winner|loser|tie|vs\.?|-|–|bye|knockout|day \d)", re.I)


def clean_team(t):
    t = re.sub(r"\s*\[\d+\]\s*", " ", t).strip()
    t = re.sub(r"^Match\s*#\d+\s*", "", t).strip()
    return re.sub(r"\s+", " ", t)


def page_lines(path):
    t = open(path, errors="ignore").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<iframe.*?</iframe>", "", t, flags=re.S)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|td|th|li|h\d|tr|span|strong|b)>", "\n", t)
    txt = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    return [l.strip() for l in txt.split("\n") if l.strip()]


def from_html(path):
    m = re.search(r"(20\d\d)", path)
    year = int(m.group(1)) if m else None
    league = "HSL" if "hsl" in path else "SPL"
    L = page_lines(path)
    if year is None:
        title = " ".join(L[:30]); m = re.search(r"(20\d\d)", title); year = int(m.group(1)) if m else None
    out, k = [], 0
    for i, l in enumerate(L):
        s = SCORE.match(l)
        if not s or i < 2:
            continue
        a, b = clean_team(L[i - 2]), clean_team(L[i - 1])
        if BAD.match(a) or BAD.match(b) or SCORE.match(L[i - 1]) or len(a) < 2 or len(b) < 2 or a == b:
            continue
        if re.fullmatch(r"[\d.,:\s]+", a + b):
            continue
        out.append(dict(league=league, year=year, source=os.path.basename(path), order=k, home=a, away=b,
                        home_goals=int(s.group(1)), away_goals=int(s.group(2)),
                        pens=f"{s.group(3)}:{s.group(4)}" if s.group(3) else ""))
        k += 1
    return out


def from_csv(path, year_hint):
    rows = list(csv.reader(io.StringIO(open(path, errors="ignore").read())))
    hdr = next((r for r in rows if "Home" in r and "Away" in r), None)
    if not hdr:
        return []
    h = [i for i, x in enumerate(hdr) if x == "Home"]
    a = [i for i, x in enumerate(hdr) if x == "Away"]
    if len(h) < 2:
        return []
    out = []
    for k, r in enumerate(rows[rows.index(hdr) + 1:]):
        try:
            out.append(dict(league="SPL", year=year_hint, source=os.path.basename(path), order=k,
                            home=clean_team(r[h[0]]), away=clean_team(r[a[0]]),
                            home_goals=int(r[h[1]]), away_goals=int(r[a[1]]), pens=""))
        except (ValueError, IndexError):
            pass
    return out


def main():
    raw = "data/humanoid/raw"
    rows = []
    for p in sorted(glob.glob(f"{raw}/*.html")):
        if re.search(r"results", p):
            rows += from_html(p)
    # map each sheet to the year of the page that embeds it
    sheet_year = {}
    for p in glob.glob(f"{raw}/*.html"):
        y = re.search(r"(20\d\d)", p)
        for sid in re.findall(r"spreadsheets/d/e/([\w-]+)/pubhtml", open(p, errors="ignore").read()):
            if y:
                sheet_year[sid] = int(y.group(1))
    for p in sorted(glob.glob(f"{raw}/*.csv")):
        y = next((v for k, v in sheet_year.items() if re.sub(r"[^A-Za-z0-9]", "_", k)[:40] in p), None)
        rows += from_csv(p, y)
    seen, uniq = set(), []
    for r in rows:
        key = (r["league"], r["year"], r["home"].lower(), r["away"].lower(), r["home_goals"], r["away_goals"])
        if key not in seen:
            seen.add(key); uniq.append(r)
    os.makedirs("data/humanoid", exist_ok=True)
    with open("data/humanoid/matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(uniq[0]))
        w.writeheader(); w.writerows(uniq)
    from collections import Counter
    print(len(uniq), "matches")
    print(Counter((r["league"], r["year"]) for r in uniq))


if __name__ == "__main__":
    main()
