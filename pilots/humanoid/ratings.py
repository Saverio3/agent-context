"""Can ratings predict humanoid robot matches? Elo-style rating updated match by match; every match is
predicted BEFORE its result is used. Writes results/humanoid/RATINGS.md and data/humanoid/ratings.csv."""
import csv, math, os
from collections import defaultdict


def norm(t):
    return " ".join(t.lower().replace("-", " ").split())


def run(rows, K=40, carry=0.75, margin=True):
    R = defaultdict(lambda: 1500.0)
    games = defaultdict(int)
    last_year = {}
    preds = []
    for r in rows:
        a, b = norm(r["home"]), norm(r["away"])
        for t in (a, b):
            if t in last_year and last_year[t] != r["year"]:
                R[t] = 1500 + carry * (R[t] - 1500)
            last_year[t] = r["year"]
        ga, gb = int(r["home_goals"]), int(r["away_goals"])
        if ga == gb and r["pens"]:
            pa, pb = map(int, r["pens"].split(":")); res = 1.0 if pa > pb else 0.0
        else:
            res = 1.0 if ga > gb else 0.0 if ga < gb else 0.5
        exp = 1 / (1 + 10 ** ((R[b] - R[a]) / 400))
        known = games[a] >= 2 and games[b] >= 2
        preds.append(dict(r, exp=exp, res=res, known=known, gap=abs(R[a] - R[b])))
        mult = math.log(abs(ga - gb) + 1) + 1 if margin else 1
        R[a] += K * mult * (res - exp); R[b] -= K * mult * (res - exp)
        games[a] += 1; games[b] += 1
    return preds, R, games


def score(preds, cond=lambda p: True):
    ps = [p for p in preds if p["known"] and p["res"] != 0.5 and cond(p)]
    if not ps:
        return 0, float("nan")
    return len(ps), sum((p["exp"] > 0.5) == (p["res"] == 1) for p in ps) / len(ps)


def main():
    rows = list(csv.DictReader(open("data/humanoid/matches.csv")))
    for r in rows:
        r["year"] = int(r["year"] or 0); r["phase"] = int(r["phase"]); r["order"] = int(r["order"])
    # SPL knockout pages list finals first -> reverse to get time order
    rows.sort(key=lambda r: (r["league"], r["year"], r["phase"], r["order"] if r["phase"] == 0 else -r["order"]))
    lines = ["# Can we predict humanoid robot matches?", "",
             "Each match is predicted using only matches played before it. Accuracy is on decisive games between "
             "teams that had already played at least 2 rated games. A coin flip scores 50%.", "",
             "| League | Matches in data | Teams | Predicted games | Accuracy (higher-rated team wins) | Accuracy when rating gap > 150 |",
             "|---|---|---|---|---|---|"]
    allR = []
    for lg in ("HSL", "SPL"):
        sub = [r for r in rows if r["league"] == lg]
        preds, R, games = run(sub)
        n, acc = score(preds)
        n2, acc2 = score(preds, lambda p: p["gap"] > 150)
        teams = len({norm(r["home"]) for r in sub} | {norm(r["away"]) for r in sub})
        lines.append(f"| {lg} ({', '.join(str(y) for y in sorted({r['year'] for r in sub}))}) | {len(sub)} | {teams} | {n} | {acc:.0%} | {acc2:.0%} ({n2} games) |")
        top = sorted(((v, t) for t, v in R.items() if games[t] >= 4), reverse=True)[:8]
        allR += [(lg, t, round(v), games[t]) for v, t in sorted(R.items() and ((v, t) for t, v in R.items()), reverse=True)]
        lines += ["", f"**{lg} top-rated teams now:** " + ", ".join(f"{t.title()} {v:.0f}" for v, t in top), ""]
        lines.insert(len(lines), "")
    draws = sum(int(r["home_goals"]) == int(r["away_goals"]) for r in rows)
    goals = [int(r["home_goals"]) + int(r["away_goals"]) for r in rows]
    lines += ["", f"Draws: {draws}/{len(rows)} ({draws / len(rows):.0%}). Average goals per game: {sum(goals) / len(goals):.1f}. "
              f"Biggest win margin: {max(abs(int(r['home_goals']) - int(r['away_goals'])) for r in rows)} goals."]
    os.makedirs("results/humanoid", exist_ok=True)
    open("results/humanoid/RATINGS.md", "w").write("\n".join(lines) + "\n")
    with open("data/humanoid/ratings.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["league", "team", "rating", "games"]); w.writerows(allR)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
