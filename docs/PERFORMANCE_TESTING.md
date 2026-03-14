# Performance Testing Checklist — Olist Data Product

**Owner:** Performance Tester (independent)
**When:** After all dashboards pass functional and UX testing
**Tools:** Browser DevTools (Network tab), Gradio profiling, BigQuery job history

---

## 1. Dashboard Load Time

Measure time from tab click to all charts rendered (DOM complete).
Run each test 3× and record the median.

| Dashboard | Cold Load (s) | Warm Load (s) | Target | Pass |
|-----------|--------------|---------------|--------|------|
| Home | | | < 2s | |
| Customer 360 (Lik Hong) | | | < 5s | |
| Payment (Meng Hai) | | | < 5s | |
| Reviews (Lanson) | | | < 5s | |
| Products (Ben) | | | < 5s | |
| Sellers (Huey Ling) | | | < 5s | |
| Geography (Kendra) | | | < 8s* | |
| Admin Panel | | | < 2s | |

*Geography map requires external GeoJSON fetch — 8s allowance.

---

## 2. BigQuery Query Performance

For each dashboard, open BigQuery Console → Job History and record query times.

| Dashboard | Query | Duration (s) | Bytes Billed | Target | Pass |
|-----------|-------|-------------|--------------|--------|------|
| Customer 360 | get_rfm_segments | | | < 10s | |
| Customer 360 | get_revenue_trend | | | < 5s | |
| Customer 360 | get_customer_profile | | | < 3s | |
| Payment | get_payment_summary | | | < 5s | |
| Payment | get_monthly_revenue_by_type | | | < 5s | |
| Reviews | get_review_score_distribution | | | < 3s | |
| Reviews | get_score_vs_delivery_delay | | | < 5s | |
| Products | get_top_categories | | | < 5s | |
| Sellers | get_seller_leaderboard | | | < 8s | |
| Sellers | get_at_risk_sellers | | | < 8s | |
| Geography | get_geolocation_sample | | | < 5s | |
| Geography | get_customer_choropleth | | | < 5s | |

**Optimisation triggers:** If any query exceeds target, check:
- Is the table partitioned/clustered in BigQuery?
- Is the query scanning unnecessary columns? (Use `SELECT` specifics, not `*`)
- Can a pre-aggregated view replace the heavy query?

---

## 3. Concurrent User Load

Test with multiple browser tabs open simultaneously.

| Scenario | Result | Target | Pass |
|----------|--------|--------|------|
| 2 dashboards open, switching between tabs | | Stable | |
| 4 tabs open concurrently | | No crash | |
| 6 tabs open (all dashboards) | | < 5% slowdown | |
| Admin Panel + 2 dashboards | | No interference | |

---

## 4. Memory Usage

Monitor Python process memory while running the full app.

| Measurement | Value | Target | Pass |
|-------------|-------|--------|------|
| Idle (app started, no charts loaded) | | < 200 MB | |
| After loading all 6 dashboards | | < 600 MB | |
| After 30 min of use | | No leak (< 10% growth) | |
| After cache clear (Admin Panel) | | Drops to near-idle | |

---

## 5. Real-time Pipeline Performance (Lik Hong)

| Measurement | Value | Target | Pass |
|-------------|-------|--------|------|
| Simulator throughput (events/sec) | | ≥ 2 events/s | |
| Pub/Sub publish latency (avg) | | < 500ms | |
| End-to-end event to BigQuery latency | | < 5 min | |
| Redis cache GET latency (avg) | | < 5ms | |
| Simulator memory usage (after 1h) | | < 100 MB | |

---

## 6. Page Responsiveness Under Data Load

| Test | Result | Target | Pass |
|------|--------|--------|------|
| Customer lookup while RFM chart loads | | UI remains interactive | |
| Refresh one chart — other charts unaffected | | Yes | |
| Admin: CDC rebuild does not freeze UI | | Yes (async) | |

---

## 7. Network Efficiency

Using browser DevTools → Network tab:

| Measurement | Value | Target | Pass |
|-------------|-------|--------|------|
| Total JS bundle size on first load | | < 5 MB | |
| Plotly chart data payload (per chart) | | < 1 MB | |
| No redundant API calls on tab switch | | 0 duplicate calls | |

---

## Summary

| Area | Status | Issues Found |
|------|--------|-------------|
| Dashboard load times | | |
| BigQuery query performance | | |
| Concurrent load | | |
| Memory stability | | |
| Real-time pipeline | | |

**Performance Tester sign-off:**
Name: ___________________  Date: ___________________
