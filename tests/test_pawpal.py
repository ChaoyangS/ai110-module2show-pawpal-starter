import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, ScheduledTask, Frequency
from datetime import date, timedelta


def test_task_completion():
    """Test that calling mark_complete() sets the next due date and resets completion status."""
    task = Task("Test Task", 30, Frequency.DAILY)
    original_next_due = task.next_due_date

    # Initially, task should not be completed
    assert task.completion_status == False

    # Mark as complete
    task.mark_complete()

    # After marking complete, completion_status should be False (ready for next occurrence)
    # but next_due_date should be updated
    assert task.completion_status == False
    assert task.next_due_date == original_next_due + timedelta(days=1)


def test_task_addition():
    """Test that adding a task to a Pet increases the pet's task count."""
    pet = Pet("Test Pet", "dog", 2)
    initial_task_count = len(pet.tasks)

    # Add a task
    task = Task("New Task", 15, Frequency.DAILY)
    pet.add_task(task)

    # Task count should have increased by 1
    assert len(pet.tasks) == initial_task_count + 1
    assert pet.tasks[-1] == task  # The added task should be the last one


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_scheduled_by_time_chronological():
    """sort_scheduled_by_time() returns ScheduledTasks in chronological order."""
    task = Task("Any", 10, Frequency.DAILY)
    unordered = [
        ScheduledTask(task, "14:00"),
        ScheduledTask(task, "08:00"),
        ScheduledTask(task, "11:30"),
    ]
    owner = Owner("Sam", available_time=8)
    scheduler = Scheduler(owner)

    result = scheduler.sort_scheduled_by_time(unordered)

    assert [st.start_time for st in result] == ["08:00", "11:30", "14:00"]


def test_organize_tasks_longest_first():
    """organize_tasks() returns tasks sorted longest-duration first."""
    tasks = [
        Task("Short", 10, Frequency.DAILY),
        Task("Long", 60, Frequency.DAILY),
        Task("Medium", 30, Frequency.DAILY),
    ]
    owner = Owner("Sam", available_time=8)
    scheduler = Scheduler(owner)

    result = scheduler.organize_tasks(tasks)

    assert [t.time for t in result] == [60, 30, 10]


def test_sort_scheduled_single_task():
    """sort_scheduled_by_time() with one task returns a list of length 1."""
    task = Task("Solo", 20, Frequency.DAILY)
    owner = Owner("Sam", available_time=8)
    scheduler = Scheduler(owner)

    result = scheduler.sort_scheduled_by_time([ScheduledTask(task, "09:00")])

    assert len(result) == 1
    assert result[0].start_time == "09:00"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_advances_one_day():
    """Marking a daily task complete sets next_due_date to the following day."""
    completion_day = date(2026, 3, 26)
    task = Task("Daily Walk", 30, Frequency.DAILY)

    task.mark_complete(completion_date=completion_day)

    assert task.next_due_date == date(2026, 3, 27)
    assert task.completion_status == False  # ready for next cycle


def test_weekly_recurrence_advances_seven_days():
    """Marking a weekly task complete sets next_due_date 7 days later."""
    completion_day = date(2026, 3, 26)
    task = Task("Weekly Bath", 45, Frequency.WEEKLY)

    task.mark_complete(completion_date=completion_day)

    assert task.next_due_date == date(2026, 4, 2)


def test_monthly_recurrence_advances_thirty_days():
    """Marking a monthly task complete sets next_due_date 30 days later."""
    completion_day = date(2026, 3, 26)
    task = Task("Vet Visit", 60, Frequency.MONTHLY)

    task.mark_complete(completion_date=completion_day)

    assert task.next_due_date == date(2026, 4, 25)


def test_mark_complete_twice_advances_correctly():
    """Calling mark_complete() twice advances next_due_date by one day each time."""
    base = date(2026, 3, 26)
    task = Task("Daily Walk", 30, Frequency.DAILY)

    task.mark_complete(completion_date=base)
    task.mark_complete(completion_date=task.next_due_date)

    assert task.next_due_date == base + timedelta(days=2)


def test_task_not_due_before_next_due_date():
    """is_due_today() returns False when check_date is before next_due_date."""
    tomorrow = date.today() + timedelta(days=1)
    task = Task("Future Task", 20, Frequency.DAILY, next_due_date=tomorrow)

    assert task.is_due_today(date.today()) == False


def test_task_due_on_next_due_date():
    """is_due_today() returns True on the exact next_due_date."""
    today = date.today()
    task = Task("Due Today", 20, Frequency.DAILY, next_due_date=today)

    assert task.is_due_today(today) == True


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_overlapping_tasks():
    """detect_conflicts() flags two tasks whose time windows overlap."""
    pet = Pet("Buddy", "dog", 3)
    task_a = Task("Walk", 60, Frequency.DAILY)
    task_b = Task("Feed", 30, Frequency.DAILY)
    pet.add_task(task_a)
    pet.add_task(task_b)

    owner = Owner("Sam", available_time=8)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    # Both start at 08:00 → they overlap
    scheduled = [
        ScheduledTask(task_a, "08:00"),
        ScheduledTask(task_b, "08:00"),
    ]
    conflicts = scheduler.detect_conflicts(scheduled)

    assert len(conflicts) == 1
    assert "CONFLICT" in conflicts[0]


def test_detect_conflicts_no_overlap():
    """detect_conflicts() returns empty list when tasks do not overlap."""
    pet = Pet("Buddy", "dog", 3)
    task_a = Task("Walk", 30, Frequency.DAILY)
    task_b = Task("Feed", 15, Frequency.DAILY)
    pet.add_task(task_a)
    pet.add_task(task_b)

    owner = Owner("Sam", available_time=8)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    # task_a ends at 08:30; task_b starts at 08:30 — no overlap
    scheduled = [
        ScheduledTask(task_a, "08:00"),
        ScheduledTask(task_b, "08:30"),
    ]
    conflicts = scheduler.detect_conflicts(scheduled)

    assert conflicts == []


def test_detect_conflicts_single_task():
    """detect_conflicts() with one task never reports a conflict."""
    pet = Pet("Whiskers", "cat", 2)
    task = Task("Feeding", 20, Frequency.DAILY)
    pet.add_task(task)

    owner = Owner("Sam", available_time=8)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts([ScheduledTask(task, "09:00")])

    assert conflicts == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_generates_empty_plan():
    """generate_daily_plan() with a pet that has no tasks returns an empty schedule."""
    pet = Pet("Nemo", "fish", 1)
    owner = Owner("Sam", available_time=8)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_daily_plan(date.today())

    assert plan.scheduled_tasks == []
    assert plan.total_time == 0


def test_task_skipped_when_exceeds_available_time():
    """Tasks that exceed available time are skipped and noted in reasoning."""
    pet = Pet("Buddy", "dog", 3)
    # 3 hours of tasks but owner only has 2 hours available
    pet.add_task(Task("Long Walk", 120, Frequency.DAILY))
    pet.add_task(Task("Grooming", 60, Frequency.DAILY))

    owner = Owner("Sam", available_time=2)  # 120 minutes
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_daily_plan(date.today())

    assert plan.total_time <= 120
    assert "Skipped" in plan.reasoning


def test_generate_plan_happy_path():
    """generate_daily_plan() schedules all due tasks when time is sufficient."""
    pet = Pet("Buddy", "dog", 3)
    pet.add_task(Task("Walk", 30, Frequency.DAILY))
    pet.add_task(Task("Feed", 15, Frequency.DAILY))

    owner = Owner("Sam", available_time=8)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_daily_plan(date.today())

    assert len(plan.scheduled_tasks) == 2
    assert plan.reasoning == "All due tasks scheduled"