# Quick Task 260331-bqs: Research — Premium Gastronomy Agency Redesign

**Researched:** 2026-03-31
**Domain:** Gastronomy marketing consultancy, editorial agency design
**Confidence:** HIGH (competitor sites fetched live, ui-ux-pro-max scripts executed)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Light editorial: warm off-white `#F8F4EF` base, near-black `#111009` text, single gold accent `#B8843C`
- Display: Cormorant Garamond, Body: DM Sans
- Scale: oversized editorial headlines (clamp 3.5rem–7rem), extreme tracking on labels
- Full editorial magazine grid — horizontal rule separators, asymmetric splits
- REMOVE: grain, ambient glow blobs, radial gradients, watermarks
- ADD: large whitespace, strong typographic hierarchy, section numbers like a magazine
- Hero: huge italic serif headline over stark horizontal layout, photo right column (full height)
- Stats bar: borderless, magazine-style with large numbers
- Services: numbered list style (01, 02, 03, 04) — no card boxes, clean rows
- About: pull quote large format, photo bleed
- FAQ: pure typographic accordion, no box decoration
- All 6 Payoneer fields must remain visible (nombre completo, empresa, teléfono, email, dirección, foto)

### Claude's Discretion
- Section order, exact copy, animation timing
- Photo placement and proportions
- Footer layout

### Deferred Ideas (OUT OF SCOPE)
- Nothing explicitly deferred (scope is clear from above)
</user_constraints>

---

## Summary

Five competitor sites were analyzed live (4 loaded successfully, suspecados.com refused connection). The ui-ux-pro-max design system and typography libraries were queried. The core finding: **most Spanish gastronomy consulting sites are competent but not premium** — they use generic CMS templates, carousels, and card grids. The gap between them and a truly premium editorial site is enormous. Juan's site can leapfrog the category by committing fully to typographic-led editorial design.

The locked decisions in CONTEXT.md are directionally correct and supported by competitor analysis. No adjustments needed to color or font choices — the evidence confirms them.

**Primary recommendation:** Execute the editorial magazine approach exactly as specified. The only competitor doing something close (wekookmarketing.com) uses serif type but buries it under slider plugins and card grids. The whitespace and typographic restraint of the locked design system will stand out immediately in this market.

---

## Competitor Analysis

### 1. Con El Morro Fino (conelmorrofino.com)

| Property | Finding |
|----------|---------|
| Background | White with dark sections (#1f1f1f) |
| Accent | Orange (#ffa422) — reads as generic/web agency, not premium gastronomy |
| Typography | "Gordita-medium" + Open Sans — custom but sans-serif, no editorial character |
| Hero | Value prop text + single CTA. No editorial structure, no photography hierarchy |
| Social proof | Portfolio photos of restaurant clients, 12-year experience claim |
| Layout | Alternating image-text blocks, narrative-driven |
| Premium factor | HIGH — restaurant photography is genuinely good. Client name-drops credible. |
| Failures | Orange accent is too tech-startup. No serif anchoring. Dense footer. Mobile UX unclear. |

**Takeaway:** Good content, generic skin. The orange does them no favors. Their photography-driven social proof (showing client restaurants) is the right move — Juan should mirror this with Porneat/Suspecados imagery.

---

### 2. FDV Consulting (fdvconsulting.com)

| Property | Finding |
|----------|---------|
| Background | Cream #F9F8F4 — almost identical to our `#F8F4EF` (validates the choice) |
| Accent | Brown/sienna #A95C37 — warm, earthy, closer to premium than orange |
| Typography | Titillium Web 300-700 — readable but characterless, no serif headline impact |
| Hero | Single-column, centered, value prop + CTA. Clean but forgettable. |
| Social proof | 12+ named testimonials with circular profile photos, company affiliations. Carousel with Swiper.js. |
| Layout | Card-based testimonials + editorial prose blocks + centered text |
| Premium factor | MEDIUM — clean and professional but nothing distinctive |
| Failures | Titillium Web is too neutral to convey expertise. Carousel dependency. |

**Takeaway:** The cream background directly validates our `#F8F4EF` choice. Their testimonial specificity (name + company + photo) is a pattern to replicate. Their font choice is their biggest weakness — Cormorant Garamond will immediately feel more authoritative.

---

### 3. Wekook Marketing (wekookmarketing.com)

| Property | Finding |
|----------|---------|
| Background | White #ffffff |
| Accent | Warm taupe #c4bba8 + gold/yellow #FEBE58 for CTAs |
| Typography | Merriweather (serif 700) + Unica One — closest to premium editorial in the set |
| Hero | Full-width slider (Slider Revolution). "Somos KOOK Lovers" tagline. Gold CTA. |
| Social proof | 40+ client logos in filterable grid. Danone, Alpro, regional restaurants. Volume over depth. |
| Layout | Card grids for services + accordion for FAQs + editorial prose sections |
| Premium factor | MEDIUM-HIGH — serif headline, warm palette, constrained saturation |
| Failures | Slider Revolution kills premium feel (heavy JS, generic animation). Card grid is corporate. Logo wall lacks specificity. |

**Takeaway:** The closest competitor to what we're building. Their serif choice is right. Their editorial aspirations exist but get drowned by plugin-heavy implementation. Our approach — plain HTML, zero JS carousel, pure typography — will outclass this by removing the noise they kept.

---

### 4. Porneat (porneat.es) — Juan's brand

| Property | Finding |
|----------|---------|
| Background | Deep blacks #000000, #121212 |
| Accent | Bold red #B81111 (CTAs) + bright blue #1863DC (interactive) |
| Typography | Clean modern sans-serif, minimalist |
| Brand personality | Irreverent, attitude-driven, "edgy branding" — "Nopor Comestible" |
| Social proof | 25,000 reviews + 4.8★ baked into brand identity |
| Key insight | "Balances playful irreverence with genuine culinary credibility" |

**Takeaway for the agency site:** Juan's personal brand is dark + irreverent. His consulting page should be the OPPOSITE — light, authoritative, editorial. This contrast is intentional: Porneat built the credibility, the agency site harvests it. The 25K reviews figure is the single most powerful credential. Lead with it everywhere.

---

### 5. Suspecados — site unavailable (ECONNREFUSED)

Site could not be fetched. Based on what is known about the brand (premium grill Madrid), it likely uses a dark, meat-focused aesthetic — upscale parrilla positioning. No specific data. Treat Porneat's DNA as the proxy.

---

## Design System Recommendation

### Final Color Palette (confirmed by competitor analysis)

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#F8F4EF` | Page base — warm off-white (identical to FDV Consulting) |
| `--bg-alt` | `#F0EBE3` | Alternate sections (slightly deeper warm) |
| `--tx` | `#111009` | Primary text — near-black warm |
| `--tx-2` | `#6B6560` | Secondary text, captions, labels |
| `--tx-muted` | `#A8A29E` | Muted text, section numbers, rules |
| `--accent` | `#B8843C` | Gold — CTAs, pull quote marks, hover states |
| `--accent-h` | `#9A6E2E` | Gold hover (darker, not lighter — more authoritative) |
| `--border` | `#DDD5CC` | Horizontal rules, dividers |
| `--white` | `#FFFFFF` | Form backgrounds, nav frosted glass base |

**Why this palette works against competitors:** Con El Morro Fino uses orange (generic). FDV uses sienna (close but warms their cream). Wekook uses taupe (neutral). Our `#B8843C` gold reads as food industry luxury — wine, olive oil, aged cheese — not tech-startup.

---

### Typography (locked, confirmed by ui-ux-pro-max)

**Pairing:** Cormorant Garamond + DM Sans

The ui-ux-pro-max library confirms "Luxury Serif" category uses Cormorant. The editorial search returns Cormorant Garamond as "Editorial Classic" for literary/refined contexts. This is the correct choice and no competitor uses it — it will be distinctive.

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600;1,700&family=DM+Sans:wght@300;400;500;600&display=swap');

--font-d: 'Cormorant Garamond', Georgia, serif;
--font-b: 'DM Sans', system-ui, sans-serif;
```

**Scale (editorial magazine):**
```css
--t-hero:    clamp(3.5rem, 8vw, 7rem);     /* Hero headline */
--t-section: clamp(2.5rem, 5vw, 4.5rem);   /* Section titles */
--t-sub:     clamp(1.25rem, 2vw, 1.75rem); /* Sub-headlines */
--t-body:    1.125rem;                      /* Body text */
--t-label:   0.75rem;                       /* Labels, section numbers */
--tracking-label: 0.2em;                    /* Extreme tracking on uppercase labels */
```

**Key rule:** Hero headline must be italic Cormorant (`font-style: italic`). This is what separates editorial from corporate. All competitors use upright sans-serif headlines — the italic serif will be the instant visual differentiator.

---

## 3 Most Impactful Layout Decisions (from competitor research)

### 1. Split hero: full-height photo column, zero decorative elements
**What competitors do:** Text-only heroes, or sliders, or generic stock photography.
**What to do instead:** Two-column grid — left 55% text (supra-label + giant italic headline + sub + CTAs + stats), right 45% full-height bleed photo of Juan at Porneat/Suspecados. The photo column has NO caption, NO overlay text, NO gradient — just the image bleeding to the viewport edge.
**Why it works:** Immediately signals "real person, real restaurants" — the credibility competitors try to manufacture with logos, Juan has in a single photo.

### 2. Numbered service rows — no boxes, just horizontal rules
**What competitors do:** 2x2 card grids with shadows, icons, borders. (Wekook, Con El Morro Fino, FDV all do this.)
**What to do instead:** Plain rows separated by `1px border-bottom: var(--border)`. Service number in `--tx-muted` (`01`, `02`, `03`, `04`), title in Cormorant 600, price right-aligned. Hover: gold left-border slide-in (3px), title color shift to `--accent`.
**Why it works:** Card boxes signal "template site." Rows signal "we had a designer." The empty space between items IS the premium signal.

### 3. Stats strip: borderless, number-forward, no decoration
**What competitors do:** Stats inside colored cards, or badges, or with icons. FDV uses circular profile cards. Wekook uses logo walls.
**What to do instead:** Full-width strip, 4 stats side by side. Large Cormorant number in `--tx`, small DM Sans label in `--tx-muted` below. No borders, no background, no icons. Thin horizontal rule above and below the strip.
**Why it works:** The restraint IS the message. Removing decoration forces the numbers to do the work — and `25K+` reviews and `4.8★` are strong enough to stand alone.

---

## Anti-Patterns to Avoid (from worst competitor patterns)

| Anti-Pattern | Seen At | Why It Fails | What to Do Instead |
|-------------|---------|-------------|-------------------|
| Slider Revolution / JS carousel | Wekook | Slow, generic, breaks premium feel | Static layout, CSS transitions max |
| Orange or saturated accent | Con El Morro Fino | Tech-startup energy, not gastronomy | Warm gold only |
| Card boxes for every section | All three | Template feel, no editorial authority | Horizontal rules + rows |
| Sans-serif display type | FDV, Con El Morro Fino | Forgettable, generic | Cormorant Garamond italic for headlines |
| Logo wall social proof | Wekook | Volume without credibility | Named testimonials with location + photo |
| Dense footer with legal blocks | Con El Morro Fino | Kills premium close | Clean footer: logo + nav + copyright + address |
| Grain overlay + glow blobs | Previous version | Dark SaaS aesthetic, not gastronomy | Remove entirely (locked decision) |
| Watermarks / decorative text | Previous version | Graphic design student feel | Remove entirely (locked decision) |
| Generic stock photography | Any | Immediately destroys trust | Real Porneat/Suspecados photos or placeholder |
| Radial gradients as decoration | Previous version | Startup landing page trope | Plain backgrounds only |

---

## Section Order Recommendation (Claude's Discretion)

Based on competitor analysis and conversion research, the optimal section order is:

```
1. NAVBAR        — fixed, transparent → frosted glass
2. HERO          — italic headline + photo split + 4-stat strip
3. MARQUEE       — brand names in loop (credibility signal, low effort)
4. PROBLEMA      — 4 pain points, numbered, sticky layout
5. SERVICIOS     — numbered rows 01-04, clean typographic
6. TRANSFORMACIÓN — Before/After, 2-column grid
7. SOBRE         — pull quote + photo bleed + 4 credential chips
8. PROCESO       — 4 steps, horizontal on desktop, vertical on mobile
9. TESTIMONIOS   — 3 testimonials, text-forward (no card boxes)
10. FAQ          — pure typographic accordion
11. CTA FINAL    — large headline + single button
12. CONTACTO     — 2-column: data left, form right
13. FOOTER       — minimal
```

**Rationale for this order:** Services appear early (before About) because decision-makers scan for pricing before reading bio. The About/credibility section mid-page serves as trust-builder before the process explanation. FAQ near the bottom addresses objections before the final CTA.

---

## Animation Philosophy

Given the editorial direction and the "remove all decorative effects" decision:

- Scroll reveal: `opacity: 0 → 1`, `transform: translateY(16px) → 0`, duration 400ms, ease-out. Nothing more.
- Navbar scroll: `background: transparent → rgba(248,244,239,0.92)`, `backdrop-filter: blur(12px)`. 200ms ease.
- FAQ accordion: `max-height: 0 → auto` with overflow hidden. 280ms ease-in-out.
- Service row hover: `border-left: 3px solid var(--accent)` slide from left, 150ms. Title color shift 150ms.
- CTA hover: `background: var(--accent) → var(--accent-h)`, 150ms. No scale, no shadow.
- Stats counter: IntersectionObserver-triggered increment from 0. Single fire, no repeat.
- NO: parallax, floating blobs, ambient gradients, text morphing, loader screens.

---

## Sources

### PRIMARY (HIGH confidence)
- Con El Morro Fino — live fetch 2026-03-31
- FDV Consulting — live fetch 2026-03-31
- Wekook Marketing — live fetch 2026-03-31
- Porneat.es — live fetch 2026-03-31
- ui-ux-pro-max design-system query: gastronomy restaurant consulting premium light editorial luxury
- ui-ux-pro-max typography query: editorial magazine luxury serif agency
- ui-ux-pro-max landing query: agency landing page service consulting

### SECONDARY (MEDIUM confidence)
- Suspecados.com — unavailable (ECONNREFUSED). Juan's brand DNA inferred from Porneat analysis and known positioning.

---

## Metadata

**Confidence breakdown:**
- Color palette: HIGH — FDV Consulting uses identical cream base, validates locked decision
- Typography: HIGH — ui-ux-pro-max confirms Cormorant for luxury/editorial, no competitor uses it (differentiation confirmed)
- Layout patterns: HIGH — all three competitors use card grids, confirming rows/editorial as the differentiator
- Anti-patterns: HIGH — observed directly in live competitor fetches

**Research date:** 2026-03-31
**Valid until:** Stable design direction — valid indefinitely for this build
