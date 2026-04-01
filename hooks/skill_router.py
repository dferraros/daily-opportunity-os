"""
UserPromptSubmit hook: inspect user prompt and suggest the matching skill.
Prints a hint to stdout — Claude sees this as hook context.
Exits 0 always (never blocks).
"""
import json
import sys
import re


ROUTES = {
    r"\b(scout|harvest|signal|find opportunit|discover)\b": "signal-harvester",
    r"\b(venezuela|venezol|latam|latin america|ven lens)\b": "latam-venezuela-lens",
    r"\b(tam|sam|som|market size|market sizing)\b": "tam-estimator",
    r"\b(benchmark|competitor|compet|rival|analog)\b": "benchmark-mapper",
    r"\b(score|rank|scoring|weighted)\b": "opportunity-scorer",
    r"\b(notion|export|csv|database|package)\b": "notion-packager",
    r"\b(deep dive|deep-dive|full analysis|thesis)\b": "deep-dive-builder",
    r"\b(weekly|week review|this week|ritual)\b": "weekly-review",
    r"\b(customer language|pain language|reviews|complaints)\b": "customer-language-miner",
    r"\b(decision memo|memo|investment memo)\b": "decision-memo-builder",
    r"\b(pain library|pain cluster|pain mapping)\b": "pain-library-mapper",
    r"\b(validat|stage 2|test the market)\b": "validation-runner",
}


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)

        data = json.loads(raw)

        # Extract prompt text — Claude Code sends it in the "prompt" field
        prompt = data.get("prompt", "")
        if not isinstance(prompt, str):
            prompt = str(prompt)

        prompt_lower = prompt.lower()

        matched_skill = None
        for pattern, skill in ROUTES.items():
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                matched_skill = skill
                break

        if matched_skill:
            print(f"Suggested skill: /{matched_skill}")

    except Exception:
        # Never block — exit 0 regardless of any error
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
