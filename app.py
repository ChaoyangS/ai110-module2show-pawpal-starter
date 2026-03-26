import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Frequency
from datetime import date, datetime, timedelta

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "current_pet" not in st.session_state:
    st.session_state.current_pet = None
if "plan" not in st.session_state:
    st.session_state.plan = None


def _end_time(start: str, duration_minutes: int) -> str:
    """Return HH:MM end time given a start string and duration in minutes."""
    t = datetime.strptime(start, "%H:%M") + timedelta(minutes=duration_minutes)
    return t.strftime("%H:%M")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.caption("A smart pet care scheduler that plans your day around your pets' needs.")
st.divider()

# ---------------------------------------------------------------------------
# Section 1 — Owner
# ---------------------------------------------------------------------------
st.subheader("Owner")
col_a, col_b, col_c = st.columns([2, 1, 1])
with col_a:
    owner_name = st.text_input("Your name", value="Jordan")
with col_b:
    available_time = st.number_input("Available time (hours/day)", min_value=1, max_value=24, value=8)
with col_c:
    st.write("")
    st.write("")
    if st.button("Create Owner", use_container_width=True):
        st.session_state.owner = Owner(owner_name, available_time)
        st.session_state.plan = None
        st.success(f"Owner **{owner_name}** created — {available_time} hrs/day available.")

if st.session_state.owner:
    o = st.session_state.owner
    st.caption(f"Active owner: **{o.name}** · {o.available_time} hrs/day · {len(o.pets)} pet(s)")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Pets
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)
with col4:
    st.write("")
    st.write("")
    if st.button("Add Pet", use_container_width=True):
        if st.session_state.owner:
            new_pet = Pet(pet_name, species, age)
            st.session_state.owner.add_pet(new_pet)
            st.session_state.current_pet = new_pet
            st.session_state.plan = None
            st.success(f"**{pet_name}** the {species} added.")
        else:
            st.error("Create an owner first.")

# Pet selector (if multiple pets exist)
if st.session_state.owner and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected = st.selectbox("Active pet (for adding tasks)", pet_names)
    st.session_state.current_pet = next(
        p for p in st.session_state.owner.pets if p.name == selected
    )

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Tasks
# ---------------------------------------------------------------------------
st.subheader("Tasks")
if st.session_state.current_pet:
    st.caption(f"Adding tasks to **{st.session_state.current_pet.name}**")
else:
    st.warning("Add a pet before adding tasks.")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
with col4:
    st.write("")
    st.write("")
    if st.button("Add Task", use_container_width=True):
        if st.session_state.current_pet:
            freq_map = {
                "daily": Frequency.DAILY,
                "weekly": Frequency.WEEKLY,
                "monthly": Frequency.MONTHLY,
            }
            new_task = Task(task_title, duration, freq_map[frequency])
            st.session_state.current_pet.add_task(new_task)
            st.session_state.plan = None
            st.success(f"Task **{task_title}** ({duration} min, {frequency}) added.")
        else:
            st.error("Add a pet first.")

# Task list — sorted shortest → longest via Scheduler.sort_by_time()
if st.session_state.owner and any(p.tasks for p in st.session_state.owner.pets):
    scheduler = Scheduler(st.session_state.owner)
    all_tasks = st.session_state.owner.get_all_tasks()
    sorted_tasks = scheduler.sort_by_time(all_tasks)

    st.markdown("##### All tasks — sorted shortest to longest")
    task_rows = []
    for t in sorted_tasks:
        owner_pet = next(
            (p.name for p in st.session_state.owner.pets if t in p.tasks), "—"
        )
        task_rows.append({
            "Pet": owner_pet,
            "Task": t.description,
            "Duration (min)": t.time,
            "Frequency": t.frequency.value,
            "Next due": str(t.next_due_date),
        })
    st.dataframe(task_rows, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Schedule
# ---------------------------------------------------------------------------
st.subheader("Today's Schedule")
st.caption(f"Planning for {date.today().strftime('%A, %B %d %Y')}")

if st.button("Generate Schedule", type="primary"):
    if st.session_state.owner and st.session_state.owner.pets:
        scheduler = Scheduler(st.session_state.owner)
        st.session_state.plan = scheduler.generate_daily_plan(date.today())
    else:
        st.error("Create an owner and add at least one pet with tasks first.")

if st.session_state.plan:
    plan = st.session_state.plan

    # --- Conflict warnings — shown first so the owner sees them immediately ---
    if plan.scheduled_tasks:
        scheduler = Scheduler(st.session_state.owner)
        conflicts = scheduler.detect_conflicts(plan.scheduled_tasks)
        if conflicts:
            st.error(
                f"**{len(conflicts)} scheduling conflict(s) found.** "
                "Two or more tasks overlap — adjust their durations or add more available time."
            )
            for conflict in conflicts:
                # Strip the leading "CONFLICT: " prefix for readability
                detail = conflict.replace("CONFLICT: ", "")
                st.warning(f"⚠️ {detail}")

    # --- Summary bar ---
    if not plan.scheduled_tasks:
        st.info("No tasks are due today.")
    else:
        st.success(
            f"{len(plan.scheduled_tasks)} task(s) scheduled · "
            f"{plan.total_time} min total"
        )

        # Schedule table — sorted chronologically via sort_scheduled_by_time()
        scheduler = Scheduler(st.session_state.owner)
        sorted_schedule = scheduler.sort_scheduled_by_time(plan.scheduled_tasks)
        schedule_rows = [
            {
                "Start": item.start_time,
                "End": _end_time(item.start_time, item.task.time),
                "Task": item.task.description,
                "Duration (min)": item.task.time,
            }
            for item in sorted_schedule
        ]
        st.dataframe(schedule_rows, use_container_width=True, hide_index=True)

        # Skipped tasks warning
        if "Skipped" in plan.reasoning:
            skipped_line = plan.reasoning.split(";")[0]
            st.warning(f"**Not scheduled (time limit reached):** {skipped_line.replace('Skipped ', '')}")
        else:
            st.success("All due tasks fit within your available time.")
