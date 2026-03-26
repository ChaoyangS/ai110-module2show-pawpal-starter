# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 📸 Demo

<a href="/course_images/ai110/ai110-module2show-pawpal-starter/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/ai110-module2show-pawpal-starter/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Features

### Scheduling algorithms

- **Greedy longest-first scheduling** — `organize_tasks()` sorts due tasks by duration descending before placing them, so longer commitments (walks, grooming) claim the best time slots early in the day.
- **Chronological sort** — `sort_scheduled_by_time()` re-orders the generated plan by clock time so the displayed schedule always reads 8:00 AM → 9:00 AM → … regardless of insertion order.
- **Shortest-first sort** — `sort_by_time()` provides an alternative ascending-duration view used in the task list UI.

### Recurrence engine

- **Daily recurrence** — marking a task complete advances `next_due_date` by 1 day via `timedelta`.
- **Weekly recurrence** — advances `next_due_date` by 7 days.
- **Monthly recurrence** — advances `next_due_date` by 30 days (approximate).
- Tasks skip scheduling automatically when `check_date < next_due_date`, so completed tasks stay off the plan until they are genuinely due again.

### Conflict detection

- `detect_conflicts()` performs pairwise overlap checks across all scheduled tasks and returns human-readable warning strings.
- Warnings identify both tasks by name, their overlapping time windows, and whether the conflict is within the same pet or across different pets.
- The Streamlit UI surfaces each conflict as a distinct `st.warning` card so owners can act on them individually.

### Filtering

- `filter_tasks(completed, pet_name)` queries tasks across all pets by completion state, pet name, or both combined.

### Time-constraint enforcement

- Tasks that would exceed the owner's `available_time` are skipped during plan generation and listed explicitly in the plan's `reasoning` field.

### Multi-pet support

- An owner can have multiple pets; `get_all_tasks()` aggregates tasks across all of them for unified scheduling and conflict checking.

## Smarter Scheduling

PawPal+ now includes improved planner behavior:

- Recurring tasks (`daily`, `weekly`, `monthly`) automatically update `next_due_date` using `timedelta` when marked complete.
- Node-level scheduling uses task duration sorting (longest-first) plus optional conflict detection for overlapping appointments.
- Filtering methods allow querying tasks by completion state and pet name (`filter_tasks(completed=..., pet_name=...)`).
- Sort utilities expose behavior for both task lengths (`sort_by_time`) and scheduled clock order (`sort_scheduled_by_time`).
- The plan generation is resilient: it returns warnings (not crashes) when task conflicts are detected.

## Testing PawPal+

### Running the tests

```bash
python -m pytest
```

### What the tests cover

| Area                    | Tests                                                                                                                                                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sorting correctness** | `sort_scheduled_by_time()` returns tasks in chronological order; `organize_tasks()` places the longest task first; both hold with a single-task list                                                          |
| **Recurrence logic**    | Daily tasks advance `next_due_date` by 1 day; weekly by 7 days; monthly by 30 days; calling `mark_complete()` twice advances correctly; `is_due_today()` returns `True` on the due date and `False` before it |
| **Conflict detection**  | Two tasks at the same start time are flagged with a `CONFLICT` warning; non-overlapping tasks produce no warnings; a single task never conflicts with itself                                                  |
| **Edge cases**          | A pet with no tasks returns an empty plan without crashing; tasks that exceed `available_time` are skipped and noted in `reasoning`; a full happy-path plan schedules all tasks when time allows              |

### Confidence level

**3 / 5 stars**

The core scheduling behaviors — sorting, recurrence, and conflict detection — are well-covered and working. Confidence is held back by a few known gaps:

- The duplicate `filter_tasks()` method (defined twice in `pawpal_system.py`) means only the second definition is active; the first is silently shadowed.
- Monthly recurrence uses a fixed 30-day approximation, which drifts for real calendar months.
- `available_time` is stored in hours but compared against task durations in minutes, so any mismatch in unit assumptions would cause silent scheduling errors.
- No tests yet cover the Streamlit UI layer or multi-pet conflict scenarios across different pets.
