# Independent Testing Checklist — Olist Data Product

**Owner:** Independent Reviewer (not a domain developer — fresh eyes)
**When:** Final review before demo/presentation
**Purpose:** Catch issues that developers miss due to familiarity bias

---

## 1. First Impressions (No Prior Context)

Open the main app cold. Record your first impressions.

| # | Observation | Pass | Notes |
|---|-------------|------|-------|
| I1 | Can you identify what this product does within 10 seconds? | | |
| I2 | Is the team clearly presented on the Home page? | | |
| I3 | Is the navigation immediately obvious? | | |
| I4 | Is the visual style professional and consistent? | | |
| I5 | Does the app feel "finished" or "like a work-in-progress"? | | |

---

## 2. Data Trustworthiness

| # | Test | Pass | Notes |
|---|------|------|-------|
| I6 | Do the KPI numbers look plausible for Brazil's largest marketplace? | | |
| I7 | Revenue figures — do they match expected Olist dataset scale (~R$13M total)? | | |
| I8 | Customer count — does it match known dataset (~96k unique customers)? | | |
| I9 | Review scores — average should be ~4.1 across the dataset | | |
| I10 | Payment split — credit card should be ~74% of orders | | |
| I11 | Geographic concentration — São Paulo state should dominate customer count | | |
| I12 | Are there any obvious data quality issues visible in tables/charts? | | |

---

## 3. Cross-Dashboard Consistency

| # | Test | Pass | Notes |
|---|------|------|-------|
| I13 | Total revenue is consistent across Payment and Customer 360 dashboards | | |
| I14 | Order counts are consistent across Product, Seller, and Geography dashboards | | |
| I15 | Date ranges are consistent across all dashboards | | |
| I16 | All dashboards use the same colour language (red=bad, green=good) | | |
| I17 | All tab labels follow the format: `<Icon> <Domain> — <Name>` | | |

---

## 4. Edge Case Behaviour

| # | Test | Pass | Notes |
|---|------|------|-------|
| I18 | Enter a random string in Customer lookup — does app handle gracefully? | | |
| I19 | Open Admin Panel — does warning display without any action taken? | | |
| I20 | Click "Refresh Status" in Admin — does status appear correctly? | | |
| I21 | Switch rapidly between tabs — any crashes or blank charts? | | |
| I22 | Resize browser window — does layout adapt reasonably? | | |

---

## 5. Admin Panel Safety Review

| # | Test | Pass | Notes |
|---|------|------|-------|
| I23 | Destructive actions (CDC rebuild) are clearly labelled and visually distinct? | | |
| I24 | Warning banner is prominent and specific? | | |
| I25 | Log output appears after actions (not silent) | | |
| I26 | No action can be taken without clear user intent (no auto-execution) | | |

---

## 6. Documentation Check

| # | Test | Pass | Notes |
|---|------|------|-------|
| I27 | `quick-setup.md` — can a new team member follow it without help? | | |
| I28 | Each developer's `README.md` — does it explain how to run standalone? | | |
| I29 | `CLAUDE.md` — are the merge contract rules clear and complete? | | |
| I30 | `project-plan.md` — does it accurately reflect what was built? | | |

---

## 7. Business Value Assessment

As an independent observer, rate each dashboard on whether it would be useful to a real e-commerce business.

| Dashboard | Business Value (1–5) | Insight Quality | Actionability | Comments |
|-----------|---------------------|----------------|---------------|---------|
| Home / Launchpad | | | | |
| Customer 360 + NBA | | | | |
| Payment Analytics | | | | |
| Reviews & Satisfaction | | | | |
| Product Analytics | | | | |
| Seller Performance | | | | |
| Geography Analytics | | | | |

---

## 8. Issues Found

List any bugs, inconsistencies, or suggestions not covered above:

| # | Issue Description | Severity (High/Med/Low) | Assigned To | Resolved |
|---|-------------------|------------------------|-------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

## Overall Assessment

**Recommendation:** ☐ Ready for demo &nbsp;&nbsp; ☐ Minor fixes needed &nbsp;&nbsp; ☐ Major issues — do not demo

**Summary comments:**
```
[Write your overall assessment here]
```

**Independent Reviewer sign-off:**
Name: ___________________  Date: ___________________
Organisation / Role: ___________________
