# Daily Opportunity OS

A daily business intelligence system that scouts, scores, and ranks business opportunities with mandatory LATAM and Venezuela focus.

Built for Claude Code. Runs daily. Produces Notion-ready outputs.

---

## Setup (5 steps)

1. **Clone or navigate to project:**
   ```bash
   cd /path/to/daily-opportunity-os
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Bootstrap directories:**
   ```bash
   bash scripts/bootstrap.sh
   ```

4. **Load sample opportunities to test:**
   ```bash
   cp data/samples/sample_opportunities.jsonl data/opportunities/opportunities.jsonl
   PYTHONPATH=src python3 -m opportunity_os.main stats
   ```

5. **Run your first daily scout:**
   ```bash
   PYTHONPATH=src python3 -m opportunity_os.main daily --dry-run
   ```

---

## Daily Usage

```bash
# Full daily run (scout + score + reports)
PYTHONPATH=src python3 -m opportunity_os.main daily

# Dry run (no files written)
PYTHONPATH=src python3 -m opportunity_os.main daily --dry-run

# Weekly review
PYTHONPATH=src python3 -m opportunity_os.main weekly

# Deep dive on specific opportunity
PYTHONPATH=src python3 -m opportunity_os.main deep-dive opp_20260401_venezuela_0003

# Search
PYTHONPATH=src python3 -m opportunity_os.main search "venezuela fintech"

# Stats dashboard
PYTHONPATH=src python3 -m opportunity_os.main stats
```

---

## Automate Daily Run

### Option A: Claude Code Scheduled Task (recommended)
```
/schedule daily at 09:00 -- run opp-os daily
```

### Option B: Windows Task Scheduler
```
Task: DailyOpportunityOS
Trigger: Daily, 09:00
Action: python C:\path	o\daily-opportunity-os\scriptsun_daily.sh
```

### Option C: Cron (WSL/Linux)
```bash
0 9 * * 1-5 cd /path/to/daily-opportunity-os && bash scripts/run_daily.sh
```

---

## Output Files

| File | Description |
|------|-------------|
| `reports/daily/YYYY-MM-DD-daily.md` | Global daily report |
| `reports/daily/YYYY-MM-DD-venezuela.md` | Venezuela section (always present) |
| `reports/daily/YYYY-MM-DD-latam.md` | LATAM-filtered digest |
| `reports/weekly/YYYY-WNN-summary.md` | Weekly review with 4 mandatory outputs |
| `exports/notion/opportunity_database.csv` | Full database for Notion import |
| `exports/notion/daily_feed.csv` | Today's top opportunities |
| `data/opportunities/opportunities.jsonl` | Master opportunity store |

---

## Notion Import

1. Open Notion -> New database
2. Import CSV -> select `exports/notion/opportunity_database.csv`
3. Map columns: `name`, `geography`, `vertical`, `bucket`, `portfolio_lane`, `attractiveness_score`, `tam`

---

## Architecture

```
Signal intake -> Normalization -> Kill Gate -> Scoring -> Geo Lens -> Portfolio Lane -> Reports -> Notion export
```

**Engines:** `src/opportunity_os/engines/`
- `kill_gate.py` -- 7-criteria binary gate (2+ fails = kill)
- `scoring_engine.py` -- 16-dimension weighted scoring (0-10)
- `tam_engine.py` -- 4 TAM methods with geo multipliers
- `benchmark_engine.py` -- 8 archetypes + analog mapping

**Skills:** `.claude/skills/` (12 SKILL.md files)
**Agents:** `.claude/agents/` (5 specialist subagents)
**Hooks:** `hooks/` (9 event-driven automations)

---

## Venezuela Rules

Every daily run produces a Venezuela section regardless of signal volume. Venezuela opportunities:
- WTP: 0.25x US baseline
- SaaS ceiling: $3-15/month
- Primary rails: Zelle, USDT, Binance P2P
- Distribution: WhatsApp-first
- Must be classified into one of 10 structural wedge categories

---

*Built with Claude Code - opportunity-os v1.0*
