"""Five sorts per model in results/{timestamp}; python evaluate.py [--report DIR]."""
import argparse
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from statistics import mean, median
from time import perf_counter

from jevsort import jevsort

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MODELS = ["typesafe/jev-1.13", "jaredpalmer/kev-4b", "liquid/d1"]
DATA = ROOT / "data-apoptosis.jsonl"
RUNS_PER_MODEL = 5

def report(folder):
    snapshot = json.loads((folder / "input.json").read_text())
    models = snapshot["models"]
    runs = [json.loads(s) for s in (folder / "runs.jsonl").read_text().splitlines()]
    all_calls = [json.loads(s) for s in (folder / "calls.jsonl").read_text().splitlines()]
    completed = {(r["model"], r["run"], r.get("attempt", 0)) for r in runs}
    calls = [c for c in all_calls if (c["model"], c["run"], c.get("attempt", 0)) in completed]
    lines = ["# Repeated-sort results", "", "Same input order; five runs planned per model. Agreement compares all record pairs in final rankings, not classical sort stability.", "",
             "| Model | Runs | Pair agreement mean/min | Exact matches | Sort seconds mean | Calls mean/total | Call seconds median/p95 | Total USD |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for model in models:
        group = [r for r in runs if r["model"] == model]
        data = [c for c in calls if c["model"] == model]
        if not group:
            continue
        scores, exact = [], 0
        for x, y in combinations(group, 2):
            positions = {v: i for i, v in enumerate(y["order"])}
            pairs = list(combinations(x["order"], 2))
            scores.append(mean(positions[a] < positions[b] for a, b in pairs))
            exact += x["order"] == y["order"]
        latency = sorted(c["seconds"] for c in data)
        costs = [c["response"].get("usage", {}).get("cost") for c in data]
        cost = f"{sum(costs):.6f}" if all(isinstance(v, (int, float)) for v in costs) else "unavailable"
        agreement = f"{mean(scores):.2%}/{min(scores):.2%}" if scores else "n/a"
        lines.append(f"| {model} | {len(group)} | {agreement} | {exact}/{len(scores)} | {mean(r['seconds'] for r in group):.2f} | {mean(r['calls'] for r in group):.1f}/{len(data)} | {median(latency):.3f}/{latency[max(0, (95 * len(latency) + 99) // 100 - 1)]:.3f} | {cost} |")
    lines += ["", "Table includes completed sorts only. Times include network/API overhead and connection retries. Call counts are successful comparisons; extra retry attempts are listed below. Costs are API-reported, not estimates. Five runs provide ten dependent run-pair comparisons per model: a descriptive pilot, not independent statistical samples.", "", "## Direct comparison repeatability", "", "Only identical ordered pairs encountered in multiple sorts are compared; coverage is adaptive and can differ across models."]
    for model in models:
        groups = defaultdict(list)
        for c in calls:
            if c["model"] == model:
                groups[c["a"].get("id", c["a"]["name"]), c["b"].get("id", c["b"]["name"])].append(c["response"]["answers"]["winner"]["choice"])
        comparisons = [a == b for values in groups.values() for a, b in combinations(values, 2)]
        if comparisons:
            lines.append(f"- {model}: {mean(comparisons):.2%} agreement; {sum(len(v)>1 for v in groups.values())} repeated ordered pairs, {len(comparisons)} repeat comparisons.")
    retries = sum(len(c.get("errors", [])) for c in all_calls)
    costs = [c["response"].get("usage", {}).get("cost") for c in all_calls]
    lines += ["", f"Saved successful calls: {len(all_calls)}; {len(all_calls)-len(calls)} belong to interrupted sorts. Logged additional connection attempts: {retries}."]
    if all(isinstance(v, (int, float)) for v in costs):
        lines.append(f"API-reported cost of all saved successful calls, including interrupted sorts: ${sum(costs):.6f}. Failed requests without responses and separate access probes are excluded; their billed cost is unknown.")
    result = "\n".join(lines) + "\n"
    (folder / "summary.md").write_text(result)
    print(result)


def run(models=MODELS):
    items = [json.loads(s) for s in (DATA).read_text().splitlines()]
    criterion = (ROOT / "criterion.txt").read_text().strip()
    folder = RESULTS / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder.mkdir(parents=True)
    snapshot = {"items": items, "criterion": criterion, "models": models, "runs": 5, "source_sha256": hashlib.sha256((ROOT / 'data-apoptosis.jsonl').read_bytes()).hexdigest()}
    (folder / "input.json").write_text(json.dumps(snapshot, indent=2))
    print(f"Results: {folder}", flush=True)
    rng = random.Random(42)
    with (folder / "calls.jsonl").open("w") as calls, (folder / "runs.jsonl").open("w") as runs:
        for repeat in range(RUNS_PER_MODEL):
            order = list(models)
            rng.shuffle(order)
            for model in order:
                attempt = datetime.now(timezone.utc).isoformat()
                count = 0
                def log(call):
                    nonlocal count
                    count += 1
                    calls.write(json.dumps({"model": model, "run": repeat, "attempt": attempt, **call}) + "\n")
                    calls.flush()
                start = perf_counter()
                ranked = jevsort(items, criterion, model, log=log)
                elapsed = perf_counter() - start
                runs.write(json.dumps({"model": model, "run": repeat, "attempt": attempt, "seconds": elapsed, "calls": count, "order": [r["name"] for r in ranked]}) + "\n")
                runs.flush()
                print(f"{model} run {repeat+1}: {count} calls, {elapsed:.1f}s", flush=True)
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, metavar="DIR")
    parser.add_argument("--models", nargs="+", choices=MODELS, default=MODELS)
    args = parser.parse_args()
    report(args.report if args.report else run(args.models))


if __name__ == "__main__":
    main()
