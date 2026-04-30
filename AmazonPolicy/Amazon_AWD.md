---
date: 2026-04-08
related:
  - "[[Amazon_2026_FBA_Fee_Changes]]"
  - "[[Inbound_Placement_Fee]]"
  - "[[FNSKU]]"
tags:
  - amazon
  - fba
  - aws
  - warehousing
  - storage
  - 2026
---

# Amazon AWD (Amazon Warehousing & Distribution)

A storage and distribution service from Amazon — separate from FBA — that acts as a **centralized buffer warehouse** for your inventory before it enters the FBA fulfillment network.

## What AWD Is

FBA = Amazon stores and fulfills your inventory.  
AWD = You store inventory at Amazon (or Amazon-managed facilities), Amazon redistributes to FBA as needed.

```
You → Ship bulk to AWD → Amazon auto-replenishes FBA FCs → Orders fulfilled by FBA
```

AWD is designed for sellers with high-volume, consistent demand who want to avoid the operational complexity of managing multi-destination freight themselves.

## What AWD Waives / Solves

| Problem AWD Solves | Normal FBA Cost | With AWD |
|-------------------|----------------|----------|
| [[Inbound Placement Fee]] | $0.30–$0.60/unit | **$0** |
| Low-inventory fees (per FNSKU) | Applies when <28 days supply | **Waived** |
| Q4 storage spikes | 3× October–December | **Capped** |
| Replenishment automation | Manual FBA restocking | **Auto-replenish** |

## AWD Managed Service Tier

AWD has a managed service tier that adds:

- **25% off storage** fees
- **25% off transport** fees

Total effect: significantly lower total fulfillment cost at scale, plus the fee waivers above.

## Who AWD Is For

**Good fit:**
- High-volume sellers (1,000+ units/month per SKU)
- Products with predictable, consistent demand
- Sellers with thin margins who need every fee optimization
- Sellers with multi-variant catalogs where one low-stock variant triggers fees across the parent ASIN

**Less ideal:**
- Low-volume or inconsistent demand (inventory sitting in AWD = carrying cost)
- Sellers without existing operational infrastructure to manage bulk inbound to AWD
- New sellers still validating product-market fit

## How Enrollment Works

1. Enroll ASINs in AWD via Seller Central
2. Create AWD shipments (ship bulk to AWD origin warehouse)
3. Set reorder points — Amazon monitors and auto-replenishes FBA FCs
4. AWD redistributes across 5+ FCs automatically → zero [[Inbound Placement Fee]]

## AWD vs 3PL for Multi-Destination Splits

| Factor | Amazon AWD | Multi-Destination 3PL |
|--------|-----------|----------------------|
| Placement fee | $0 | $0 (at 5+ splits) |
| Low-inventory waiver | Yes | No (unless separately negotiated) |
| Q4 storage cap | Yes | No |
| Auto-replenish | Yes | No (requires manual trigger) |
| Cost structure | Storage + transport fees | Per-handling + freight |
| Control | Amazon manages | You/3PL manage |

**Practical note:** Many sellers use a 3PL for day-to-day FBA prep and inbound splits, and AWD as an overflow/supply chain buffer. The two are not mutually exclusive.

## Source

[[Amazon_2026_FBA_Fee_Changes]] — Section 4 (Inbound Placement Fees) and Section 6 (Inventory Management — Low-Inventory Fees)
