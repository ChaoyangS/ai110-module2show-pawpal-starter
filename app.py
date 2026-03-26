import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Frequency
from datetime import date

# Initialize session state
if 'owner' not in st.session_state:
    st.session_state.owner = None
if 'current_pet' not in st.session_state:
    st.session_state.current_pet = None

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
available_time = st.number_input("Available time (hours)", min_value=1, max_value=24, value=8)

if st.button("Create Owner"):
    st.session_state.owner = Owner(owner_name, available_time)
    st.success(f"Owner {owner_name} created with {available_time} hours available.")

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add Pet") and st.session_state.owner:
    pet = Pet(pet_name, species, age)
    st.session_state.owner.add_pet(pet)
    st.session_state.current_pet = pet
    st.success(f"Pet {pet_name} added to {st.session_state.owner.name}.")
elif st.button("Add Pet"):
    st.error("Please create an owner first.")

st.markdown("### Tasks")
st.caption("Add tasks to the current pet. Tasks will be scheduled for the selected pet.")

if st.session_state.current_pet:
    st.write(f"Adding tasks to: {st.session_state.current_pet.name} ({st.session_state.current_pet.type})")
else:
    st.warning("No pet selected. Add a pet first.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"], index=0)
with col4:
    if st.button("Add task") and st.session_state.current_pet:
        freq_enum = Frequency.DAILY if frequency == "daily" else Frequency.WEEKLY if frequency == "weekly" else Frequency.MONTHLY
        task = Task(task_title, duration, freq_enum)
        st.session_state.current_pet.add_task(task)
        st.success(f"Task '{task_title}' added to {st.session_state.current_pet.name}.")
    elif st.button("Add task"):
        st.error("Please add a pet first.")

if st.session_state.current_pet and st.session_state.current_pet.tasks:
    st.write("Current tasks for this pet:")
    task_data = [{"Description": t.description, "Time": t.time, "Frequency": t.frequency.value, "Completed": t.completion_status} for t in st.session_state.current_pet.tasks]
    st.table(task_data)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily schedule based on your pets' tasks and available time.")

if st.button("Generate schedule"):
    if st.session_state.owner and st.session_state.owner.pets:
        scheduler = Scheduler(st.session_state.owner)
        today = date.today()
        plan = scheduler.generate_daily_plan(today)
        
        st.success("Schedule generated!")
        st.markdown("### Today's Schedule")
        st.code(plan.display_plan(), language="text")
        
        if plan.reasoning:
            st.info(f"**Reasoning:** {plan.reasoning}")
    else:
        st.error("Please create an owner and add at least one pet with tasks first.")
