---
phase: 2
slug: taxonomy-competitive-benchmark
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | python3 stdlib assertions (no dependencies) |
| **Quick run** | `python3 C:/Users/ferra/OneDrive/Desktop/.planning/phases/02-taxonomy-competitive-benchmark/validate_phase2.py` |
| **Estimated runtime** | ~2 seconds |
| **Wave 0 required** | No |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Req IDs | Automated Command |
|---------|------|------|---------|-------------------|
| 2-01-T1 | 02-01 | 1 | TAX-01 to TAX-07 | `python3 -c "import ast; ast.parse(open('C:/Users/ferra/OneDrive/Desktop/.planning/phases/02-taxonomy-competitive-benchmark/validate_phase2.py', encoding='utf-8').read()); print('PASS: script is valid Python')"` |
| 2-01-T2 | 02-01 | 1 | TAX-01 to TAX-07 | `python3 -c "f=open('C:/Users/ferra/OneDrive/Desktop/.planning/phases/02-taxonomy-competitive-benchmark/playbook-section-trigger-taxonomy.md',encoding='utf-8').read(); [__import__('builtins').__import__('sys').exit(1) for s in ['Family A','Family B','Family C','Family D','Family E','Family F'] if s not in f]; print('PASS')"` |
| 2-02-T1 | 02-02 | 1 | TAX-08 | `python3 -c "f=open('C:/Users/ferra/OneDrive/Desktop/.planning/phases/02-taxonomy-competitive-benchmark/playbook-section-asset-universe.md',encoding='utf-8').read(); [__import__('sys').exit(1) for s in ['Wallet','Brokerage','Pro','Earn','Card','Loan','Space Center','Pay','Wealth'] if s not in f]; print('PASS')"` |
| 2-03-T1 | 02-03 | 1 | BENCH-01, BENCH-02, BENCH-03 | `python3 -c "f=open('C:/Users/ferra/OneDrive/Desktop/.planning/phases/02-taxonomy-competitive-benchmark/playbook-section-competitor-benchmark.md',encoding='utf-8').read(); [__import__('sys').exit(1) for s in ['Coinbase','Binance','Kraken','Bitpanda','Revolut','Nexo','COPY','AVOID','INNOVATE'] if s not in f]; print('PASS')"` |
| 2-04-T1 | 02-04 | 1 | COMP-01, COMP-02, COMP-03, COMP-04 | `python3 -c "f=open('C:/Users/ferra/OneDrive/Desktop/.planning/phases/02-taxonomy-competitive-benchmark/playbook-section-compliance-per-trigger.md',encoding='utf-8').read(); [__import__('sys').exit(1) for s in ['MiCA','GDPR','ePrivacy','CNMV','Diego','TRANSACTIONAL','INFORMATIONAL','MARKETING'] if s not in f]; print('PASS')"` |

---

## Sampling Windows

| Window | Tasks | Automated Coverage |
|--------|-------|--------------------|
| Wave 1, tasks 1-5 | 2-01-T1, 2-01-T2, 2-02-T1, 2-03-T1, 2-04-T1 | 5/5 (100%) |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands
- [x] No consecutive window of 3+ tasks without automated verify
- [x] Estimated feedback latency < 5s per task
- [ ] Wave 0 stubs resolved (N/A — no MISSING automated tags)
- [x] nyquist_compliant set to true
