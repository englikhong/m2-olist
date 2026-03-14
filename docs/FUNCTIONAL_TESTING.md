# Functional Testing Checklist — Olist Data Product

**Owner:** Each domain developer + 1 assigned peer reviewer
**When:** Before submitting dashboard for integration into `app.py`

---

## 1. GCP Connectivity

| # | Test | Pass | Notes |
|---|------|------|-------|
| F1 | Dashboard loads without crashing when `gcp_config.yaml` is present | | |
| F2 | Dashboard shows a clear error message (not a crash) when GCP config is missing | | |
| F3 | Dashboard shows a clear error message when BigQuery query fails (e.g. table not found) | | |
| F4 | ADC auth method connects successfully to BigQuery | | |
| F5 | Service account auth method connects successfully to BigQuery | | |
| F6 | `qualified_table()` returns correct fully-qualified table reference | | |

---

## 2. Data Loading

| # | Test | Pass | Notes |
|---|------|------|-------|
| F7 | All charts load data on page open (`dashboard.load()` fires) | | |
| F8 | Charts render without errors when data is available | | |
| F9 | Charts show an empty state (not a crash) when query returns 0 rows | | |
| F10 | DataFrames display correct column headers | | |
| F11 | Numeric values are rounded to sensible decimal places | | |
| F12 | Date columns display in readable format (YYYY-MM or YYYY-MM-DD) | | |

---

## 3. Interactive Controls

| # | Test | Pass | Notes |
|---|------|------|-------|
| F13 | All buttons trigger their correct action | | |
| F14 | Search/lookup inputs accept valid values and return results | | |
| F15 | Sliders and dropdowns update charts correctly | | |
| F16 | Empty input to search fields shows appropriate message (not crash) | | |
| F17 | Invalid input (e.g. non-existent customer ID) shows "Not found" message | | |

---

## 4. Domain-specific Functional Tests

### Customer 360 (Lik Hong)
| # | Test | Pass |
|---|------|------|
| F18 | Customer profile lookup returns correct aggregated metrics | |
| F19 | RFM chart shows all 5+ segments | |
| F20 | Next Best Action generates at least one recommendation | |
| F21 | Order history table shows correct columns and is sorted by date desc | |

### Payment (Meng Hai)
| # | Test | Pass |
|---|------|------|
| F22 | Pie chart revenue totals match sum of payment_value in Fact_Orders | |
| F23 | Instalment distribution only shows credit_card orders | |
| F24 | Cancellation rate is between 0% and 100% | |

### Reviews (Lanson)
| # | Test | Pass |
|---|------|------|
| F25 | Score distribution covers all 5 score levels (1–5) | |
| F26 | Low score filter updates table when slider changes | |
| F27 | Delivery delay chart shows negative values for early deliveries | |

### Products (Ben)
| # | Test | Pass |
|---|------|------|
| F28 | Category names appear in English (not Portuguese) | |
| F29 | Category trend chart updates when a valid category is entered | |
| F30 | Top products table shows product_id, category, revenue | |

### Sellers (Huey Ling)
| # | Test | Pass |
|---|------|------|
| F31 | Leaderboard is sorted by revenue descending | |
| F32 | At-risk sellers all meet the flagging criteria (score < 3 OR late > 30%) | |
| F33 | Delivery delay chart includes both early (negative) and late (positive) bars | |

### Geography (Kendra)
| # | Test | Pass |
|---|------|------|
| F34 | Choropleth renders state boundaries for Brazil | |
| F35 | Scatter map points fall within Brazil's geographic bounds | |
| F36 | Underserved regions table is sorted by customers_per_seller descending | |

---

## 5. Admin Panel (Lik Hong)
| # | Test | Pass |
|---|------|------|
| F37 | Clear cache completes without error when Redis is available | |
| F38 | Clear cache shows "unavailable" message (not crash) when Redis is not running | |
| F39 | Start Agent button launches simulator and shows PID | |
| F40 | Stop Agent button terminates simulator and confirms stop | |
| F41 | Start Agent when already running shows "already running" message | |
| F42 | Pipeline Status shows correct simulator running/stopped state | |

---

## Sign-off

| Developer | Tested Date | Peer Reviewer | Review Date |
|-----------|-------------|---------------|-------------|
| Lik Hong | | | |
| Meng Hai | | | |
| Lanson | | | |
| Ben | | | |
| Huey Ling | | | |
| Kendra | | | |
