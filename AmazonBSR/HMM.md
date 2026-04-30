---
aliases: []
tags:
  - architecture/mindmap
  - status/draft
date_created: 2026-03-23
last_modified: 2026-03-23
---

# 🧠 Mindmap: Untitled

## 🎯 Core Objective
Hidden variable models
You have an **observable state** (the BSR number, which is noisy) and a **hidden state** (the actual true sales count, which you cannot see).
- **Kalman Filters:** Originally used in guidance systems and widely adopted in algorithmic trading, a Kalman Filter takes noisy, continuous measurements over time (your scraped BSR) and produces a statistically optimal estimate of the underlying true state (daily sales velocity). It smooths out weird Amazon API glitches and isolates the true trajectory of the product.
- **Hidden Markov Models:** An HMM can be trained to look at the sequence of BSR movements and output the most likely sequence of hidden events (e.g., State 0: No Sale, State 1: Single Sale, State 2: Multiple Sales).

---

## 🗺️ The Map
*(Use the Mermaid syntax below to visually map the components and their relationships. Update as the system architecture evolves.)*

```mermaid
mindmap
  root((Core System))
    Branch A
      Node A1
      Node A2
    Branch B
      Node B1
        Sub-node B1a