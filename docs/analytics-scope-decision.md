# Perception Analytics Scope Decision: CSV vs PDF Export (T086)

## Overview & Context
Section 5.3 of the Master Specification lists **"Export Analytics (CSV/PDF)"** as a **Good-to-Have** feature.

During Milestone M6 implementation (Task T085), client-side **CSV export** was chosen and implemented for downloading perception summary metrics, time-series job volume counts, and per-class pixel distribution statistics.

---

## Scope Rationale
1. **Data Interchange Standard**: CSV provides raw, machine-readable data suitable for ingestion into external data analytics tools (Pandas, Excel, Tableau, BigQuery).
2. **Client-Side Efficiency**: Client-side CSV generation requires zero additional backend dependencies or binary PDF rendering engine overhead (such as ReportLab or Puppeteer), preserving sub-second responsiveness.
3. **Deferral of PDF Export**: PDF report formatting was deferred to future scope (Section 3.8) to prioritize core perception pipeline reliability, Celery worker async queue performance, and Section 8.2 contract compliance.
