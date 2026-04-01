# Estado del Mercado — Council Slide

## Objetivo
Slide semanal estandarizado para el Council de Bit2Me. Máx 1 minuto. Replicable cada semana.

## Requisitos Pablo Campos (directivos, inamovibles)
1. Fear & Greed Index (fuente: alternative.me o coinmarketcap)
2. "Qué pasa esta semana": FED, PCE, unemployment, macro events hoy → próximo martes
3. Correlación B2M con mercado: volume, nº operaciones, ticket medio
4. Mezclar mercado + impacto B2M (NO separados)
5. Máx 1 slide / 1 minuto
6. Formato estándar replicable cada semana

## Regla CRÍTICA: Datos
- NUNCA asumir datos. NUNCA usar estimaciones. 100% fuentes confirmadas.
- Los datos son SIEMPRE a 7 días (no 24h, no mensual)
- Fuentes válidas: alternative.me, Messari, Yahoo Finance, The Block, CoinGlass, CoinDesk

## Archivos del Proyecto
| Archivo | Ruta | Función |
|---------|------|---------|
| gen_gauge.py | /sessions/.../gen_gauge.py | Genera imagen gauge Fear & Greed (matplotlib) |
| build_slide_v2.js | /sessions/.../build_slide_v2.js | Build PPTX con pptxgenjs (VERSIÓN ACTUAL) |
| fear_greed_final.png | /sessions/.../fear_greed_final.png | Imagen gauge generada |
| **OUTPUT FINAL** | /mnt/Desktop/EstadoMercado_W09_B2M_v2.pptx | Slide entregado W09 |

## Cómo Regenerar el Slide (pasos exactos)
```bash
# 1. Generar gauge (actualizar value= en gen_gauge.py primero)
python3 /sessions/sharp-practical-dijkstra/gen_gauge.py
cp /sessions/sharp-practical-dijkstra/fear_greed_w09.png /sessions/sharp-practical-dijkstra/fear_greed_final.png

# 2. Build PPTX (output directo a Desktop)
NODE_PATH=/sessions/sharp-practical-dijkstra/.npm-global/lib/node_modules \
  node /sessions/sharp-practical-dijkstra/build_slide_v2.js
```

## Layout del Slide (3 columnas, 10"×5.625" LAYOUT_16x9)
- **LEFT** (x=0.18, w=3.32): Mercado Global — BTC price, Spot Vol 7D, gráfica The Block, mini cards Futuros/DEX/TVL
- **MIDDLE** (x=3.76, w=2.64): Sentimiento (Fear & Greed gauge) + "Qué pasa esta semana" (eventos macro)
- **RIGHT** (x=6.65, w=3.16): Impacto B2M — Brokerage Vol, PRO Vol, Nº Operaciones, Ticket Medio
- **BOTTOM**: Barra amarilla "LECTURA" con insight clave

## Stack Técnico
- **pptxgenjs**: npm, instalado en `/sessions/sharp-practical-dijkstra/.npm-global`
- NODE_PATH: `/sessions/sharp-practical-dijkstra/.npm-global/lib/node_modules`
- **Python matplotlib**: genera gauge semi-circular PNG
- **IMPORTANTE**: shadow objects en pptxgenjs se mutan. Usar factory function `sh()` por cada uso.

## Datos W09 (Feb 16-22, 2026 / presentado Feb 25)
| Dato | Valor | Fuente |
|------|-------|--------|
| BTC precio | $65,010 +3.04% | Messari/Yahoo Finance, 25 feb |
| Fear & Greed | 11 (Miedo Extremo) | alternative.me, 25 feb |
| Vol. Spot 7D | $436.1B ▼48.3% | Council PPTX W09 verificado |
| Brokerage B2M | 6.9M€ ▼62.95% | Council PPTX W09 verificado |
| PRO B2M | 29.7M€ ▼54.3% | Council PPTX W09 verificado |
| Futuros | ▼75% | Council PPTX W09 |
| DEX | ▼67% | Council PPTX W09 |
| TVL | ▼33% | Council PPTX W09 |
| Nº Operaciones 7D | [PENDIENTE] | Daniel → Qlik/BigQuery Gold Layer |
| Ticket Medio | [PENDIENTE] | Daniel → Qlik/BigQuery Gold Layer |

## Gráfica The Block 7DMA (W09)
Valores Daily Exchange Volume (puntos de la gráfica, aproximados de imagen):
`[35, 38, 69, 55, 48, 38, 27, 25]` — fechas Feb 3 a Feb 24
Pico: ~$69B el 9 feb. Caída a ~$25B el 24 feb.

## Eventos Macro W09 (hoy→próx martes)
| Día | Evento |
|-----|--------|
| Hoy (Feb 25) | NVDA Earnings |
| Jue Feb 26 | GDP Q4 EEUU 2ª revisión |
| Vie Feb 27 | PCE Core + PPI EEUU (1:30 PM UTC) |
| Lun Mar 2 | ISM Manufacturing |

## Fuentes Web (para cada semana)
- Fear & Greed: https://alternative.me/crypto/fear-and-greed-index/
- BTC precio: https://messari.io o Yahoo Finance (BTC-USD)
- Spot vol: https://www.theblock.co → Charts → Daily Exchange Volume
- Futuros/derivados: https://www.coinglass.com
- Macro calendar: Yahoo Finance Economic Calendar (sección US events)
- Mercado general: CoinDesk, CoinTelegraph para contexto narrativo

## Campos [UPDATE] Que Daniel Rellena Cada Semana
1. BTC precio + % cambio 7D
2. Fear & Greed value (actualizar en gen_gauge.py: línea `value = X`)
3. Spot Vol 7D + % vs semana anterior
4. Gráfica The Block 7DMA (8 puntos, fechas 7 días)
5. Futuros/DEX/TVL % cambio 7D
6. Brokerage B2M vol 7D + % (de Qlik Council dashboard)
7. PRO B2M vol 7D + % (de Qlik Council dashboard)
8. Nº Operaciones 7D (de Qlik/BigQuery Gold Layer)
9. Ticket Medio 7D (de Qlik/BigQuery Gold Layer)
10. Eventos macro semana (Yahoo Finance Economic Calendar, filtrar US events)
11. Texto LECTURA (insight principal, max 1-2 líneas)
