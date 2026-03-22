"""Leitner-box spaced repetition logic."""

from datetime import date, timedelta

# Box -> days until next review
INTERVALS = {1: 1, 2: 2, 3: 5, 4: 10, 5: 30}


def get_next_review_date(box: int) -> str:
    days = INTERVALS.get(box, 1)
    return (date.today() + timedelta(days=days)).isoformat()


def build_review_quiz(
    due_questions: list[dict], num_total: int = 5
) -> tuple[list[dict], int]:
    """Select questions for a review quiz from the due queue.

    Returns (selected_old_questions, num_new_to_generate).
    Always reserves at least 1 slot for a new question.
    Caps box-1 questions at 3 to prevent them monopolizing sessions.
    """
    if not due_questions:
        return [], num_total

    max_old = num_total - 1  # reserve 1 slot for new

    box1 = [q for q in due_questions if q["box"] == 1]
    higher = [q for q in due_questions if q["box"] > 1]

    selected: list[dict] = []

    # Take up to 3 from box 1
    selected.extend(box1[:3])

    # Fill remaining old slots from higher boxes
    remaining_old_slots = max_old - len(selected)
    if remaining_old_slots > 0:
        selected.extend(higher[:remaining_old_slots])

    # If we still have old slots and more box-1 questions, use them
    remaining_old_slots = max_old - len(selected)
    if remaining_old_slots > 0:
        selected.extend(box1[3 : 3 + remaining_old_slots])

    num_new = num_total - len(selected)
    return selected, num_new
