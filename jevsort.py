"""Merge sort with an A/B decision model. Set OPENROUTER_API_KEY."""

import json
import os
from time import perf_counter, sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def jevsort(options, criterion, model="jaredpalmer/kev-4b", *, log=None):
    """Return a new list, ordered by the criterion prompt."""
    def choose(a, b):
        payload = {
            "model": model,
            "state": {"A": a, "B": b},
            "questions": {"winner": {
                "type": "choice",
                "instructions": f"Which comes first? {criterion}",
                "criteria": {"A": "Option A", "B": "Option B"},
            }},
        }
        request = Request(
            "https://openrouter.ai/api/alpha/decisions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
            },
        )
        start = perf_counter()
        errors = []
        for attempt in range(3):
            try:
                with urlopen(request, timeout=60) as response:
                    data = json.load(response)
                break
            except URLError as error:
                if attempt == 2 or (isinstance(error, HTTPError)
                                    and error.code != 429 and not 500 <= error.code < 600):
                    raise
                errors.append(str(error))
                sleep(attempt + 1)
        seconds = perf_counter() - start
        choice = data["answers"]["winner"]["choice"]
        if choice not in ("A", "B"):
            raise ValueError(f"Expected A or B, got {choice!r}")
        if log:
            log({"a": a, "b": b, "seconds": seconds, "errors": errors, "response": data})
        return choice

    def sort(items):
        if len(items) < 2:
            return items
        middle = len(items) // 2
        left = sort(items[:middle])
        right = sort(items[middle:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if choose(left[i], right[j]) == "A":
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        return result + left[i:] + right[j:]

    return sort(list(options))
