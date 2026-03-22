"""Quiz utilities — answer parsing and scoring."""

import re

HEDGING = re.compile(r"\b(maybe|perhaps|probably|guess|think|not sure|unsure|possibly|no idea)\b", re.IGNORECASE)
LETTERS = re.compile(r"\b([A-D])\b")


def parse_answer(text: str) -> tuple[str | None, str | None]:
    """Parse natural language answer into (primary, secondary).

    Returns (None, None) if no valid letter found.
    """
    matches = LETTERS.findall(text.upper())
    if not matches:
        return None, None
    # Deduplicate while preserving order
    seen = []
    for m in matches:
        if m not in seen:
            seen.append(m)
    primary = seen[0]
    secondary = seen[1] if len(seen) > 1 else None
    return primary, secondary


def is_uncertain(text: str, secondary: str | None) -> bool:
    return secondary is not None or bool(HEDGING.search(text))


def score_answer(primary: str, secondary: str | None, uncertain: bool, correct: str) -> float:
    correct = correct.upper()
    if primary == correct:
        return 0.5 if uncertain else 1.0
    if secondary and secondary == correct:
        return 0.25
    return 0.0
