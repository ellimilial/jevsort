# jevsort

Merge sort using an AI model as an A/B comparator. Give it a list and a fuzzy criterion;
each comparison sends two items to OpenRouter and chooses which comes first.

Replace OpenRouter for a local deployment for 1-2 orders of magnitude speed improvement. 

Python 3.10+; standard library only.

```sh
export OPENROUTER_API_KEY="your-key"
python example.py
```

```python
from jevsort import jevsort

ranked = jevsort(
    ["apple", "carrot", "pear"],
    "Fruit before vegetables, then alphabetical order",
    model="jaredpalmer/kev-4b",
)
```

Items can be any JSON-serialisable values. The function returns a new list.
Calls use your OpenRouter account and may incur charges.

## Experiment

`data-apoptosis.jsonl` contains 31 biomedical resources: names, descriptions, usage
summaries, usage patterns, tags and reported citation counts. No limitations,
references or tracking fields. `criterion.txt` asks which resource is more useful
for pancreatic-cancer target identification.

```sh
python evaluate.py
python evaluate.py --models liquid/d1
python evaluate.py --report results/{timestamp}
```

The default experiment runs five sorts each with Jev, Kev and D1. It saves inputs,
rankings and call logs under `results/{timestamp}/`, plus a summary of repeated A/B agreement,
final-ranking agreement, latency, comparison counts and API-reported cost.
Each run creates a new directory named with its UTC start time, preserving earlier runs.

Five runs are a small descriptive experiment. Input order stays fixed; agreement
measures consistency, not biological correctness or classical sort stability
(preserving the input order of equal items).

Timestamped results can be included in Git so results can be shared with the code.
Archived source data and editor files are ignored.

MIT licence.

Open `analysis.ipynb` for run setup, runtime, cost, stability and returned rankings.
Set `RESULTS` to a run directory; saved outputs are included. No API calls.
