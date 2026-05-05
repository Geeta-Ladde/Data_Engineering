# 🔧 Data Pipeline Maintenance Plan

> **Production-grade pipeline ownership, on-call rotation schedules,
> investor reporting runbooks, and incident response protocols
> for a 4-person data engineering team managing 5 critical pipelines.**

---

## 📌 Overview

This document defines the operational framework for maintaining five
production data pipelines covering profit, growth, and engagement metrics.
It establishes clear ownership, fair on-call rotation, detailed runbooks
for investor-facing pipelines, and incident response procedures.

**Team Size:** 4 Data Engineers
**Pipelines Managed:** 5
**Investor-Facing Pipelines:** 3 (P0 criticality)

---

## 👥 Team

| Name | Role |
|------|------|
| Alex Chen | Senior Data Engineer |
| Jordan Martinez | Data Engineer |
| Sam Patel | Data Engineer |
| Riley Thompson | Data Engineer |

---

## 📋 Pipeline Ownership Matrix

### Business Area: Profit

#### Pipeline 1: Unit-Level Profit (Experiments)
- **Primary Owner:** Alex Chen
- **Secondary Owner:** Sam Patel
- **Business Criticality:** High — enables A/B testing and experimentation
- **SLA:** Data available by 9 AM PST daily

#### Pipeline 2: Aggregate Profit (Investors)
- **Primary Owner:** Jordan Martinez
- **Secondary Owner:** Alex Chen
- **Business Criticality:** Critical — investor reporting
- **SLA:** Data available by 8 AM PST on reporting days

---

### Business Area: Growth

#### Pipeline 3: Daily Growth (Experiments)
- **Primary Owner:** Sam Patel
- **Secondary Owner:** Riley Thompson
- **Business Criticality:** High — enables growth experiments
- **SLA:** Data available by 10 AM PST daily

#### Pipeline 4: Aggregate Growth (Investors)
- **Primary Owner:** Riley Thompson
- **Secondary Owner:** Jordan Martinez
- **Business Criticality:** Critical — investor reporting
- **SLA:** Data available by 8 AM PST on reporting days

---

### Business Area: Engagement

#### Pipeline 5: Aggregate Engagement (Investors)
- **Primary Owner:** Alex Chen
- **Secondary Owner:** Riley Thompson
- **Business Criticality:** Critical — investor reporting
- **SLA:** Data available by 8 AM PST on reporting days

---

## 📅 On-Call Rotation Schedule

### Rotation Structure
- **Frequency:** Weekly (Monday 9 AM PST to Monday 9 AM PST)
- **Type:** Primary and Secondary on-call
- **Escalation Time:** 30 minutes for P1 incidents, 2 hours for P2 incidents

### 2025 Q4 Schedule

| Week Starting | Primary On-Call | Secondary On-Call | Notes |
|--------------|----------------|-------------------|-------|
| Nov 24 | Jordan Martinez | Sam Patel | Thanksgiving week |
| Dec 1 | Sam Patel | Riley Thompson | |
| Dec 8 | Riley Thompson | Alex Chen | |
| Dec 15 | Alex Chen | Jordan Martinez | |
| Dec 22 | Jordan Martinez | Sam Patel | Holiday week |
| Dec 29 | Sam Patel | Riley Thompson | New Year's week |

### 2026 Q1 Schedule

| Week Starting | Primary On-Call | Secondary On-Call | Notes |
|--------------|----------------|-------------------|-------|
| Jan 5 | Riley Thompson | Alex Chen | |
| Jan 12 | Alex Chen | Jordan Martinez | MLK Day (Jan 19) |
| Jan 19 | Jordan Martinez | Sam Patel | |
| Jan 26 | Sam Patel | Riley Thompson | |
| Feb 2 | Riley Thompson | Alex Chen | |
| Feb 9 | Alex Chen | Jordan Martinez | |
| Feb 16 | Jordan Martinez | Sam Patel | Presidents Day (Feb 16) |
| Feb 23 | Sam Patel | Riley Thompson | |

### Holiday Coverage Policy

**Major Holidays (No expected production deployments):**
- Thanksgiving Day & Day After
- Christmas Eve & Christmas Day
- New Year's Eve & New Year's Day
- Memorial Day, July 4th, Labor Day

**Holiday On-Call Compensation:**
- 1.5x comp time off
- $500 holiday stipend
- Ability to swap shifts with 48-hour notice

**Holiday Rotation Rules:**
1. No engineer should be primary on-call for more than 1 major holiday per year
2. Engineers can volunteer for holiday coverage in exchange for preferred time off
3. Team lead must approve all holiday swaps 48 hours in advance

---

## 📒 Investor Reporting Runbooks

### 🔴 Runbook 1: Aggregate Profit Pipeline

**Owner:** Jordan Martinez (Primary), Alex Chen (Secondary)
**Criticality:** P0 — Investor Reporting
**Schedule:** Daily at 6 AM PST, completes by 8 AM PST
**Reporting Frequency:** Monthly (last business day) and Quarterly (earnings calls)

#### Architecture
```
Source Systems → Data Lake (S3) → Spark ETL → Snowflake → BI Dashboard
```

#### Data Sources
1. Transactional Database (Revenue data)
2. Cost Management System (COGS, operational costs)
3. Payment Gateway (Transaction fees, refunds)
4. Marketing Platform (Customer acquisition costs)

#### Potential Failure Scenarios

| Issue | Symptom | Possible Causes | Detection |
|-------|---------|----------------|-----------|
| Source System Delays | Pipeline timeout waiting for upstream data | DB maintenance overlap, API rate limiting, network issues | CloudWatch alarm when source data not available by 6:30 AM PST |
| Data Quality Anomalies | Revenue totals off by >5% vs previous day | Duplicate transactions, missing refund data, schema changes | Automated alerts to #data-quality Slack channel |
| Calculation Logic Errors | Profit margins appear incorrect | Cost allocation changes, tax errors, incorrect JOINs | Reconciliation checks against finance team |
| Infrastructure Failures | Pipeline job fails or times out | Spark resource exhaustion, Snowflake credit limits, S3 permissions | DataDog alerts on job failures |
| Report Generation Failures | Dashboard not updated by 8 AM PST | BI tool refresh failed, query timeout, cache issues | Automated dashboard health checks |
| Reconciliation Mismatches | Numbers don't match finance reports | Different cut-off times, accrual vs cash differences, timezone errors | Weekly reconciliation report flags variances >1% |

---

### 🔴 Runbook 2: Aggregate Growth Pipeline

**Owner:** Riley Thompson (Primary), Jordan Martinez (Secondary)
**Criticality:** P0 — Investor Reporting
**Schedule:** Daily at 5 AM PST, completes by 8 AM PST
**Reporting Frequency:** Monthly and Quarterly investor updates

#### Architecture
```
User Events (Kafka) → Stream Processing (Flink) → Data Warehouse → Aggregate Tables → BI Layer
```

#### Data Sources
1. User registration events
2. Product usage metrics
3. Subscription management system
4. Churn/cancellation events
5. Reactivation data

#### Potential Failure Scenarios

| Issue | Symptom | Possible Causes | Detection |
|-------|---------|----------------|-----------|
| Event Stream Lag | Real-time metrics delayed or stale | Kafka consumer lag, Flink checkpoint failures, backpressure | Kafka lag monitoring exceeds 5 minutes |
| User Deduplication Errors | Inflated user counts or growth rates | Multiple user IDs per user, bot traffic, test accounts | Sudden spikes in new user acquisition >20% day-over-day |
| Cohort Calculation Issues | Retention metrics appear inconsistent | Incorrect cohort assignment, timezone misalignment, window function errors | Retention curves show impossible patterns |
| Attribution Model Changes | Growth sources shift unexpectedly | Marketing model updated without pipeline changes, UTM parsing errors | Marketing team flags discrepancies |
| Seasonality Not Accounted For | False alarms on growth anomalies | Holiday patterns, day-of-week effects not normalized | Alert fatigue — too many false positives |
| Definition Drift | Metric definitions differ from finance/product | Active user definition changed, revenue recognition policy updated | Stakeholder confusion during investor prep |

---

### 🔴 Runbook 3: Aggregate Engagement Pipeline

**Owner:** Alex Chen (Primary), Riley Thompson (Secondary)
**Criticality:** P0 — Investor Reporting
**Schedule:** Daily at 4 AM PST, completes by 8 AM PST
**Reporting Frequency:** Monthly and Quarterly board meetings

#### Architecture
```
Product Analytics (Segment) → Event Warehouse → DBT Transformations → Metrics Layer → Looker
```

#### Data Sources
1. Web application events
2. Mobile app analytics
3. Feature usage logs
4. Session duration data
5. Content interaction events

#### Potential Failure Scenarios

| Issue | Symptom | Possible Causes | Detection |
|-------|---------|----------------|-----------|
| Event Tracking Degradation | Drop in events without usage drop | Ad blockers, SDK incompatibility, analytics outage, GDPR changes | Event volume drops >15% vs 7-day average |
| Session Calculation Errors | Session duration or count incorrect | Session timeout logic changed, bot sessions, sessionization errors | Unrealistic session durations (>24 hours or <1 second) |
| Feature Adoption Misreporting | Usage stats don't match product expectations | Feature flag changes, event naming conventions changed | Product manager escalations |
| Metric Aggregation Logic Bugs | DAU/MAU ratios appear impossible | Double-counting users, date window errors, deduplication key errors | Engagement metrics exceed 100% or show negative growth |
| Performance Degradation | Dashboard load times excessive | Aggregate tables not materialized, query optimization needed | Dashboard timeout errors |
| Data Freshness Issues | Metrics showing stale data during investor meetings | ETL failed silently, cache not invalidated, DST schedule shift | Last updated timestamp check fails |
| Engagement Metric Gaming | Sudden unexplained spike in engagement | Bot traffic, QA team activity, repeated event firing bug | Traffic source analysis shows anomalies |

---

## 🚨 Incident Response Protocol

### Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|--------------|------------|
| **P0 — Critical** | Investor pipeline failed, will miss SLA for board meeting | Immediate | Page on-call immediately |
| **P1 — High** | Experiment data unavailable, blocking active experiments | 30 minutes | Slack alert to on-call |
| **P2 — Medium** | Data quality issues or performance degradation | 2 hours | Ticket created, handled during business hours |

### Communication Plan for P0 Incidents

1. On-call engineer acknowledges within **5 minutes**
2. Create incident Slack channel: `#incident-YYYY-MM-DD-description`
3. Post status updates every **30 minutes**
4. Notify stakeholders:
   - VP of Finance
   - VP of Data
   - Investor Relations team
5. Post-mortem required within **48 hours**

---

## 🛠️ Maintenance Windows

| Type | Schedule |
|------|----------|
| Weekly Maintenance | Sundays 2–6 AM PST |
| Quarterly Deep Maintenance | First Saturday of quarter, 12 AM–8 AM PST |

**During maintenance windows:**
- Non-critical alerts suppressed
- Experimental pipelines can be offline
- Investor pipelines must have backup/historical data available

---

## 📞 Contact & Escalation

| Role | Name | Slack | Escalation Order |
|------|------|-------|-----------------|
| Senior Data Engineer | Alex Chen | @alex.chen | 1st |
| Data Engineer | Jordan Martinez | @jordan.m | 2nd |
| Data Engineer | Sam Patel | @sam.patel | 3rd |
| Data Engineer | Riley Thompson | @riley.t | 4th |
| VP of Data | Morgan Lee | @morgan.lee | 5th |

**Escalation Path:**
```
On-call Engineer → Secondary On-call → Team Lead → VP of Data → CTO
```

---

## 🎓 About This Project

This document demonstrates production-grade data pipeline operations
planning — covering ownership models, on-call fairness, runbook design,
and incident response frameworks used by data engineering teams at
scale across profit, growth, and engagement business domains.

---

## 👩‍💻 Author

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

- 🔗 [LinkedIn](https://www.linkedin.com/in/geetasa/)
- 📧 geetas0915@gmail.com
- 📍 Folsom, CA

---

## 📚 Further Reading

- [Google SRE Book — On-Call](https://sre.google/sre-book/being-on-call/)
- [PagerDuty Incident Response Guide](https://response.pagerduty.com/)
- [Runbook Best Practices](https://www.atlassian.com/incident-management/runbook)

---

⭐ **If this helped you design your own pipeline maintenance framework, please give it a star!**
