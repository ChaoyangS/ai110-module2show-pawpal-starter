from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import date, datetime
from enum import Enum


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ScheduledTask:
    task: 'Task'
    start_time: str  # e.g., "09:00"


@dataclass
class Task:
    description: str
    time: int  # minutes
    frequency: Frequency
    completion_status: bool = False

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completion_status = True

    def is_due_today(self, check_date: date) -> bool:
        """Check if the task is due on the given date based on frequency."""
        if self.frequency == Frequency.DAILY:
            return True
        elif self.frequency == Frequency.WEEKLY:
            return check_date.weekday() == 0  # Monday
        elif self.frequency == Frequency.MONTHLY:
            return check_date.day == 1
        return False


@dataclass
class Pet:
    name: str
    type: str  # e.g., 'dog', 'cat'
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Get all tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completion_status]


@dataclass
class Owner:
    name: str
    available_time: int  # daily hours available
    preferences: Dict[str, Any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update the owner's preferences."""
        self.preferences.update(preferences)

    def get_available_time(self) -> int:
        """Get the owner's available daily time in hours."""
        return self.available_time


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    total_time: int = 0
    reasoning: str = ""

    def display_plan(self) -> str:
        """Display the daily plan as a formatted string."""
        plan_str = f"Daily Plan for {self.date.strftime('%Y-%m-%d')}:\n"
        for scheduled in self.scheduled_tasks:
            plan_str += f"- {scheduled.start_time}: {scheduled.task.description} ({scheduled.task.time} min)\n"
        plan_str += f"Total time: {self.total_time} minutes\n"
        plan_str += f"Reasoning: {self.reasoning}"
        return plan_str

    def add_task_to_plan(self, task: Task, time: str) -> None:
        """Add a task to the plan at the specified time."""
        scheduled = ScheduledTask(task, time)
        self.scheduled_tasks.append(scheduled)
        self.total_time += task.time

    def validate_plan(self) -> bool:
        """Validate that the plan fits within the owner's available time."""
        return self.total_time <= self.available_time * 60


class Scheduler:
    def __init__(self, owner: Owner, constraints: Dict[str, Any] = None):
        self.owner = owner
        self.constraints = constraints or {}

    def generate_daily_plan(self, plan_date: date) -> DailyPlan:
        """Generate a daily plan for the given date."""
        plan = DailyPlan(plan_date)
        available_time = self.owner.get_available_time() * 60
        tasks = self.get_due_tasks(plan_date)
        organized_tasks = self.organize_tasks(tasks)

        current_time = datetime.strptime("08:00", "%H:%M")
        reasoning_parts = []

        for task in organized_tasks:
            if plan.total_time + task.time <= available_time:
                time_str = current_time.strftime("%H:%M")
                plan.add_task_to_plan(task, time_str)
                # Properly handle time addition
                total_minutes = current_time.hour * 60 + current_time.minute + task.time
                new_hour = total_minutes // 60
                new_minute = total_minutes % 60
                current_time = current_time.replace(hour=new_hour, minute=new_minute)
            else:
                reasoning_parts.append(f"Skipped {task.description} due to time constraints")

        plan.reasoning = "; ".join(reasoning_parts) if reasoning_parts else "All due tasks scheduled"
        return plan

    def get_due_tasks(self, check_date: date) -> List[Task]:
        """Get all tasks that are due on the given date."""
        due_tasks = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.is_due_today(check_date):
                    due_tasks.append(task)
        return due_tasks

    def organize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Organize tasks by sorting them by duration descending."""
        # Simple organization: sort by time descending (longer tasks first)
        return sorted(tasks, key=lambda t: t.time, reverse=True)

    def explain_plan(self, plan: DailyPlan) -> str:
        """Get the reasoning behind the generated plan."""
        return plan.reasoning
