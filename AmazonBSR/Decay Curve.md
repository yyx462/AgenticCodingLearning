---
aliases:
  - baseline
tags:
  - architecture/mindmap
  - status/draft
date_created: 2026-03-23
last_modified: 2026-03-23
---

# 🧠 Mindmap: Decay Curve

## 🎯 Core Objective
*calculate the expected rank at time $t$ if no sales occur*
- $BSR_{expected} = BSR_{t-1} + (BSR_{t-1} \times \text{DecayFactor})$.

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