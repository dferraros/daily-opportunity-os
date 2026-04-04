import sys, json
sys.path.insert(0, 'src')
from opportunity_os.storage import read_all_opportunities

# All unique notion pages (most recent per title, prefer 338adfa8 = Apr 4)
RAW_PAGES = [
    # SaaS / product
    ("Vertical SaaS OS for Informal LATAM Retail SMBs", "338adfa8-5ce2-81c9-8b4a-f82b888202ec", "17:21"),
    ("Spanish SMB Payroll Compliance SaaS", "338adfa8-5ce2-8165-96c4-fbc7466bfb12", "17:32"),
    ("Colombian Vertical SaaS for Financial Services Ops", "338adfa8-5ce2-8183-a5fa-ddd7fb6c7117", "17:32"),
    ("B2B Payment Reconciliation SaaS", "338adfa8-5ce2-81ee-a93c-c16cf417946a", "17:21"),
    ("Vertical SaaS for Construction Site Operations", "338adfa8-5ce2-81e2-aa01-f01e5efdd33e", "17:32"),
    ("ESG Compliance SaaS for Mid-Market", "338adfa8-5ce2-819e-8132-ca9d141cbb3d", "17:21"),
    ("WhatsApp Commerce Order Management SaaS for Colombian SMBs", "338adfa8-5ce2-8125-8416-c4ccc409f8e3", "17:32"),
    ("Venezuelan Creator Monetization Platform", "338adfa8-5ce2-8151-9006-cce663a5af4b", "17:32"),
    ("Embedded Credit for Informal LATAM SMBs via SaaS", "338adfa8-5ce2-812b-951d-cc6bbe99aa83", "17:21"),
    ("SMB Talent Management SaaS - HR for 10-200 Employee Companies", "338adfa8-5ce2-8112-ad5e-ca46c6bd0ef9", "17:24"),
    ("E-Invoicing Compliance SaaS for Mandatory LATAM Regulations", "338adfa8-5ce2-8100-9548-fedc8c5f31bb", "17:21"),
    ("AI-Native Vertical SaaS - Industry-Specific AI Replacing Legacy Workflows", "338adfa8-5ce2-81d0-a4d2-fb10f67daca3", "17:24"),
    ("B2B Supply Chain Coordination SaaS for Venezuelan Businesses", "338adfa8-5ce2-8140-a029-f4cb4ad0a2a0", "17:32"),
    # Payments
    ("Venezuelan Freelancer Cross-Border Payment Stack", "338adfa8-5ce2-81dc-87f9-fa1dd17993b3", "17:21"),
    ("USDT Payment Collection Tool for Venezuelan Informal SMBs", "338adfa8-5ce2-817c-b551-f5d773043503", "17:32"),
    ("USDT Merchant Payment Rails and Accounting for Venezuelan Commerce", "338adfa8-5ce2-8166-b60d-c22a3422e414", "17:21"),
    ("Venezuelan Gig Worker USDT Payment and Cash-Out Network", "338adfa8-5ce2-814e-b8c9-e9eaeea8c1ee", "17:32"),
    ("RegTech and AML Compliance Automation for LATAM Fintechs", "338adfa8-5ce2-81f6-a4e3-d981d9c5e342", "17:24"),
    ("Fintech Gender Gap - Women-First Financial Products in Emerging Markets", "338adfa8-5ce2-8141-84ea-eb4a2a95b9b8", "17:24"),
    ("Diaspora-to-Venezuela Payroll and Contractor Management Tool", "338adfa8-5ce2-81f3-9f13-c212bc728bf1", "17:21"),
    ("Cross-Border USDT B2B Payment Rails for LATAM Importers", "338adfa8-5ce2-8122-a2c1-f634df84d4af", "17:32"),
    ("B2B Cross-Border Payment Rails Gap", "338adfa8-5ce2-817c-850f-e609705979d7", "17:24"),
    ("Colombia Open Finance Data Aggregation Layer", "338adfa8-5ce2-8155-a0b9-d6581176ba8b", "17:24"),
    ("LATAM B2B Stablecoin Settlement with Accounting Integration", "338adfa8-5ce2-8149-818b-c318484c91eb", "17:21"),
    ("USDT Accounting Tool for Venezuelan Informal SMBs", "338adfa8-5ce2-81cd-bb02-efe3f53583cf", "17:21"),
    ("Venezuelan P2P Rate Optimization Tool for Merchants", "338adfa8-5ce2-8167-84ff-e30ff80431dc", "17:21"),
    ("Venezuelan USDT Merchant Commerce Infrastructure", "336adfa8-5ce2-8113-9203-df99081cd7b0", "09:25"),
    # Logistics
    ("AI Logistics OS for Mid-Market Distributors", "338adfa8-5ce2-8146-a550-f33245068968", "17:24"),
    ("Informal Commerce Logistics Coordinator for Venezuelan Merchants", "338adfa8-5ce2-8115-957f-e8b2916ca4ca", "17:32"),
    ("SMB Last-Mile Logistics Integration Layer", "338adfa8-5ce2-81da-af97-d72f571419ed", "17:21"),
    ("SMB On-Demand Logistics - Flexible Last-Mile for Small Merchants", "338adfa8-5ce2-81ee-8193-f6586459bdda", "17:24"),
    ("Last-Mile Distribution Management for Independent LATAM Sales Reps", "338adfa8-5ce2-81d2-af76-fa3484c4aba7", "17:24"),
    ("Cross-Border SMB Parcel Shipping - Consolidated Freight for Small Merchants", "338adfa8-5ce2-81a2-a7c8-c11a814b2dc9", "17:24"),
    ("Last-Mile Route Optimization for Regional Couriers", "338adfa8-5ce2-81f6-ac25-c5e0d7647ee5", "17:32"),
    # AI / fintech
    ("AI Relationship Manager for Community Banks", "338adfa8-5ce2-81d8-8d85-ff106e8e4421", "17:21"),
    ("AI Fraud Detection for LATAM Payment Rails", "338adfa8-5ce2-8161-9540-d1c34626f08a", "17:24"),
    ("AI WhatsApp Customer Service Bots for Venezuelan Informal Businesses", "338adfa8-5ce2-8113-bf20-cd9bb80f8d06", "17:32"),
    ("AI-First Bookkeeping Automation for Spanish Autonomos and SMBs", "338adfa8-5ce2-8132-97f0-d8ae559b32b0", "17:32"),
    ("Mexican Marketplace Embedded Finance Stack", "338adfa8-5ce2-81a3-89ca-dd4d75969bfd", "17:32"),
    # Creators
    ("Creator Monetization for Micro-Creators (Sub-$15K Earners)", "338adfa8-5ce2-81dd-9684-cc68344c3ad7", "17:24"),
    ("Skilled Trades Vertical Recruiting Platform", "338adfa8-5ce2-8103-9642-e105fa8a4dca", "17:21"),
    ("Creator Merch and Fulfillment Integration Platform", "338adfa8-5ce2-8198-aa27-efa44c881243", "17:32"),
    ("Spanish-Language Creator Monetization Stack", "338adfa8-5ce2-81c6-b735-d1d3c084439a", "17:21"),
    ("LATAM Creator Monetization via Stablecoins", "338adfa8-5ce2-8177-ad7a-fe34f24e2cc7", "17:32"),
    ("LATAM E-Invoicing Compliance Automation for SMBs", "338adfa8-5ce2-8111-a067-d1ce7e518bbd", "17:32"),
    # Remittance / diaspora
    ("Venezuelan Diaspora Remittance-to-Investment Platform", "338adfa8-5ce2-810d-81ac-c137d0ee70a6", "17:21"),
    ("Venezuelan Diaspora Remittance-to-Investment Conversion Platform", "338adfa8-5ce2-812e-a285-c3261215c63f", "17:32"),
    ("Venezuelan Remittance Corridor Digitization", "338adfa8-5ce2-8130-b0de-c71087396567", "17:21"),
    ("Stablecoin Remittance Rail for Central America and Caribbean", "338adfa8-5ce2-81c0-b8bc-d215eb3b22d6", "17:24"),
    ("Micro-Insurance for LATAM Gig Workers", "338adfa8-5ce2-8154-8aa5-e351e9d5db06", "17:24"),
    ("Gig Worker Micro-Insurance for Colombian and Venezuelan Informal Workers", "338adfa8-5ce2-8172-98ee-e98da016340a", "17:32"),
    # Credit / BNPL
    ("BNPL and Consumer Credit Access for Venezuelan Market", "338adfa8-5ce2-81e6-a458-cd7fee8a5587", "17:21"),
    ("Alternative Credit Scoring for Gig Workers", "338adfa8-5ce2-8125-81af-e7dce971ee78", "17:24"),
    ("Agri-Credit Scoring for LATAM Smallholder Farmers", "338adfa8-5ce2-81a7-87df-d1d20bda5cda", "17:24"),
    ("B2B Credit Score Infrastructure for Informal LATAM Businesses", "338adfa8-5ce2-818e-989d-fe501a6413d2", "17:32"),
    ("Venezuelan BNPL Expansion to LATAM Markets", "338adfa8-5ce2-81a1-bc31-e285f21d64c7", "17:32"),
    ("B2B BNPL for SME Supply Chain in LATAM", "338adfa8-5ce2-8194-b8aa-df337701e81a", "17:24"),
    ("LATAM SMB Embedded Credit and Financing Layer", "338adfa8-5ce2-81bd-b509-cd712f39b25c", "17:32"),
    ("MSME Credit Gap - Underserved SME Lending Infrastructure", "338adfa8-5ce2-8109-b8a2-fbaaff7e732c", "17:24"),
    # Commerce / inventory
    ("WhatsApp Commerce OS for Latin American SMBs", "338adfa8-5ce2-8148-ad9d-f0f2fba3b573", "17:24"),
    ("WhatsApp-Native Order Management for Venezuelan Retail SMBs", "338adfa8-5ce2-8133-a9f8-cea970f490fe", "17:21"),
    ("WhatsApp-Native Inventory Management for Venezuelan Retail", "338adfa8-5ce2-81e9-91d3-e5aed69aa787", "17:32"),
    ("Bodega Tech Stack for Venezuelan Neighborhood Stores", "338adfa8-5ce2-81d3-a3d1-ffd342d7b8cb", "17:21"),
    ("SMB Inventory and POS for Venezuelan Informal Retailers", "338adfa8-5ce2-81e4-8bb4-d42998d62a25", "17:21"),
    ("Informal Vendor Digitization - Street Vendor POS", "338adfa8-5ce2-817c-a9a4-c004dfcb7d06", "17:21"),
    ("E-Commerce Trust and Escrow Layer for Venezuelan Digital Commerce", "338adfa8-5ce2-81ee-87a0-dfba70f8c515", "17:21"),
    ("Loyalty and Rewards Infrastructure for LATAM Informal Retailers", "338adfa8-5ce2-81e6-9392-ffbfc07d328f", "17:32"),
    ("Venezuelan Necessity Entrepreneurship Infrastructure", "338adfa8-5ce2-815f-8866-e1afe16aade9", "17:21"),
    ("Venezuelan Informal Commerce and Social Commerce OS", "338adfa8-5ce2-81d9-b693-c712341b9eec", "17:21"),
    # Other
    ("SMB Cybersecurity - Managed Security for Non-Technical Businesses", "338adfa8-5ce2-811e-87eb-ebfdbb58ce89", "17:24"),
    ("SME Expense Management for LATAM", "338adfa8-5ce2-8186-a461-de7066473391", "17:24"),
    ("Financial Forecasting Automation for SMBs", "338adfa8-5ce2-8128-94eb-e16669d12392", "17:32"),
    ("Credential Management for Non-Tech SMBs", "338adfa8-5ce2-81fc-a555-fc5a7fb60be5", "17:32"),
    ("Earned Wage Access - On-Demand Pay for Hourly Workers", "338adfa8-5ce2-8140-83b5-ce2e42abcd88", "17:24"),
    ("Venezuelan Freelancer USD Invoicing and International Collection Platform", "338adfa8-5ce2-8155-a763-ea4197ca7455", "17:32"),
    ("Real-Time Business Intelligence for Venezuelan Merchants", "338adfa8-5ce2-815f-8c83-d8cade92e3a1", "17:32"),
    ("Supply Chain Data Integration - Multi-System Unification for Mid-Market", "338adfa8-5ce2-813b-ab88-cf77da6c7a0a", "17:24"),
    ("Financial Ops Sub-Ledger - Revenue Recognition Automation for SaaS", "338adfa8-5ce2-81b8-8bed-e0d3147029c6", "17:24"),
    ("Free-to-Paid Conversion Infrastructure - Upgrade Flow Optimization Layer", "338adfa8-5ce2-810d-b201-cd1fd1901830", "17:24"),
]

notion_map = {}
for title, pid, ts in RAW_PAGES:
    if title not in notion_map or ts > notion_map[title][1]:
        notion_map[title] = (pid, ts)

opps = read_all_opportunities()

def normalize(s):
    return (s.lower().strip()
            .replace('\u2014', '-').replace('\u2013', '-')
            .replace('  ', ' ').replace(' - ', ' ')
            .replace('--', '-'))

matches = []
unmatched_local = []
for opp in opps:
    local_name = opp.get('name', '')
    pain = opp.get('pain_validation_score')
    path = opp.get('first_10_customer_path', '')
    matched_pid = None
    matched_title = None
    local_norm = normalize(local_name)

    for notion_title, (pid, ts) in notion_map.items():
        notion_norm = normalize(notion_title)
        if local_norm == notion_norm:
            matched_pid = pid
            matched_title = notion_title
            break
        if notion_norm.startswith(local_norm) or local_norm.startswith(notion_norm):
            matched_pid = pid
            matched_title = notion_title
            break

    if matched_pid:
        matches.append({
            'local_name': local_name,
            'notion_title': matched_title,
            'page_id': matched_pid,
            'pain_validation_score': pain,
            'first_10_customer_path': (path or '')[:300],
        })
    else:
        unmatched_local.append(local_name)

print(f"Matched: {len(matches)}")
print(f"Unmatched: {len(unmatched_local)}")
if unmatched_local:
    print("\n=== STILL UNMATCHED ===")
    for n in unmatched_local:
        print(f"  - {n}")

with open('scripts/notion_matches.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(matches)} matches to scripts/notion_matches.json")
