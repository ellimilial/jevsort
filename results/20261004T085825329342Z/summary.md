# Repeated-sort results

Same input order; five runs planned per model. Agreement compares all record pairs in final rankings, not classical sort stability.

| Model | Runs | Pair agreement mean/min | Exact matches | Sort seconds mean | Calls mean/total | Call seconds median/p95 | Total USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| typesafe/jev-1.13 | 5 | 96.17%/92.26% | 0/10 | 39.75 | 118.0/590 | 0.312/0.423 | 0.040202 |
| jaredpalmer/kev-4b | 5 | 100.00%/100.00% | 10/10 | 76.65 | 115.0/575 | 0.600/0.943 | 0.029193 |
| liquid/d1 | 5 | 93.29%/89.68% | 0/10 | 53.34 | 117.2/586 | 0.359/1.046 | 0.029298 |

Table includes completed sorts only. Times include network/API overhead and connection retries. Call counts are successful comparisons; extra retry attempts are listed below. Costs are API-reported, not estimates. Five runs provide ten dependent run-pair comparisons per model: a descriptive pilot, not independent statistical samples.

## Direct comparison repeatability

Only identical ordered pairs encountered in multiple sorts are compared; coverage is adaptive and can differ across models.
- typesafe/jev-1.13: 94.28% agreement; 128 repeated ordered pairs, 979 repeat comparisons.
- jaredpalmer/kev-4b: 100.00% agreement; 115 repeated ordered pairs, 1150 repeat comparisons.
- liquid/d1: 94.69% agreement; 155 repeated ordered pairs, 904 repeat comparisons.

Saved successful calls: 1762; 11 belong to interrupted sorts. Logged additional connection attempts: 0.
API-reported cost of all saved successful calls, including interrupted sorts: $0.099395. Failed requests without responses and separate access probes are excluded; their billed cost is unknown.
