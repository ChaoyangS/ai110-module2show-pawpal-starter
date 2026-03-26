from pawpal_system import Owner, Pet, Task, Scheduler, Frequency
from datetime import date, datetime, timedelta

# Create an Owner
owner = Owner("John Doe", 8)  # 8 hours available per day

# Create at least two Pets
pet1 = Pet("Buddy", "dog", 3, ["Needs medication twice daily"])
pet2 = Pet("Whiskers", "cat", 2)

# Add pets to the owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create tasks with different times (added out of order)
task1 = Task("Morning Walk", 30, Frequency.DAILY)  # 30 minutes
task2 = Task("Feeding", 15, Frequency.DAILY)       # 15 minutes
task3 = Task("Play Time", 45, Frequency.DAILY)     # 45 minutes
task4 = Task("Grooming", 20, Frequency.WEEKLY)    # 20 minutes
task5 = Task("Vet Check", 60, Frequency.MONTHLY)  # 60 minutes

# Add tasks to the pets (out of order by duration)
pet1.add_task(task3)  # 45 min first
pet1.add_task(task1)  # 30 min
pet1.add_task(task2)  # 15 min
pet2.add_task(task5)  # 60 min
pet2.add_task(task4)  # 20 min

# Mark some tasks as completed (with specific dates for testing)

# Define today
today = date.today()

# Mark daily task as completed today
task2.mark_complete(today)  # Feeding completed today

# Mark weekly task as completed today (assuming today is Monday for weekly tasks)
task4.mark_complete(today)  # Grooming completed today

# Create a Scheduler
scheduler = Scheduler(owner)

print(f"\nBefore generating plan - Task status:")
print(f"Feeding (daily): completed={task2.completion_status}, next_due={task2.next_due_date}")
print(f"Grooming (weekly): completed={task4.completion_status}, next_due={task4.next_due_date}")

# Generate today's schedule
plan = scheduler.generate_daily_plan(today)

# Print "Today's Schedule" to the terminal
print("\nToday's Schedule:")
print(plan.display_plan())

# Test what happens tomorrow for daily tasks
tomorrow = today + timedelta(days=1)
print(f"\nTomorrow's ({tomorrow}) due tasks:")
tomorrow_due = scheduler.get_due_tasks(tomorrow)
for task in tomorrow_due:
    print(f"  - {task.description} ({task.frequency.value}) - next due: {task.next_due_date}")

# Test next Monday for weekly tasks
next_monday = today + timedelta(days=(7 - today.weekday()))
print(f"\nNext Monday's ({next_monday}) due tasks:")
monday_due = scheduler.get_due_tasks(next_monday)
for task in monday_due:
    print(f"  - {task.description} ({task.frequency.value}) - next due: {task.next_due_date}")

print("\n" + "="*50)
print("DEMONSTRATING SORTING AND FILTERING METHODS")
print("="*50)

# Get all tasks
all_tasks = scheduler.filter_tasks()
print(f"\nAll tasks ({len(all_tasks)}):")
for task in all_tasks:
    status = f"Completed: {task.completion_status}, Next due: {task.next_due_date}"
    print(f"  - {task.description}: {task.time} min, {status}")

# Get due tasks for today
due_today = scheduler.get_due_tasks(today)
print(f"\nDue today ({len(due_today)}):")
for task in due_today:
    print(f"  - {task.description}: {task.time} min ({task.frequency.value}) - next due: {task.next_due_date}")

print("\n" + "="*60)
print("TESTING CONFLICT DETECTION")
print("="*60)

# Create a test scenario with overlapping tasks
from pawpal_system import ScheduledTask

# Create some overlapping scheduled tasks for testing
test_task1 = ScheduledTask(task1, "09:00")  # Morning Walk at 9:00
test_task2 = ScheduledTask(task3, "08:30")  # Play Time at 8:30 (overlaps with Vet Check)
test_task3 = ScheduledTask(task5, "08:00")  # Vet Check at 8:00

test_scheduled = [test_task1, test_task2, test_task3]

# Test conflict detection
conflicts = scheduler.detect_conflicts(test_scheduled)

print(f"Test scheduled tasks ({len(test_scheduled)}):")
for st in test_scheduled:
    end_time = (datetime.strptime(st.start_time, "%H:%M") + timedelta(minutes=st.task.time)).strftime("%H:%M")
    print(f"  - {st.start_time}-{end_time}: {st.task.description}")

if conflicts:
    print(f"\nDetected {len(conflicts)} conflict(s):")
    for conflict in conflicts:
        print(f"  ⚠️  {conflict}")
else:
    print("\nNo conflicts detected.")