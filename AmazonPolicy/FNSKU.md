---
date: 2026-04-08
related:
  - "[[Amazon_2026_FBA_Fee_Changes]]"
  - "[[3PL]]"
  - "[[Aged_Inventory_Surcharges]]"
tags:
  - amazon
  - fba
  - sku
  - fnsku
  - inventory
---

# FNSKU (Fulfillment Network Stock Keeping Unit)

Amazon's unique identifier for a product in its fulfillment network. Stands for **Fulfillment Network SKU**. Every distinct product variant (size, color, style) gets its own FNSKU.

## FNSKU vs Other Identifiers

| ID | Owner | What It Identifies | Example |
|----|-------|-------------------|---------|
| **FNSKU** | Amazon | Product + variant as it exists in Amazon's warehouse | B08NX5BJPM |
| **ASIN** | Amazon | Product listing (parent or child) | B08NX5BJ |
| **UPC/EAN** | GS1 | Manufacturer product | 001234567890 |
| **Seller SKU** | You | Your internal product reference | WIDGET-BLU-L |

The FNSKU is Amazon's way of tracking which seller's inventory any given unit belongs to — critical in a shared fulfillment network where multiple sellers may offer the same ASIN.

## FNSKU-Level vs ASIN-Level in 2026

Before 2026, Amazon evaluated some fees (like low-inventory fees) at the **parent ASIN** level. In 2026, key fees shifted to **per-FNSKU**.

**The impact:** Under per-ASIN rules, one healthy variant "covers" a low-stock variant. Under per-FNSKU rules, each variant stands alone.

**Example — apparel with 4 variants:**

```
Variant:              Black/Large  Blue/Large  Black/Small  Blue/Small
Units in stock:      500          400         3            2
Days of supply:      45           38          0.5          0.3

Under per-ASIN (2025):  Total = 905 units → No low-inventory fee
Under per-FNSKU (2026): Black/Small and Blue/Small each flagged independently
                        → Low-inventory fees on EVERY sale of those variants
```

Sellers in apparel, beauty, and other multi-variant categories are seeing single low-stock SKUs consume 10%+ of revenue in fees.

## FNSKU Labeling Requirements

- Each unit must have a scannable FNSKU barcode (label or direct print)
- Labels must be applied correctly — wrong FNSKU = [[Inbound Defect Fee]]
- [[3PL]] services typically handle FNSKU labeling as part of FBA Prep
- Amazon may apply a sticker over the original barcode if it conflicts with their scanning system

## FNSKU and Returns

Returns processing fees are also evaluated at the FNSKU level (tracking return rate per variant). A single high-return variant can drag up your overall return rate and trigger fees — even if other variants are fine.

## Related

- **[[Inbound Defect Fee]]** — Mislabeling or misrouting inventory by FNSKU triggers penalties up 30% in 2026.
- **[[Low-Inventory Fee]]** — Now per FNSKU, not per ASIN. Major change for multi-variant sellers.
- **[[3PL]]** — Most 3PLs handle FNSKU labeling as part of their FBA Prep service.

## Source

[[Amazon_2026_FBA_Fee_Changes]] — Section 6 (Inventory Management — Low-Inventory Fees)
