import pytest
from pawpal_system import Task, Pet, Frequency


def test_task_completion():
    """Test that calling mark_complete() changes the task's completion status."""
    task = Task("Test Task", 30, Frequency.DAILY)
    
    # Initially, task should not be completed
    assert task.completion_status == False
    
    # Mark as complete
    task.mark_complete()
    
    # Now it should be completed
    assert task.completion_status == True


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