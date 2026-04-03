---
id: 06-02E
wave: 2
depends_on: [06-01B, 06-01D]
files_modified:
  - src/opportunity_os/firecrawl_client.py
  - src/opportunity_os/research_executor.py
autonomous: true
---

# Plan 06-02E: Firecrawl Integration for Pain Validation

## Goal

Add optional Firecrawl web crawling to the research executor. When `FIRECRAWL_API_KEY` is set, crawl Reddit and targeted forums for pain evidence. Falls back to existing Anthropic web_search if key not set. Never breaks the pipeline.

## must_haves

- [ ] New `firecrawl_client.py` module with thin wrapper around Firecrawl API
- [ ] research_executor.py calls firecrawl for Reddit/forum pain crawling when key is available
- [ ] Crawled pain phrases stored in `exact_customer_phrases` field (max 5)
- [ ] If FIRECRAWL_API_KEY not set, falls back to existing behavior (no error)
- [ ] Firecrawl failures never break the pipeline (guarded with try/except + log_failure)

## Tasks

<task id="1">
<title>Create firecrawl_client.py thin wrapper</title>
<read_first>
- src/opportunity_os/research_executor.py (see how it reads env keys with _load_env_key(), around line 30-50)
- .env (check if FIRECRAWL_API_KEY placeholder exists)
</read_first>
<action>
Create `src/opportunity_os/firecrawl_client.py`:

```python
"""Firecrawl client -- thin wrapper for crawling Reddit/forums for pain evidence.

Reads FIRECRAWL_API_KEY from .env. If not set, all functions return None gracefully.
Uses Firecrawl /v1/scrape endpoint to extract text content from target URLs.
"""

import json
import os
import time
from typing import Optional

# Target subreddits for pain evidence crawling
PAIN_EVIDENCE_URLS = [
    "https://www.reddit.com/r/vzla/search/?q={query}&sort=new",
    "https://www.reddit.com/r/Colombia/search/?q={query}&sort=new",
    "https://www.reddit.com/r/fintech/search/?q={query}&sort=new",
]

MAX_PHRASES = 5
RATE_LIMIT_SECONDS = 2.0


def _load_firecrawl_key() -> Optional[str]:
    """Load FIRECRAWL_API_KEY from .env file or environment."""
    key = os.environ.get("FIRECRAWL_API_KEY")
    if key:
        return key
    # Try .env file
    from pathlib import Path
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        env_path = parent / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FIRECRAWL_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and val != "your_key_here":
                            return val
            break
    return None


def crawl_pain_evidence(query: str, geography: str = "global") -> Optional[list[str]]:
    """
    Crawl Reddit/forums for pain evidence phrases matching the query.

    Returns list of up to MAX_PHRASES exact customer phrases, or None if Firecrawl unavailable.
    """
    api_key = _load_firecrawl_key()
    if not api_key:
        return None

    try:
        import httpx
    except ImportError:
        return None

    phrases = []
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Filter URLs by geography
    urls = PAIN_EVIDENCE_URLS
    if geography == "venezuela":
        urls = [u for u in urls if "vzla" in u or "fintech" in u]
    elif geography in ("colombia", "latam"):
        urls = [u for u in urls if "Colombia" in u or "fintech" in u]

    for url_template in urls[:2]:  # max 2 URLs to stay within rate limits
        url = url_template.format(query=query.replace(" ", "+"))
        try:
            resp = httpx.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers=headers,
                json={"url": url, "formats": ["markdown"]},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("data", {}).get("markdown", "")
                # Extract short pain phrases (sentences with pain indicators)
                for line in content.split("\n"):
                    line = line.strip()
                    if len(line) > 20 and len(line) < 200:
                        pain_words = ["problema", "necesito", "frustrado", "dificil",
                                     "imposible", "caro", "lento", "malo", "no funciona",
                                     "pain", "struggle", "expensive", "broken", "need"]
                        if any(w in line.lower() for w in pain_words):
                            phrases.append(line[:200])
                            if len(phrases) >= MAX_PHRASES:
                                return phrases
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception:
            continue  # Individual URL failure is OK

    return phrases if phrases else None
```

Also ensure `httpx` is available -- check `pyproject.toml` dependencies. If not present, add a note that it should be added, but the code handles ImportError gracefully.
</action>
<acceptance_criteria>
- File src/opportunity_os/firecrawl_client.py exists
- grep "def crawl_pain_evidence" src/opportunity_os/firecrawl_client.py returns a match
- grep "FIRECRAWL_API_KEY" src/opportunity_os/firecrawl_client.py returns at least 2 matches
- grep "MAX_PHRASES = 5" src/opportunity_os/firecrawl_client.py returns a match
- python -c "from opportunity_os.firecrawl_client import crawl_pain_evidence; print(crawl_pain_evidence('test'))" prints None (no key set)
</acceptance_criteria>
</task>

<task id="2">
<title>Integrate firecrawl into research_executor.py</title>
<read_first>
- src/opportunity_os/research_executor.py (full file -- find where exact_customer_phrases is populated, and where the main research loop runs)
- src/opportunity_os/firecrawl_client.py (the module just created in Task 1)
</read_first>
<action>
In `src/opportunity_os/research_executor.py`, integrate Firecrawl:

1. After the existing imports, add:
   ```python
   from opportunity_os.pipeline_monitor import log_failure
   ```

2. Inside the `run_research_executor(opp)` function, AFTER the existing Anthropic web_search research completes and BEFORE setting `research_executed_at`, add:
   ```python
   # Firecrawl pain evidence enrichment (optional, guarded)
   try:
       from opportunity_os.firecrawl_client import crawl_pain_evidence
       query = opp.get("problem_statement", opp.get("name", ""))[:100]
       geo = opp.get("geography", "global")
       firecrawl_phrases = crawl_pain_evidence(query, geography=geo)
       if firecrawl_phrases:
           existing = opp.get("exact_customer_phrases") or []
           # Merge, dedupe, cap at 5
           combined = list(dict.fromkeys(existing + firecrawl_phrases))[:5]
           opp["exact_customer_phrases"] = combined
           print(f"  Firecrawl: {len(firecrawl_phrases)} pain phrases found for {opp.get('name', '')[:40]}")
   except Exception as e:
       log_failure("firecrawl_pain_evidence", e, opp_id=opp.get("id", "unknown"))
   ```

3. The key behavior: if `FIRECRAWL_API_KEY` is not set, `crawl_pain_evidence` returns None, and the block does nothing. If Firecrawl fails, `log_failure` records it but the pipeline continues.
</action>
<acceptance_criteria>
- grep "firecrawl" src/opportunity_os/research_executor.py returns at least 2 matches (import + usage)
- grep "crawl_pain_evidence" src/opportunity_os/research_executor.py returns a match
- grep "log_failure" src/opportunity_os/research_executor.py returns at least 1 match
- python -c "import ast; ast.parse(open('src/opportunity_os/research_executor.py').read()); print('syntax OK')" succeeds
</acceptance_criteria>
</task>

## Verification

```bash
cd C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os
PYTHONPATH=src uv run python -c "
from opportunity_os.firecrawl_client import crawl_pain_evidence
result = crawl_pain_evidence('payments venezuela')
print(f'Firecrawl result (no key expected): {result}')
# Should print None since no API key is set
"
```
