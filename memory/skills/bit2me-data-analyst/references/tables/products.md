# Product Reference — LTV, Churn, Revenue

## Product Stack
| Product | Internal Name | Revenue 2025 | Active Users | Weekly Churn | LTV | Notes |
|---------|--------------|-------------|-------------|-------------|-----|-------|
| Brokerage | Spot (renaming) | ~€18.5M | ~92,000 | 1.5% | €246 | Core product. Dominant. |
| Pro | Spot (professional) | €530,959 | ~1,000 | 2.0% | €511 | North Star: trading volume. Owner: Nicolas Contasti. |
| Earn | ERN | — | — | 1.0% | €350 | LOWEST churn. BEST retention. |
| Loan | — | — | 939 | 3.5% | €428 | Collateral: BTC/ETH/SOL/XRP. |
| Card | — | €245,420 | 4,628 | 6.74% | €15.13 | ⚠ HIGHEST churn. NOT a retention anchor. |
| Stocks | Inversiones / BTUM | €0 | — | — | — | BLOCKED by CNMV. Waitlist ready. |

## Product FM Definitions
| Product | FM Event | Notes |
|---------|---------|-------|
| Brokerage | SWAP, SELL, or PURCHASE with commission > €0.50 | |
| Pro/Spot | First executed BUY or SELL trade | |
| Earn | First Earn subscription activation | |
| Loan | First loan REQUEST (even if not approved) | |
| Card | First Card PURCHASE (not just "Add Card") | |
| B2M Token | NOT counted as FM | Explicitly excluded |

## North Star by Product
| Product | North Star | Owner |
|---------|-----------|-------|
| Brokerage | Revenue / trading volume | Juan Fornell |
| Pro/Spot | Trading volume | Nicolas Contasti |
| Earn | AUC (Assets Under Custody) | Álvaro Durán |
| Loan | Revenue from loans | Álvaro Durán |
| Card | "Crypto Assets Usage" (delta churn + LTV incremental) | Alejandro Gas |
| Stocks | TBD (blocked by CNMV) | Ayoub Ichchou |

## Card Specific Warnings
- 6.74% weekly churn = 14.8 week average lifetime = €15 LTV
- Industry benchmark: Revolut £59 ARPU, 42-48% card usage rate. Bit2Me: 0.26%.
- EU interchange cap: 0.2% (limits revenue per transaction)
- Card = retention/lock-in play, NOT revenue play at current scale
- Q1 2026 focus: LTV incremental + Delta Churn (does Card reduce churn vs non-card users?)

## Earn / ERN Specific
- Lowest weekly churn (1.0%) = 100-week lifetime
- Locked funds = strong retention signal
- Best cross-sell target after Brokerage FM
- Traceability: 50% (target: 80%). DO NOT analyze as complete.

## Loan Specific
- Collateral accepted: BTC, ETH, SOL, XRP
- C8 = 90.91% of Loan revenue. NEVER mass push.
- Traceability: 60%. BLOCKS Growth actions until ≥80%.
- Feb 26 launch: first Growth LC journey targeting Loan (email+push+in-app)
- Target: LC users who NEVER requested a loan + have eligible collateral

## Cross-Product Opportunity (from Feb 5 analysis)
- Advanced Brokerage users (non-trading): €17/user avg, 41K potential total
- Smart Holders (c6/c7): 8,800 users, high avg ticket, growing buys vs sells, €600K potential
- DCA users: 2,400 configured → only 800 actually bought (lack of funds)
- All cross-product segments require MANUAL download from Qlik (not in CleverTap)
