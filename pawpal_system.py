from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
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
    next_due_date: Optional[date] = None

    def __post_init__(self):
        """Initialize next_due_date if not set."""
        if self.next_due_date is None:
            self.next_due_date = date.today()

    def mark_complete(self, completion_date: Optional[date] = None) -> None:
        """Mark the task as completed and set the next due date based on frequency."""
        self.completion_status = True
        completion_date = completion_date or date.today()
        
        if self.frequency == Frequency.DAILY:
            self.next_due_date = completion_date + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            self.next_due_date = completion_date + timedelta(days=7)
        elif self.frequency == Frequency.MONTHLY:
            # Approximate monthly as 30 days for simplicity
            self.next_due_date = completion_date + timedelta(days=30)
        
        # Reset completion status for next occurrence
        self.completion_status = False

    def is_due_today(self, check_date: date) -> bool:
        """Check if the task is due on the given date."""
        return check_date >= self.next_due_date


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
        available_minutes = self.owner.get_available_time() * 60
        
        # Get and organize due tasks
        due_tasks = self.get_due_tasks(plan_date)
        if not due_tasks:
            plan.reasoning = "No tasks due today"
            return plan
            
        organized_tasks = self.organize_tasks(due_tasks)
        
        # Schedule tasks starting from 8 AM
        current_time = datetime.strptime("08:00", "%H:%M")
        skipped_tasks = []
        
        for task in organized_tasks:
            if plan.total_time + task.time <= available_minutes:
                time_str = current_time.strftime("%H:%M")
                plan.add_task_to_plan(task, time_str)
                current_time = self._add_minutes_to_time(current_time, task.time)
            else:
                skipped_tasks.append(task.description)
        
        # Build reasoning
        if skipped_tasks:
            plan.reasoning = f"Skipped {', '.join(skipped_tasks)} due to time constraints"
        else:
            plan.reasoning = "All due tasks scheduled"
        
        # Check for conflicts (optional performance optimization: only if conflicts are likely)
        if len(plan.scheduled_tasks) > 1:
            conflicts = self.detect_conflicts(plan.scheduled_tasks)
            if conflicts:
                plan.reasoning += f"; WARNINGS: {'; '.join(conflicts)}"
        
        return plan

    def _add_minutes_to_time(self, time: datetime, minutes: int) -> datetime:
        """Add minutes to a datetime object, properly handling hour and minute overflow.
        
        This helper method safely adds minutes to a time, wrapping hours correctly
        when minutes exceed 60, ensuring valid time calculations for scheduling.
        
        Args:
            time: The base datetime object to add minutes to
            minutes: Number of minutes to add (can be any positive integer)
            
        Returns:
            A new datetime object with the minutes added
            
        Example:
            >>> base_time = datetime.strptime("09:30", "%H:%M")
            >>> result = _add_minutes_to_time(base_time, 45)
            >>> result.strftime("%H:%M")  # "10:15"
        """
        total_minutes = time.hour * 60 + time.minute + minutes
        new_hour = total_minutes // 60
        new_minute = total_minutes % 60
        return time.replace(hour=new_hour, minute=new_minute)

    def get_due_tasks(self, check_date: date) -> List[Task]:
        """Get all tasks that are due on the given date using list comprehension.
        
        Iterates through all pets and their tasks, filtering for tasks that are
        due on the specified date based on their frequency and completion history.
        
        Args:
            check_date: The date to check for due tasks
            
        Returns:
            List of Task objects that are due on the given date
            
        Note:
            This method uses a concise list comprehension for better readability
            and slight performance improvement over nested loops.
        """
        return [task for pet in self.owner.pets for task in pet.tasks if task.is_due_today(check_date)]

    def organize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Organize tasks by sorting them by duration descending (longest first).
        
        Uses a simple greedy approach that prioritizes longer tasks to be scheduled
        earlier in the day, which often creates more natural care routines.
        
        Args:
            tasks: List of tasks to organize
            
        Returns:
            Sorted list of tasks with longest duration first
            
        Note:
            This is a simple O(n log n) sorting operation suitable for typical
            pet care scenarios with limited numbers of tasks.
        """
        return sorted(tasks, key=lambda t: t.time, reverse=True)

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by their duration in ascending order using a lambda function.
        
        Provides an alternative sorting method that can be used for different
        scheduling strategies or analysis purposes.
        
        Args:
            tasks: List of Task objects to sort
            
        Returns:
            New list sorted by task duration (shortest to longest)
            
        Example:
            >>> tasks = [Task("Short", 15, Frequency.DAILY), Task("Long", 60, Frequency.DAILY)]
            >>> sorted_tasks = sort_by_time(tasks)
            >>> [t.time for t in sorted_tasks]  # [15, 60]
        """
        return sorted(tasks, key=lambda t: t.time)

    def sort_scheduled_by_time(self, scheduled_tasks: List[ScheduledTask]) -> List[ScheduledTask]:
        """Sort scheduled tasks by their start time in chronological order.
        
        Parses HH:MM time strings and sorts scheduled tasks by their actual
        start times, useful for displaying schedules in proper time sequence.
        
        Args:
            scheduled_tasks: List of ScheduledTask objects to sort
            
        Returns:
            New list sorted by start time (earliest to latest)
            
        Example:
            >>> tasks = [ScheduledTask(task, "10:00"), ScheduledTask(task, "08:30")]
            >>> sorted_tasks = sort_scheduled_by_time(tasks)
            >>> [st.start_time for st in sorted_tasks]  # ["08:30", "10:00"]
        """
        return sorted(scheduled_tasks, key=lambda st: datetime.strptime(st.start_time, "%H:%M"))

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name with flexible criteria.
        
        Provides powerful filtering capabilities to query tasks across all pets
        based on completion status, specific pet ownership, or combinations thereof.
        
        Args:
            completed: Filter by completion status. 
                      True = only completed tasks,
                      False = only pending tasks,
                      None = ignore completion status
            pet_name: Filter by specific pet name. 
                     If provided, only returns tasks for that pet.
                     If None, includes tasks from all pets.
            
        Returns:
            List of Task objects matching the filter criteria
            
        Examples:
            >>> # Get all pending tasks
            >>> pending = filter_tasks(completed=False)
            >>> 
            >>> # Get completed tasks for specific pet
            >>> done = filter_tasks(completed=True, pet_name="Buddy")
            >>>
            >>> # Get all tasks for a pet
            >>> all_pet_tasks = filter_tasks(pet_name="Whiskers")
        """
        filtered = []
        for pet in self.owner.pets:
            if pet_name and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completion_status != completed:
                    continue
                filtered.append(task)
        return filtered

    def detect_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[str]:
        """Detect time conflicts between scheduled tasks and return warning messages.
        
        Performs pairwise comparison of all scheduled tasks to identify overlapping
        time slots. Provides detailed warnings about which tasks conflict, their
        time ranges, and whether conflicts involve the same pet or different pets.
        
        Args:
            scheduled_tasks: List of ScheduledTask objects to check for conflicts
            
        Returns:
            List of warning message strings describing any conflicts found.
            Empty list if no conflicts detected.
            
        Example:
            >>> conflicts = detect_conflicts(scheduled_tasks)
            >>> if conflicts:
            ...     print("Scheduling conflicts found:")
            ...     for warning in conflicts:
            ...         print(f"⚠️  {warning}")
            
        Note:
            Uses O(n²) pairwise comparison which is acceptable for typical
            pet care schedules (usually < 10 tasks per day).
        """
        warnings = []
        
        for i, task_a in enumerate(scheduled_tasks):
            start_a = datetime.strptime(task_a.start_time, "%H:%M")
            end_a = start_a + timedelta(minutes=task_a.task.time)
            
            for j, task_b in enumerate(scheduled_tasks):
                if i >= j:  # Avoid checking same task or duplicate pairs
                    continue
                    
                start_b = datetime.strptime(task_b.start_time, "%H:%M")
                end_b = start_b + timedelta(minutes=task_b.task.time)
                
                # Check for time overlap
                if start_a < end_b and start_b < end_a:
                    # Find which pet each task belongs to
                    pet_a = None
                    pet_b = None
                    for owner_pet in self.owner.pets:
                        if task_a.task in owner_pet.tasks:
                            pet_a = owner_pet.name
                        if task_b.task in owner_pet.tasks:
                            pet_b = owner_pet.name
                    
                    conflict_type = "same pet" if pet_a == pet_b else "different pets"
                    warning = f"CONFLICT: '{task_a.task.description}' ({pet_a}) and '{task_b.task.description}' ({pet_b}) overlap on {task_a.start_time}-{end_a.strftime('%H:%M')} and {task_b.start_time}-{end_b.strftime('%H:%M')} ({conflict_type})"
                    warnings.append(warning)
        
        return warnings

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name."""
        filtered = []
        for pet in self.owner.pets:
            if pet_name and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completion_status != completed:
                    continue
                filtered.append(task)
        return filtered

    def explain_plan(self, plan: DailyPlan) -> str:
        """Get the reasoning behind the generated plan."""
        return plan.reasoning
