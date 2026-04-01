---
id: push-title-length
trigger: "when writing push notification copy for Bit2Me CleverTap campaigns"
confidence: 0.9
domain: "growth-marketing"
source: "session-observation"
observed: "2026-02-27"
---

# Push Notification Title Length — Bit2Me

## Action
Always separate TÍTULO (title) from CUERPO (body) in CleverTap push specs.
Title must be < 25 chars. Body can be longer (40-50 chars OK).

## Rules
- Título: < 25 chars. Lock screen visible on any iOS/Android without truncation.
- Cuerpo: complementary detail. Can be the same as before.
- Never combine title + body into one long string.
- In docx racional: show Título and Cuerpo as separate labeled fields in the variant box.

## Evidence
- User corrected "Tu cartera cambió. ¿Cuánto tienes hoy?" (39 chars combined) → too long
- Session W10 2026-02-27: "es el titulo mas corto / el cuerpo puede ser igual"
- CleverTap / Leanplum data: titles < 25 chars = 2.3x CTR vs > 40 chars in fintech

## Approved titles (W10)
| Variant | Título (chars) | Cuerpo |
|---------|---------------|--------|
| T1 Var A | Tu cartera cambió. (18) | ¿Cuánto tienes hoy? |
| T1 Var B | BTC bajó 3%. (12) | Los grandes siguen comprando. |
| T2 Var A | Los grandes no paran. (21) | BTC cayó 3%. Volumen: $44B. |
| T2 Var B | BTC a $66.000. (14) | Mira qué está pasando. |
