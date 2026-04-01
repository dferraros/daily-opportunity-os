# dbt (data build tool) Skill

**Warehouse target:** Google BigQuery
**Dialect:** BigQuery Standard SQL
**Context:** Bit2Me analytics engineering — lifecycle stages, Gold Layer, BI/dashboard marts
**Updated:** 2026-03-25

---

## 1. WHEN TO USE THIS SKILL

Invoke this skill when the task involves any of:

- Building or modifying dbt models (`.sql` files in a dbt project)
- Designing staging / intermediate / mart layers over raw BigQuery tables
- Adding dbt tests (schema tests, singular tests, custom macros)
- Setting up incremental models for daily user state snapshots
- Building the Bit2Me lifecycle stage classifier as a maintainable pipeline
- Generating dbt documentation (`dbt docs generate`)
- Translating ad-hoc BigQuery SQL into version-controlled, testable dbt models
- CI/CD for analytics (slim CI, `state:modified`)
- Any reference to "Gold Layer views V0a–V10" being productionized

Do NOT use this skill for one-off BigQuery queries, Qlik dashboard design, or CleverTap configuration.

---

## 2. CORE CONCEPTS

### Models
A model is a single `.sql` file that defines a transformation. dbt compiles it and materializes it in BigQuery as a table, view, or incremental table.

```sql
-- models/marts/lifecycle/user_lifecycle_stage.sql
{{ config(materialized='table') }}

SELECT
  user_id,
  lifecycle_stage,
  health_score,
  updated_at
FROM {{ ref('int_user_lifecycle_scored') }}
```

### Sources
Declare raw tables you do not own. Defined in YAML. dbt tracks freshness against them.

```yaml
# models/staging/bit2me/_sources.yml
sources:
  - name: bit2me_raw
    database: bit2me-prod
    schema: raw
    tables:
      - name: users
        loaded_at_field: created_at
        freshness:
          warn_after: {count: 24, period: hour}
          error_after: {count: 48, period: hour}
      - name: transactions
        loaded_at_field: transaction_date
```

Reference a source in SQL:
```sql
SELECT * FROM {{ source('bit2me_raw', 'transactions') }}
```

### Refs
Reference another dbt model. dbt builds the DAG automatically.

```sql
FROM {{ ref('stg_transactions') }}   -- references models/staging/.../stg_transactions.sql
```

### Seeds
Static CSV files committed to the repo, loaded as tables. Use for:
- Lifecycle stage definitions and thresholds
- Suppression lists (C8 whale IDs, compliance groups)
- Country/geo mappings

```
dbt seed                    -- loads all seeds
dbt seed --select c8_suppression
```

### Tests
Defined in schema YAML. Run with `dbt test`.

```yaml
models:
  - name: user_lifecycle_stage
    columns:
      - name: user_id
        tests:
          - unique
          - not_null
      - name: lifecycle_stage
        tests:
          - not_null
          - accepted_values:
              values:
                - EXCLUDED
                - REGISTERED
                - KYC
                - DEPOSITED
                - FM
                - ACTIVE
                - POWER
                - AT_RISK
                - PRE_DORMANCY
                - DORMANT_BAL
                - DORMANT_ZERO
                - REACTIVATED
                - CHURNED
```

### Macros (Jinja)
Reusable SQL logic. Stored in `macros/`. Called with `{{ macro_name(args) }}`.

```sql
-- macros/is_fm_transaction.sql
{% macro is_fm_transaction(commission_col, product_type_col) %}
  CASE
    WHEN {{ product_type_col }} = 'BROKERAGE' AND {{ commission_col }} > 0.50 THEN TRUE
    WHEN {{ product_type_col }} = 'PRO' THEN TRUE
    WHEN {{ product_type_col }} = 'LOAN' THEN TRUE
    ELSE FALSE
  END
{% endmacro %}
```

Usage:
```sql
SELECT
  transaction_id,
  {{ is_fm_transaction('commission_eur', 'product_type') }} AS is_fm
FROM {{ ref('stg_transactions') }}
```

---

## 3. PROJECT STRUCTURE

```
bit2me_dbt/
├── dbt_project.yml            # project config, materializations per layer
├── profiles.yml               # BigQuery connection (local dev only; in dbt Cloud use environments)
├── packages.yml               # dbt-utils, dbt-expectations, etc.
├── seeds/
│   ├── c8_suppression.csv
│   ├── lifecycle_stage_thresholds.csv
│   └── country_geo_mapping.csv
├── macros/
│   ├── is_fm_transaction.sql
│   ├── days_since.sql
│   └── mece_validate.sql
├── models/
│   ├── staging/
│   │   └── bit2me/
│   │       ├── _sources.yml
│   │       ├── _staging_models.yml   # schema tests for all stg_ models
│   │       ├── stg_users.sql
│   │       ├── stg_transactions.sql
│   │       ├── stg_kyc_events.sql
│   │       └── stg_deposits.sql
│   ├── intermediate/
│   │   └── lifecycle/
│   │       ├── _intermediate_models.yml
│   │       ├── int_user_fm_events.sql
│   │       ├── int_user_transaction_summary.sql
│   │       ├── int_user_health_score.sql
│   │       └── int_user_lifecycle_scored.sql
│   └── marts/
│       ├── lifecycle/
│       │   ├── _mart_models.yml
│       │   ├── user_lifecycle_stage.sql      -- V0a equivalent
│       │   ├── user_health_score_daily.sql   -- V0b equivalent
│       │   ├── segment_summary.sql           -- V1 equivalent
│       │   └── dormant_with_balance.sql      -- V3 equivalent
│       └── reporting/
│           ├── flash_report_daily.sql
│           └── ab_test_results.sql
└── tests/
    └── assert_lifecycle_mece.sql  -- singular test: no user in 2 stages
```

### dbt_project.yml — materialization strategy per layer

```yaml
name: 'bit2me_dbt'
version: '1.0.0'
config-version: 2

profile: 'bit2me'

model-paths: ["models"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
test-paths: ["tests"]

models:
  bit2me_dbt:
    staging:
      +materialized: view          # staging = always views, cheap to rebuild
      +schema: staging
    intermediate:
      +materialized: view          # intermediate = views unless expensive joins
      +schema: intermediate
    marts:
      +materialized: table         # marts = tables for BI performance
      +schema: marts
      lifecycle:
        user_lifecycle_stage:
          +materialized: incremental   # override for incremental daily snapshot
          +partition_by:
            field: snapshot_date
            data_type: date
          +cluster_by: ["lifecycle_stage", "country"]
```

---

## 4. KEY PATTERNS BY LAYER

### Staging Layer — Raw Source Cleanup

Rules:
- Rename columns to snake_case standard names
- Cast types (no implicit casts)
- Apply standard filters (excluded users, test accounts, C8 suppression)
- Add `_loaded_at` metadata column
- No business logic, no joins

```sql
-- models/staging/bit2me/stg_users.sql
{{ config(materialized='view') }}

WITH source AS (
  SELECT * FROM {{ source('bit2me_raw', 'users') }}
),

cleaned AS (
  SELECT
    CAST(id AS STRING)                  AS user_id,
    CAST(external_id AS STRING)         AS external_id,
    LOWER(TRIM(email))                  AS email,
    CAST(created_at AS TIMESTAMP)       AS registered_at,
    CAST(kyc_completed_at AS TIMESTAMP) AS kyc_completed_at,
    UPPER(TRIM(country_code))           AS country_code,
    CAST(is_banned AS BOOL)             AS is_banned,
    CAST(is_internal AS BOOL)           AS is_internal,
    CAST(is_test AS BOOL)               AS is_test,
    UPPER(TRIM(status))                 AS status,
    CURRENT_TIMESTAMP()                 AS _loaded_at
  FROM source
)

-- ALWAYS apply standard exclusions at staging
SELECT *
FROM cleaned
WHERE status = 'ENABLED'
  AND is_banned = FALSE
  AND is_internal = FALSE
  AND is_test = FALSE
```

```sql
-- models/staging/bit2me/stg_transactions.sql
{{ config(materialized='view') }}

WITH source AS (
  SELECT * FROM {{ source('bit2me_raw', 'transactions') }}
),

cleaned AS (
  SELECT
    CAST(transaction_id AS STRING)      AS transaction_id,
    CAST(user_id AS STRING)             AS user_id,
    CAST(transaction_date AS TIMESTAMP) AS transaction_at,
    DATE(transaction_date)              AS transaction_date,
    UPPER(TRIM(product_type))           AS product_type,
    UPPER(TRIM(transaction_type))       AS transaction_type,
    CAST(amount_eur AS FLOAT64)         AS amount_eur,
    CAST(commission_eur AS FLOAT64)     AS commission_eur,
    CAST(is_reversal AS BOOL)           AS is_reversal,
    CURRENT_TIMESTAMP()                 AS _loaded_at
  FROM source
  WHERE transaction_date IS NOT NULL
    AND user_id IS NOT NULL
)

SELECT * FROM cleaned
```

---

### Intermediate Layer — Business Logic and Joins

Rules:
- Reference only `stg_` models or other `int_` models via `ref()`
- This is where business rules live (FM logic, health score calculation)
- Join tables here, not in marts
- Name pattern: `int_<entity>_<transformation>.sql`

```sql
-- models/intermediate/lifecycle/int_user_fm_events.sql
{{ config(materialized='view') }}

-- Identifies each user's first FM event per the Bit2Me EMA definition
WITH transactions AS (
  SELECT * FROM {{ ref('stg_transactions') }}
  WHERE is_reversal = FALSE
),

fm_eligible AS (
  SELECT
    user_id,
    transaction_id,
    transaction_at,
    product_type,
    commission_eur,
    amount_eur,
    -- FM qualification logic (see bit2me-data-analyst skill for full definition)
    CASE
      WHEN product_type = 'BROKERAGE' AND commission_eur > 0.50 THEN TRUE
      WHEN product_type = 'PRO'       AND amount_eur > 0         THEN TRUE
      WHEN product_type = 'LOAN'      AND amount_eur > 0         THEN TRUE
      WHEN product_type = 'EARN'      AND amount_eur > 0         THEN TRUE
      ELSE FALSE
    END AS is_fm_eligible
  FROM transactions
  -- B2M token explicitly excluded
  WHERE transaction_type != 'B2M_TOKEN_PURCHASE'
),

first_fm AS (
  SELECT
    user_id,
    MIN(transaction_at) AS first_fm_at,
    DATE(MIN(transaction_at)) AS first_fm_date
  FROM fm_eligible
  WHERE is_fm_eligible = TRUE
  GROUP BY user_id
)

SELECT * FROM first_fm
```

```sql
-- models/intermediate/lifecycle/int_user_transaction_summary.sql
{{ config(materialized='view') }}

WITH transactions AS (
  SELECT * FROM {{ ref('stg_transactions') }}
  WHERE is_reversal = FALSE
),

fm_events AS (
  SELECT * FROM {{ ref('int_user_fm_events') }}
),

summary AS (
  SELECT
    t.user_id,
    COUNT(*)                                        AS total_transactions,
    COUNT(DISTINCT DATE(t.transaction_at))           AS active_days,
    MAX(t.transaction_at)                           AS last_transaction_at,
    DATE(MAX(t.transaction_at))                     AS last_transaction_date,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(t.transaction_at)), DAY) AS days_since_last_tx,
    SUM(t.commission_eur)                           AS total_commission_eur,
    SUM(t.amount_eur)                               AS total_volume_eur,
    COUNT(DISTINCT t.product_type)                  AS distinct_products_used,
    COUNTIF(DATE(t.transaction_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY)) AS tx_last_28d,
    fm.first_fm_at,
    fm.first_fm_date
  FROM transactions t
  LEFT JOIN fm_events fm USING (user_id)
  GROUP BY t.user_id, fm.first_fm_at, fm.first_fm_date
)

SELECT * FROM summary
```

---

### Mart Layer — Final Tables for BI/Dashboards

Rules:
- Reference only `int_` models (or other `mart` models for cross-domain joins)
- Optimized for query performance: materialized as tables, partitioned, clustered
- These are the Bit2Me lifecycle views V0a–V10 equivalents in dbt form
- Schema docs must be complete (description on every column)

---

## 5. LIFECYCLE-SPECIFIC PATTERNS FOR BIT2ME

### 5a. User Lifecycle Stage Classifier (V0a equivalent)

```sql
-- models/marts/lifecycle/user_lifecycle_stage.sql
{{
  config(
    materialized='incremental',
    unique_key='user_id',
    partition_by={
      'field': 'snapshot_date',
      'data_type': 'date',
      'granularity': 'day'
    },
    cluster_by=['lifecycle_stage', 'country_code'],
    on_schema_change='sync_all_columns'
  )
}}

WITH users AS (
  SELECT * FROM {{ ref('stg_users') }}
),

tx_summary AS (
  SELECT * FROM {{ ref('int_user_transaction_summary') }}
),

kyc_events AS (
  SELECT * FROM {{ ref('stg_kyc_events') }}
),

-- C8 suppression seed (loaded via dbt seed)
c8_suppression AS (
  SELECT user_id FROM {{ ref('c8_suppression') }}
),

classified AS (
  SELECT
    u.user_id,
    u.external_id,
    u.country_code,
    u.registered_at,
    k.kyc_completed_at,
    tx.first_fm_at,
    tx.last_transaction_at,
    tx.days_since_last_tx,
    tx.total_transactions,
    tx.tx_last_28d,
    tx.total_commission_eur,
    tx.distinct_products_used,

    -- 13-stage lifecycle classifier (MECE)
    CASE
      WHEN u.user_id IN (SELECT user_id FROM c8_suppression)      THEN 'EXCLUDED'
      WHEN k.kyc_completed_at IS NULL                             THEN 'REGISTERED'
      WHEN tx.first_fm_at IS NULL AND tx.total_transactions = 0   THEN 'KYC'
      -- Check deposits: user has deposited but no FM event
      WHEN tx.first_fm_at IS NULL                                 THEN 'DEPOSITED'
      -- FM users: classified by recency of last transaction
      WHEN tx.days_since_last_tx <= 28 AND tx.tx_last_28d >= 5   THEN 'POWER'
      WHEN tx.days_since_last_tx <= 28                            THEN 'ACTIVE'
      WHEN tx.days_since_last_tx BETWEEN 29 AND 60               THEN 'AT_RISK'
      WHEN tx.days_since_last_tx BETWEEN 61 AND 90               THEN 'PRE_DORMANCY'
      -- Dormant: split by whether they hold a balance
      -- NOTE: balance check requires joining balance table (add stg_balances ref)
      WHEN tx.days_since_last_tx > 90 AND tx.total_commission_eur > 0  THEN 'DORMANT_BAL'
      WHEN tx.days_since_last_tx > 90                                   THEN 'DORMANT_ZERO'
      ELSE 'FM'  -- FM with no qualifying recency bucket yet
    END AS lifecycle_stage,

    CURRENT_DATE() AS snapshot_date,
    CURRENT_TIMESTAMP() AS _classified_at

  FROM users u
  LEFT JOIN kyc_events k USING (user_id)
  LEFT JOIN tx_summary tx USING (user_id)
)

SELECT * FROM classified

{% if is_incremental() %}
  -- Only process users whose state may have changed
  WHERE user_id IN (
    SELECT DISTINCT user_id
    FROM {{ ref('stg_transactions') }}
    WHERE transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)
  )
  OR snapshot_date = CURRENT_DATE()
{% endif %}
```

### 5b. Health Score Model

```sql
-- models/intermediate/lifecycle/int_user_health_score.sql
{{ config(materialized='view') }}

-- Health Score: 100-pt composite (Recency 30 + Frequency 20 + Product 15 + Balance 20 + Engagement 15)
WITH tx AS (
  SELECT * FROM {{ ref('int_user_transaction_summary') }}
),

scored AS (
  SELECT
    user_id,

    -- Recency (30 pts): 0-30 based on days since last transaction
    CASE
      WHEN days_since_last_tx IS NULL     THEN 0
      WHEN days_since_last_tx <= 7        THEN 30
      WHEN days_since_last_tx <= 14       THEN 25
      WHEN days_since_last_tx <= 28       THEN 20
      WHEN days_since_last_tx <= 60       THEN 10
      WHEN days_since_last_tx <= 90       THEN 5
      ELSE 0
    END AS recency_score,

    -- Frequency (20 pts): based on transactions in last 28 days
    CASE
      WHEN tx_last_28d >= 10  THEN 20
      WHEN tx_last_28d >= 5   THEN 15
      WHEN tx_last_28d >= 2   THEN 10
      WHEN tx_last_28d = 1    THEN 5
      ELSE 0
    END AS frequency_score,

    -- Product diversity (15 pts): distinct products used
    CASE
      WHEN distinct_products_used >= 4 THEN 15
      WHEN distinct_products_used = 3  THEN 12
      WHEN distinct_products_used = 2  THEN 8
      WHEN distinct_products_used = 1  THEN 4
      ELSE 0
    END AS product_score,

    -- Engagement score placeholder (15 pts) — extend with CleverTap push open data
    0 AS engagement_score

  FROM tx
)

SELECT
  user_id,
  recency_score,
  frequency_score,
  product_score,
  engagement_score,
  -- Balance score must be joined separately from balance table
  (recency_score + frequency_score + product_score + engagement_score) AS health_score_partial
FROM scored
```

### 5c. Incremental Daily Snapshot Pattern

For slowly-changing snapshots (daily user state history):

```sql
{{
  config(
    materialized='incremental',
    unique_key=['user_id', 'snapshot_date'],
    partition_by={
      'field': 'snapshot_date',
      'data_type': 'date',
      'granularity': 'day'
    },
    cluster_by=['lifecycle_stage'],
    incremental_strategy='insert_overwrite'   -- BigQuery-native: replaces entire partition
  )
}}

-- When running incrementally, only build today's snapshot partition
{% if is_incremental() %}
  WHERE snapshot_date = CURRENT_DATE()
{% endif %}
```

Strategy guide for BigQuery:
- `insert_overwrite` — replaces the partition. Best for daily snapshots. Safe to re-run.
- `merge` — upserts by `unique_key`. Use when rows can be updated in same partition.
- `append` — just inserts new rows. Only if data is append-only and never updated.

### 5d. MECE Validation as a dbt Singular Test

```sql
-- tests/assert_lifecycle_mece.sql
-- Fails if any user appears in more than one lifecycle stage on the same snapshot date.
-- A non-zero result = MECE violation = pipeline bug.

SELECT
  user_id,
  snapshot_date,
  COUNT(DISTINCT lifecycle_stage) AS stage_count
FROM {{ ref('user_lifecycle_stage') }}
WHERE snapshot_date = CURRENT_DATE()
GROUP BY user_id, snapshot_date
HAVING COUNT(DISTINCT lifecycle_stage) > 1
```

```sql
-- tests/assert_no_null_lifecycle_stage.sql
-- Every classified user must have a stage. No NULLs allowed.

SELECT user_id
FROM {{ ref('user_lifecycle_stage') }}
WHERE lifecycle_stage IS NULL
  AND snapshot_date = CURRENT_DATE()
```

### 5e. Schema YAML with Full Docs

```yaml
# models/marts/lifecycle/_mart_models.yml
version: 2

models:
  - name: user_lifecycle_stage
    description: >
      Daily snapshot of each user's lifecycle stage (13-stage model).
      Partitioned by snapshot_date, clustered by lifecycle_stage and country_code.
      Equivalent to BigQuery Gold Layer view V0a. C8 whales classified as EXCLUDED.
    tests:
      - dbt_utils.expression_is_true:
          expression: "snapshot_date = CURRENT_DATE()"
          name: assert_today_partition_exists
    columns:
      - name: user_id
        description: Internal UUID. Primary key.
        tests:
          - not_null
          - unique
      - name: lifecycle_stage
        description: >
          MECE lifecycle classification. One of: EXCLUDED, REGISTERED, KYC,
          DEPOSITED, FM, ACTIVE, POWER, AT_RISK, PRE_DORMANCY, DORMANT_BAL,
          DORMANT_ZERO, REACTIVATED, CHURNED.
        tests:
          - not_null
          - accepted_values:
              values: [EXCLUDED, REGISTERED, KYC, DEPOSITED, FM, ACTIVE, POWER,
                       AT_RISK, PRE_DORMANCY, DORMANT_BAL, DORMANT_ZERO,
                       REACTIVATED, CHURNED]
      - name: snapshot_date
        description: Date this classification was computed. Used as partition key.
        tests:
          - not_null
      - name: health_score
        description: >
          100-pt composite score: Recency(30) + Frequency(20) + Product(15) +
          Balance(20) + Engagement(15).
      - name: days_since_last_tx
        description: Calendar days between last transaction and snapshot_date.
      - name: country_code
        description: ISO 3166-1 alpha-2. Cluster key for geo-filtered queries.
```

---

## 6. BIGQUERY-SPECIFIC CONFIGURATIONS

### project.dataset.table Syntax

In dbt for BigQuery, the three-part name maps to:
- `project` = GCP project ID (e.g., `bit2me-prod`)
- `dataset` = BigQuery dataset / dbt schema (e.g., `marts`, `staging`)
- `table` = model name

dbt resolves this automatically via `profiles.yml` + `dbt_project.yml` schema overrides. Never hardcode `project.dataset.table` in model SQL — use `{{ ref() }}` or `{{ source() }}` instead.

### Partitioning

```yaml
# In model config block
partition_by:
  field: snapshot_date    # DATE column
  data_type: date
  granularity: day        # day | month | year
```

Best practice: always filter on the partition column in downstream queries.

```sql
-- Good: BigQuery prunes partitions
WHERE snapshot_date = CURRENT_DATE()

-- Bad: full table scan
WHERE DATE(_classified_at) = CURRENT_DATE()
```

### Clustering

```yaml
cluster_by: ["lifecycle_stage", "country_code"]
```

Cluster on columns that appear most frequently in `WHERE` and `GROUP BY`. For lifecycle models: `lifecycle_stage`, `country_code`, `user_id`.

### BigQuery Optimizations in dbt

```sql
-- Use DATE_DIFF instead of DATEDIFF (BigQuery syntax)
DATE_DIFF(CURRENT_DATE(), last_transaction_date, DAY)

-- Use COUNTIF instead of COUNT(CASE WHEN ...)
COUNTIF(transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY))

-- Use APPROX_COUNT_DISTINCT for large cardinality estimates
APPROX_COUNT_DISTINCT(user_id)

-- Avoid SELECT * in intermediate models — list columns explicitly
```

### profiles.yml (local dev only — never commit credentials)

```yaml
# ~/.dbt/profiles.yml
bit2me:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth                 # uses gcloud auth application-default login
      project: bit2me-dev           # dev project, not prod
      dataset: dbt_danielf          # personal dev schema
      threads: 4
      timeout_seconds: 300
      location: EU
    prod:
      type: bigquery
      method: service-account
      project: bit2me-prod
      dataset: marts
      keyfile: /secrets/dbt-sa.json
      threads: 8
      timeout_seconds: 600
      location: EU
```

---

## 7. CI/CD — dbt Cloud vs dbt Core

### dbt Core (self-hosted)
Run via CLI or orchestrated by Airflow/Cloud Composer/Cloud Run.

```bash
# Full run
dbt run --target prod

# Specific model + all downstream
dbt run --select user_lifecycle_stage+

# Specific model + all upstream
dbt run --select +user_lifecycle_stage

# Full DAG for a subdirectory
dbt run --select marts/lifecycle/

# With variables
dbt run --vars '{"snapshot_date": "2026-03-25"}'
```

### dbt Cloud
Managed SaaS. Handles scheduling, CI/CD, docs hosting.

Recommended job structure for Bit2Me:
- **Daily run** (06:00 CET): `dbt run --select marts/lifecycle/ --target prod`
- **Daily test** (06:30 CET): `dbt test --select marts/lifecycle/ --target prod`
- **Docs refresh** (weekly): `dbt docs generate && dbt docs serve`

### Slim CI — Only Build What Changed

Slim CI runs only models changed in a PR, plus their downstream dependencies. Requires dbt Cloud or a state artifact from the last production run.

```bash
# In CI pipeline (e.g., GitHub Actions)
dbt run --select state:modified+ --defer --state ./prod-artifacts/

# state:modified  = models whose SQL changed
# +               = all downstream models that depend on changed models
# --defer         = use prod tables for unchanged upstream models (no full rebuild)
# --state         = path to prod manifest.json artifact
```

GitHub Actions pattern:
```yaml
- name: dbt CI slim run
  run: |
    dbt deps
    dbt run --select state:modified+ --defer --state s3://bit2me-dbt-artifacts/prod/
    dbt test --select state:modified+
```

---

## 8. COMMON COMMANDS

```bash
# Install dependencies (dbt-bigquery, dbt-utils)
dbt deps

# Compile SQL without running (useful for reviewing generated SQL)
dbt compile --select user_lifecycle_stage

# Run all models
dbt run

# Run specific model
dbt run --select stg_users

# Run a model + all downstream
dbt run --select stg_transactions+

# Run all models in a folder
dbt run --select staging/bit2me/

# Run all tests
dbt test

# Run tests for specific model
dbt test --select user_lifecycle_stage

# Run only schema tests (not singular tests)
dbt test --select test_type:generic

# Load seeds
dbt seed

# Generate + view documentation
dbt docs generate
dbt docs serve       # opens localhost:8080 with full DAG lineage

# Check source freshness
dbt source freshness

# Debug connection
dbt debug

# Show compiled SQL for a model (without running)
dbt compile --select user_lifecycle_stage
cat target/compiled/bit2me_dbt/models/marts/lifecycle/user_lifecycle_stage.sql

# List all models in DAG order
dbt ls --select +user_lifecycle_stage --output path
```

---

## 9. PACKAGES TO INSTALL

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0", "<2.0.0"]
    # Provides: surrogate_key, date_spine, expression_is_true, pivot, unpivot

  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
    # Provides: expect_column_values_to_be_between, expect_table_row_count_to_be_between

  - package: dbt-labs/audit_helper
    version: [">=0.9.0", "<0.10.0"]
    # Provides: compare_relations — useful for validating Gold Layer migration
```

Useful macros from `dbt_utils`:

```sql
-- Generate surrogate key (when no natural PK exists)
{{ dbt_utils.generate_surrogate_key(['user_id', 'snapshot_date']) }} AS row_id

-- Date spine (generate one row per day for a date range)
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2023-01-01' as date)",
    end_date="current_date()"
) }}

-- Safe divide (avoids division by zero)
{{ dbt_utils.safe_divide('numerator', 'denominator') }}
```

---

## 10. MIGRATION PATTERN — AD-HOC SQL TO DBT

When converting an existing BigQuery query (e.g., from a Qlik analyst or a Gold Layer view) to a dbt model:

1. Paste the query into `models/staging/` or `models/intermediate/` as appropriate
2. Replace hardcoded `project.dataset.table` references with `{{ source() }}` or `{{ ref() }}`
3. Extract hardcoded thresholds (e.g., recency cutoffs) into variables or seeds
4. Add `{{ config(...) }}` block at the top
5. Write schema YAML with tests for all output columns
6. Run `dbt compile` to verify SQL compiles correctly
7. Run `dbt run --select <model_name>` in dev schema
8. Compare row counts against original query: `dbt-labs/audit_helper` `compare_relations`
9. Run `dbt test --select <model_name>`
10. Commit and open PR

---

## 11. GOTCHAS AND ANTI-PATTERNS

| Anti-pattern | Correct approach |
|---|---|
| Hardcoding `bit2me-prod.raw.users` in model SQL | Use `{{ source('bit2me_raw', 'users') }}` |
| Joining tables in staging models | Staging = one source table only. Joins belong in `int_` |
| Using `SELECT *` in mart models | Explicit column list — prevents schema drift breaking dashboards |
| Running `dbt run` on prod without testing in dev first | Always run in dev schema first (`--target dev`) |
| Putting business logic in staging | Staging = rename + cast + filter only. Logic goes in intermediate |
| Incremental model without `unique_key` | Always set `unique_key` to enable upserts on re-runs |
| Not partitioning large tables | Any table >100M rows or queried by date must be partitioned |
| Skipping `dbt test` in CI | Tests must run on every PR. Untested models will silently corrupt dashboards |
| Committing `profiles.yml` with credentials | `profiles.yml` is local only. Use env vars or dbt Cloud environments for prod secrets |
| Not filtering on partition column in WHERE | Always filter `WHERE snapshot_date = X` to avoid full scans |
