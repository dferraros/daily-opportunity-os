# Quick Task 260331-bqs: Redesign payoneer-web as premium gastronomy marketing agency site - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning (yolo mode — all decisions made autonomously)

<domain>
## Task Boundary

Rebuild `Projects/payoneer-web/index.html` as a premium gastronomy marketing consultancy site.
Brand: Digital Artwork / Juan Ignacio De Biase Malave.
Single-file HTML + CSS + JS, zero build step, zero dependencies except Google Fonts.

</domain>

<decisions>
## Implementation Decisions

### Color scheme
- Light editorial: warm off-white `#F8F4EF` base, near-black `#111009` text, single gold accent `#B8843C`
- Rationale: high-end Madrid/European agencies (white-plate, etc.) all use light mode — it reads as luxury, not dark-mode SaaS

### Typography direction
- Display: Cormorant Garamond (keep — it's correct for gastronomy luxury)
- Body: DM Sans (keep)
- Scale: oversized editorial headlines (clamp 3.5rem–7rem), extreme tracking on labels

### Layout approach
- Full editorial magazine grid — horizontal rule separators, asymmetric splits
- Remove: grain, ambient glow blobs, radial gradients, watermarks
- Add: large whitespace, strong typographic hierarchy, section numbers like a magazine

### Competitor references to study
- conelmorrofino.com/consultoria-restaurantes-madrid/ — Spanish gastronomy consultant
- fdvconsulting.com — restaurant consulting Madrid
- wekookmarketing.com — gastronomy marketing agency
- porneat.es + suspecados.com — Juan's own brands (use visual DNA)

### Claude's Discretion
- Section order, exact copy, animation timing
- Photo placement and proportions
- Footer layout

</decisions>

<specifics>
## Specific Ideas

- Hero: huge italic serif headline over a stark horizontal layout, photo right column (full height)
- Stats bar: borderless, magazine-style with large numbers
- Services: numbered list style (01, 02, 03, 04) — no card boxes, just clean rows
- About section: pull quote large format, photo bleed
- FAQ: pure typographic accordion, no box decoration
- All 6 Payoneer fields must remain in contact + footer (Payoneer compliance requirement)

</specifics>

<canonical_refs>
## Canonical References

- Payoneer compliance: 6 fields required visible — nombre completo, empresa, teléfono, email, dirección, foto
- ui-ux-pro-max recommendation: Exaggerated Minimalism for agency landing pages
- Existing content: Projects/payoneer-web/PLAN.md (full copy + section specs)

</canonical_refs>
