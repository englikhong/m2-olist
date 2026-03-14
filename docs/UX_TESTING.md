# UX Testing Checklist — Olist Data Product

**Owner:** UX Tester (assigned independently from domain developers)
**When:** After functional testing passes; before final integration demo
**Focus:** Look and feel, usability, consistency, accessibility

---

## 1. Visual Design — Dark Theme

| # | Test | Pass | Notes |
|---|------|------|-------|
| U1 | All pages use dark background (`#0D0D0D` / `#1A1A1A`) — no white flashes | | |
| U2 | Text is legible on dark background (minimum contrast ratio 4.5:1) | | |
| U3 | Accent colours (red/orange/gold/green) are used consistently for their intended meaning | | |
| U4 | Red = alert/negative · Orange = primary/neutral · Gold = secondary · Green = positive | | |
| U5 | No default Gradio blue/purple accent colours visible anywhere | | |
| U6 | Tab highlights use orange bottom border on active tab | | |
| U7 | Buttons use correct variant: primary=orange, destructive=red, secondary=grey | | |

---

## 2. Layout & Responsiveness

| # | Test | Pass | Notes |
|---|------|------|-------|
| U8 | KPI metric row is visible above the fold on a 1080p screen | | |
| U9 | Charts are legible at default browser zoom (100%) | | |
| U10 | Cards and tiles wrap cleanly on narrower browser widths | | |
| U11 | No horizontal scrollbar at 1280px width | | |
| U12 | Tables do not overflow their container | | |
| U13 | Page headers (left orange bar + title) appear on every domain dashboard | | |

---

## 3. Home / Launchpad

| # | Test | Pass | Notes |
|---|------|------|-------|
| U14 | Hero banner is prominent and clearly identifies the project | | |
| U15 | All 6 nav tiles are visible without scrolling on 1080p | | |
| U16 | Each tile shows: icon, title, owner, description, badge | | |
| U17 | Live badge (green) vs Batch badge (orange) vs Offline (grey) are distinct | | |
| U18 | System status bar shows at top of home page | | |
| U19 | Architecture section is readable and not cluttered | | |

---

## 4. Charts & Visualisations

| # | Test | Pass | Notes |
|---|------|------|-------|
| U20 | All chart backgrounds are transparent or dark (no white chart backgrounds) | | |
| U21 | Chart gridlines are subtle (`#2A2A2A`), not distracting | | |
| U22 | Chart titles are descriptive and include units where relevant | | |
| U23 | Axis labels are present on all bar/line charts | | |
| U24 | Legends are readable on dark background | | |
| U25 | Hover tooltips appear on chart interaction | | |
| U26 | Colour-blind consideration: charts don't rely solely on red/green for distinction | | |

---

## 5. Navigation & Flow

| # | Test | Pass | Notes |
|---|------|------|-------|
| U27 | All 8 tabs (Home, 6 dashboards, Admin) are accessible from main app | | |
| U28 | Tab labels include the emoji icon and developer name | | |
| U29 | Active tab is clearly distinguishable from inactive tabs | | |
| U30 | Dashboards load within 5 seconds on first open (excluding BigQuery query time) | | |
| U31 | Loading indicators appear during data fetching | | |
| U32 | Error states (GCP not configured) show a clear, non-technical message | | |

---

## 6. Admin Panel UX

| # | Test | Pass | Notes |
|---|------|------|-------|
| U33 | Destructive actions (CDC rebuild) are clearly styled in red/danger | | |
| U34 | Safe actions (cache clear) are clearly styled in green/safe | | |
| U35 | Warning banner is visible at top of Admin Panel | | |
| U36 | Log outputs use monospace font on dark background | | |
| U37 | Start/Stop buttons are visually distinct (primary vs stop variant) | | |
| U38 | Action feedback (log output) appears promptly after button click | | |

---

## 7. Typography

| # | Test | Pass | Notes |
|---|------|------|-------|
| U39 | Font is Inter or system sans-serif (no serif fonts visible) | | |
| U40 | Section titles use consistent size and weight | | |
| U41 | KPI values are large and prominent | | |
| U42 | KPI labels are small, uppercase, grey (not competing with values) | | |
| U43 | Code/IDs use monospace font (`JetBrains Mono` or fallback) | | |

---

## 8. Scrollbars & Polish

| # | Test | Pass | Notes |
|---|------|------|-------|
| U44 | Custom scrollbars are dark (`#2A2A2A` track, orange thumb on hover) | | |
| U45 | No unstyled Gradio default components visible | | |
| U46 | Empty states show an icon + message (not blank space) | | |
| U47 | Section dividers (left accent bar) appear before each major section | | |

---

## Overall Rating

| Category | Score (1–5) | Comments |
|----------|-------------|---------|
| Visual consistency | | |
| Data clarity | | |
| Navigation | | |
| Professional feel | | |
| Dark theme execution | | |
| **Overall** | | |

**UX Tester sign-off:**
Name: ___________________  Date: ___________________
