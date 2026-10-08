import json
from pathlib import Path

from jevsort import jevsort


records = [
    json.loads(line)
    for line in (Path(__file__).parent / "data-apoptosis.jsonl").read_text().splitlines()
]

items = records[:4]

ranked = jevsort(
    items,
    (Path(__file__).parent / "criterion.txt").read_text().strip(),
)
for rank, item in enumerate(ranked, 1):
    print(rank, item["name"])
