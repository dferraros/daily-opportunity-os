# J02 Journey System — Project

## Vision
Build the complete post-first-purchase journey system for Bit2Me users.
A Hub + Spokes architecture with 3 market variants: B2C Spain/EU, B2C LatAm, B2B.

## What we are building
- Hub J02-CORE: 5-touchpoint activation journey (S0 in-app → S0.5 alert → S1 push → S2 in-app → S3 email → S4 push)
- 8 Product Spokes: Earn, Pro, DCA, Diversify, Referidos, Card, B2M, B2B
- 3 Recovery tracks: Tipo A (warm <30d), Tipo B (cold 31-60d), Tipo C (frozen 60+d)
- J02.5 Loyalty: D+45-D+90 retention loop
- J02-LATAM: LatAm variant (WhatsApp primary, USD/inflation copy)
- J05 B2B: Separate architecture for empresa accounts
- Mermaid diagram: Full system architecture for Confluence
- Jira-ready tickets: One per touchpoint/spoke with owner + acceptance criteria

## Stack
- Documents: Word (.docx) via docx npm package
- Diagrams: Mermaid (.mmd) for Confluence native rendering
- CRM: CleverTap (Katy executes)
- Data: BigQuery (Alvaro)
- Approval: Diego (legal/copy gate)

## Success criteria
- All copy written in Spanish (no em dashes, no AI-sounding phrasing)
- Each touchpoint has: psychological principle, benchmark, A/B test spec, KPI
- B2C Spain: MiCA compliant
- B2C LatAm: WhatsApp-primary, USD framing, inflation context
- B2B: ROI/treasury tone, separate from B2C entirely
- Word doc: team-readable, Jira-structured
- Mermaid diagram: renderable in Confluence

## Data context (from Excel analysis)
- 5,182 FM users (Jan-Mar 2026)
- 74.3% convert to 2nd purchase (25.7% = 1,333 do not)
- Tipo A: 491 users, <30d without 2nd op
- Tipo B: 547 users, 31-60d without 2nd op  
- Tipo C: 295 users, 60+d without 2nd op
- D+0 conversions: 39.6% of all FM
- Dormant with balance: 72.4k users, EUR 19.5M AUC
- MMU: 23k (target 30k Mar 31)

## Key people
- Katy: CleverTap execution
- Diego: Legal/copy approval (ALL messages)
- Alvaro: BigQuery data + price_change_pct_24h event
- Daniel: Strategy owner
