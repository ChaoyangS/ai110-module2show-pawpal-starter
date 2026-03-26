from pawpal_system import Owner, Pet, Task, Scheduler, Frequency
from datetime import date

# Create an Owner
owner = Owner("John Doe", 8)  # 8 hours available per day

# Create at least two Pets
pet1 = Pet("Buddy", "dog", 3, ["Needs medication twice daily"])
pet2 = Pet("Whiskers", "cat", 2)

# Add pets to the owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create at least three Tasks with different times
task1 = Task("Morning Walk", 30, Frequency.DAILY)  # 30 minutes
task2 = Task("Feeding", 15, Frequency.DAILY)       # 15 minutes
task3 = Task("Play Time", 45, Frequency.DAILY)     # 45 minutes

# Add tasks to the pets
pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

# Create a Scheduler
scheduler = Scheduler(owner)

# Generate today's schedule
today = date.today()
plan = scheduler.generate_daily_plan(today)

# Print "Today's Schedule" to the terminal
print("Today's Schedule:")
print(plan.display_plan())