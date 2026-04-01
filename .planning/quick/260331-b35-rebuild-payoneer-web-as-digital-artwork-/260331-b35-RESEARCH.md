# Research: Digital Artwork Consultancy Rebuild

## Section Order (recommended)

1. **Nav bar** — sticky, minimal (logo + 1-2 links + contact anchor). Establishes identity immediately without clutter.
2. **Hero** — full-viewport. Name of firm, one-line positioning statement, single CTA ("Let's talk" or "Book a call"). NO price, NO service list. Trust comes before scope.
3. **Trust bar / credentials strip** — logos of clients, media mentions, or certifications in a single horizontal row. Appears immediately after hero fold. Fastest trust signal in B2B.
4. **Services overview** — 3-4 cards max. Name the problem each service solves, not just the deliverable. Example: "You need more reservations" → "Revenue-focused campaigns for restaurants and hospitality brands."
5. **Why us / Differentiators** — 2-3 short statements of unique method or point of view. This is where the brand voice lives.
6. **About / Founder story** — Photo of the person (critical for Payoneer compliance). 3-4 lines. Human-first. Builds trust for high-ticket B2B.
7. **Case studies / Portfolio** — 2-3 outcomes-led examples. Format: client type → challenge → result (quantified). No client names needed if confidential.
8. **Testimonials** — 2-3 short quotes. Real name + role/company. More powerful than logos alone for boutique consultancies.
9. **Process / How we work** — 3-step visual. Sets expectations, reduces friction, pre-qualifies time-wasters.
10. **CTA / Contact** — Full contact block: name, company, phone, email, address, contact form. Required for Payoneer compliance.
11. **Footer** — Legal, privacy, minimal nav repeat. Repeat name, email, phone, address.

**Why this order works:** Follows the B2B buyer psychology arc: attention → trust → relevance → proof → action. Each section answers a sequential question: Who are you? → Who else trusts you? → What do you do? → Why you? → Who is behind this? → Proof it worked? → What do others say? → How does it start? → Where do I reach you?

---

## Design Refinements

**Current palette:** bg `#0C0907`, gold `#C9964F`, cream `#EDE4D4`

**Assessment:** Solid foundation. The near-black reads as premium gastronomy (Noma, Eleven Madison Park menus). Two targeted refinements:

- **Gold:** `#C9964F` leans slightly orange on bright screens. Consider shifting to `#B8892A` (warmer, deeper) or `#C4973E` to read more "aged gold" and less "amber beer." Avoid `#FFD700` — casino register.
- **Body text:** Use `#F0E8D8` (slightly warmer than full cream) for body. Reserve `#EDE4D4` for display headlines only. Reduces eye fatigue on dark backgrounds.
- **Card depth:** `#151009` (slightly lighter than bg) creates depth for cards without adding new colors. Keeps the single-file constraint intact.
- **Texture:** Add a subtle CSS noise overlay (SVG filter or pseudo-element) at 3-5% opacity. Removes the "flat screen" feel and makes the dark background read as tactile/luxury. Zero dependencies.

**Typography (keep as-is):** Cormorant Garamond + DM Sans is a well-validated premium hospitality pairing.
- Display headings: weight 300-400, letter-spacing `-0.02em`
- Body: DM Sans weight 300-400, line-height 1.65
- Gold accents on subheadings only — not body text (too much gold reads cheap)

---

## Hero Copy Pattern

**Formula:** [What you do] + [for whom] + [outcome they care about]

**Strong patterns observed on premium B2B consultancy sites:**
- "We turn exceptional restaurants into recognizable brands."
- "Strategic marketing for the world's most ambitious hospitality businesses."
- "Your gastronomy brand, built to last." (quiet luxury — understated, confident)

**For Digital Artwork 126 LLC:**
- Lead with the outcome the client wants (more covers, more awareness, more revenue) — not the service ("we do social media")
- Never use "Welcome to" or "Specialists in" — both register as generic
- One line max above the fold. Sub-headline (DM Sans, smaller) adds specificity
- Single CTA: "Start a project" or "Let's talk" — avoid "Learn more" (implies they need convincing)

**Avoid in the hero:**
- Listing services (feels like a menu, not a consultancy)
- Vague abstract language ("crafting experiences," "igniting passion")
- Animated headline text — premium sites let typography stand still; motion is reserved for scroll transitions

---

## Credentials/Social Proof Pattern

**How premium consultancies show proof without prices or disclosing clients:**

1. **Named founder + photo** — most powerful solo trust signal. A face converts.
2. **Specific outcome language** — "Helped open 4 restaurant concepts in Miami" beats "extensive experience"
3. **Years + number** — "12 years, 40+ brands" is concrete and believable
4. **Selective logos** — 3 recognizable logos outperform 12 obscure ones
5. **One full case study** — structure: brand type → challenge → what we did → result. No client name required.
6. **Media/awards strip** — even trade press logos signal third-party validation
7. **Process as credibility** — a clear 3-step method implies expertise. Most cheap agencies have no stated process.

**Do NOT do:**
- Generic star ratings without attribution — reads as fabricated
- Testimonials without name + role (anonymous = useless)
- "Trusted by X+ clients" without any names — unverifiable

---

## Payoneer Compliance Placement

Payoneer requires a submitted website URL that demonstrates how the business operates and how customers find it. Their Business Profile review checks for real business identity. The site needs to clearly show:

- **Business/company name** — in the header (nav logo area), visible on load
- **Owner/founder name + photo** — in the About section. Face photo is strongly recommended; manual reviews look for human presence
- **Phone number** — in the Contact section and footer
- **Email address** — in the Contact section and footer
- **Physical address** — in the Contact section and footer (required for KYC address match)
- **Description of services** — Services section covers this
- **Who customers are** — implied clearly by niche (gastronomy/hospitality brands)

**Placement recommendation:**
- Put "Digital Artwork 126 LLC" in the nav header — visible on every scroll position
- About section: principal's photo + full name prominently displayed
- Footer: name, email, phone, full address (single HTML file = these appear on every page state)
- Contact section: form + all direct contact details side-by-side, not just a form alone

**Note:** Payoneer does not publish a public checklist requiring all of this on the website, but their compliance review verifies that the submitted URL shows a real, operating business. A site that looks inactive, vague, or has no contact info will fail manual review.

---

## Anti-patterns to Avoid

| Anti-pattern | Why it signals cheap/low-end |
|---|---|
| Generic stock food photography | Immediately identifiable; says "template", not boutique |
| Gold text on gold-adjacent backgrounds | Illegible and visually chaotic — gold is accent only |
| Listing 10+ services | Signals generalist, not specialist. Specialists command premium. |
| No photo of the person | Anonymous agencies lose trust for high-ticket B2B |
| Abstract hero copy ("crafting experiences") | Zero information density. Buyers bounce in 5 seconds. |
| Bullet-point-heavy service descriptions | Reads like a spec sheet, not a consultancy |
| Animated headlines/text reveals on hero | Delays value communication. Premium sites are confident, not theatrical. |
| Footer-only contact info | For Payoneer compliance AND trust, contact needs its own section |
| Overuse of gold — borders, text, backgrounds | Diluted gold is not gold. Max 2-3 elements per page. |
| No process section | Implies improvised work. Process = expertise signal. |
| Generic CTAs: "Click here", "Learn more" | Low-intent language. "Start a project" implies partnership. |
| Missing mobile optimization | Non-negotiable in 2025; Payoneer manual reviews may be on mobile |

---

## Reference Sites Found

| Site | What to study |
|---|---|
| [white-plate.com](https://www.white-plate.com/en/) | Gastronomy + hotel marketing agency Munich/London. Named principals, Michelin-star credentials, portfolio-grid structure. |
| [eatwithyoureyes.co.uk](https://www.eatwithyoureyes.co.uk/) | UK food/drink branding agency. Strong niche positioning, clean aesthetic. |
| [awwwards.com/websites/hotel-restaurant](https://www.awwwards.com/websites/hotel-restaurant/) | Curated gallery of highest-quality hotel/restaurant sites. Best source for dark aesthetic references. |
| [mediaboom.com — luxury website design](https://mediaboom.com/news/luxury-website-design/) | 50 luxury website design ideas. Color palette and typography examples. |
| [trivision.com — Quiet Luxury Branding](https://trivision.com/uncategorized/quiet-luxury-branding-trends-2025/) | Aman/Bentley/Apple quiet luxury trend analysis. Directly applicable to premium gastronomy positioning. |
| [studioandor.com — luxury design trends](https://studioandor.com/blog/luxury-website-design-trends) | Typography, texture, and color advice for luxury digital branding in 2025. |
| [ambrosemarketing.com — 7 elements of luxury web design](https://www.ambrosemarketing.com/blog/7-essential-elements-of-luxury-website-design-in-2025) | 7-element framework: visual design, UX, navigation, tech, brand message, security, sustainability. |

---

## Key Synthesis

The most important insight: premium gastronomy marketing consultancy sites succeed by doing less, not more. One strong positioning line, one face, a handful of outcomes-based proof points, and frictionless contact. The dark luxury aesthetic works when gold is used sparingly (2-3 accents max), texture is implied rather than illustrated, and white space is generous. The Payoneer compliance goal and the conversion goal are fully aligned — both require a real, human, contactable business identity to be visible and credible on the page.
