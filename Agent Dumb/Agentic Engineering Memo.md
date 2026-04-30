---
tags:
  - agentic-coding
  - research
created: 2026-04-15
updated: 2026-04-15
---
# Master

## bug: Train Spearman WORSE than Test Spearman
```
commit 1
Date:   Wed Apr 15
```

```
  Bug 1: Optimizer minimize MSE, you measure Spearman.
  MSE care about exact numbers. Spearman care about ranking only.
  Optimizer not trying to fix ranking. Dumb.

  Bug 2: Train use different predict than test.
  optimize() use raw wsc. evaluate() maybe use different pipeline.
  Train model ≠ Test model. Not fair comparison.

  ---
  Further Analysis

  Root cause: Proxy objective mismatch.
  MSE ≈ "how far are my numbers from truth"
  Spearman ≈ "is order of my predictions same as order of truth"

  These are loosely related at best. Model can have perfect ranking (Spearman=1) but terrible MSE if predictions are offset from true values. Converse: model can have perfect MSE but random ranking.

  Why Nelder-Mead go wild:
  Derivative-free optimizers need bounds. Without bounds, they explore freely and can land anywhere. The clipping is a hack — it makes evaluation use valid params, but the optimizer already converged to a different (invalid) region's local minimum.

  Why train worse than test:
  Because clip change model. Optimizer found best MSE in crazy-space. Clip that crazy to valid range → model changes. The MSE-optimal clipped model different from MSE-optimal unclipped model. Thus train Spearman suffer.

  The real fix:
  Use Spearman as training objective (via differentiable approximation), OR constrain optimizer bounds strictly, OR apply clipping INSIDE the objective function so optimizer sees what evaluator sees.

```

---

## bug: OOM
```
commit 2
Date: Wed Apr 15
```

```
Root cause: differentiable_spearman_loss() build big (n, n) matrix every optimizer step. n=20K → 3.2 GB per call ×
   100 steps = RAM go boom.

  Other issues:
  - 3 CSVs load with no dtype specs → pandas use big floats
  - .copy() double BSR DataFrame memory
  - Zero gc.collect() across 100 L-BFGS-B iterations
  - Harness subprocess run with NO memory limit (only Claude subprocess had 3 GiB cap)

  Fix

  1. Pairwise matrix → subsample: Cap at 2M pairs. n=20K now use 2M pairs (16 MB) not 160M pairs (3.2 GB).
  2. dtype= on read_csv: int32, float32 not default float64. CSV 15 MB on disk not 100 MB in memory.
  3. gc.collect() every 10 steps: Heap stay clean. No accumulation.
  4. Harness get cgroup limit: Same 3 GiB hard cap as Claude subprocess. OOM kill clean, not crash loop.

  Result: Memory stay bounded. Loop no crash.

```

## dumb: merge_asof
```
commit 3
Date: Wed Apr 15
```

```
What I did (overcomplicated):
  - Tried to merge_asof the entire filtered DataFrame (11k+ rows) in one shot
  - df had indices from Excel row numbers (3539, 3540, ...)
  - After sorting by purchase_date and reset_index(), df_sorted had sequential
  indices (0, 1, 2, ...)
  - merge_asof returned results in df_sorted's order
  - Assigning back via .values or any other method meant mixing up which row got
  which group_id because the index labels didn't match

  Why I did it:
  I defaulted to "vectorized = fast = good" without recognizing that the index
  mismatch from filtering made vectorized assignment broken. Then I kept trying to
  patch the index alignment instead of stepping back.

  Simple approach (what we should have done from the start):
  - Per product: sort its orders by purchase_date, sort group_map for that product
  by day, run merge_asof, map back by purchase_date — no cross-product index
  confusion at all.

  The per-product loop is slower but trivially correct. Speed doesn't matter for 4
  Excel files.

```