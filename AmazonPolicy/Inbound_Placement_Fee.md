---
date: 2026-04-08
related:
  - "[[Amazon_2026_FBA_Fee_Changes]]"
  - "[[Amazon_AWD]]"
  - "[[3PL]]"
  - "[[FNSKU]]"
tags:
  - amazon
  - fba
  - fees
  - inbound
  - 2026
---

# Inbound Placement Fee

A charge applied when you send inventory to Amazon's fulfillment network. Covers the cost of Amazon redistributing your inventory across its fulfillment center (FC) network so product is geographically positioned near end customers before orders arrive.

## How It Works

When you create a shipment in Seller Central, you choose how many fulfillment centers to split your inventory across. Amazon uses this to determine your **placement fee**:

| Split Type | FC Count | Placement Fee |
|-----------|---------|--------------|
| Minimal split | 1 | Highest |
| Partial split | 2–3 | Reduced |
| Amazon-optimized | 5+ | **$0** |

The logic: Amazon wants inventory pre-positioned near buyers. Fewer splits = more internal redistribution Amazon has to do = higher charge passed to you.

## Fee Calculation

Placement fees are per-unit, typically tiered by product size:

```
Large standard item (minimal split): ~$0.60/unit
Large standard item (partial split): ~$0.30/unit
Large standard item (5+ split):      $0.00
```

At 5,000 units per shipment → **$0 to $3,000** placement fee depending on split choice.

## Why It Matters in 2026

Amazon introduced tiered placement fees in 2026 as part of a broader shift toward charging for operational convenience. Minimal split was previously a marginal cost difference — now it can consume **up to 5% of product margins** at scale.

For high-volume sellers shipping 1,000+ units recurring, optimizing split strategy is one of the fastest ROI operational changes available.

## How to Eliminate the Fee

**Option 1 — Amazon AWD:**
Ship bulk to AWD → AWD auto-distributes to FBA FCs. Zero placement fee, plus AWD waives low-inventory fees and Q4 storage spikes for enrolled ASINs.

**Option 2 — Multi-destination 3PL:**
Ship once to 3PL → 3PL splits across 5+ FCs using its carrier relationships. Typically $0.30–$0.50/unit instead of $0.60+ for minimal split.

## Key Terms

- **[[FC (Fulfillment Center)]]** — An Amazon warehouse. US network spans dozens of FCs (e.g., PHX3, MDW2, DTW5), each specializing in size/product type.
- **Minimal split** — Shipping all inventory to a single FC. Maximum convenience, maximum placement fee.
- **Amazon-optimized split** — Following Amazon's recommended FC map across 5+ locations. Zero placement fee.
- **Inbound Defect Fee** — Related penalty for misrouted, late, or abandoned shipments. Up 30% in 2026.

## Source

[[Amazon_2026_FBA_Fee_Changes]] — Section 4: Inbound Placement Fees
