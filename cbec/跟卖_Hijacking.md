---
tags:
  - terminology
  - amazon
  - fraud
created: 2026-04-13
updated: 2026-04-13
---

# 跟卖 (Hijacking)

> [!INFO] Definition
> **跟卖 (Hijacking)** 是指其他卖家在 Amazon 上盗用已有 listing 的销售页面，直接在该 ASIN 下销售自己的产品（通常是正品或仿品），蹭原 listing 的流量和 [[BSR]]。

## 核心要点

- Amazon 允许多个卖家共享同一 listing（跟卖机制本意是让正品在不同渠道流通）
- Hijacker 利用此机制，将自己的产品混入已有热度的 listing
- 后果：页面 reviews 被稀释、品牌形象受损、销量数据被污染

## 跟卖者来源

| 来源 | 动机 |
| :--- | :--- |
| **分销商窜货** | 跨区拿货低价在 Amazon 销售
| **仿品卖家** | 蹭流量卖假货 |
| **跟卖机器人** | 自动化跟卖热门 ASIN |

## 对 BSR 的影响

> [!WARNING] 数据污染风险
> 跟卖导致的销量波动并非真实市场需求，会干扰你的 [[BSR]] 预测模型。

**识别信号：**
- BSR 突然波动，但 reviews 增长与排名变化不匹配
- 多变体产品中某 SKU 突然出现大量同质 reviews
- 销量来源难以归因（无法判断是品牌自营还是跟卖者销售）

## 应对策略

1. **品牌备案 (Brand Registry)**：注册品牌后可以举报跟卖
2. **透明计划 (Transparency)**：Amazon 产品溯源追踪
3. **测试购买 (Test Buy)**：购买跟卖者产品进行真假鉴定后举报
4. **跟卖监控工具**：如 Helium 10、Jungle Scout 监控跟卖

---

## Connections

- [[CBEC_跨境电商全链路痛点与权衡]]
- [[CBEC_术语表]]
