# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design consists of a class diagram with 5 main classes representing the core components of the PawPal+ pet care planning system: Owner, Pet, CareTask, Scheduler, and DailyPlan. The design follows object-oriented principles with clear separation of concerns, using dataclasses for data-focused classes (Owner, Pet, CareTask, DailyPlan) to keep the code clean and concise, while using a regular class for the Scheduler which contains the main business logic. Relationships show that Owner has a Pet, Scheduler manages Owner, Pet, CareTasks, and generates DailyPlans, and DailyPlans contain scheduled CareTasks.

The classes included and their responsibilities are:

1. **Owner**: Represents the pet owner, responsible for storing personal information (name, available time) and preferences (e.g., preferred walk times). It provides methods to update and retrieve preferences and available time.

2. **Pet**: Represents the pet, responsible for holding basic pet information (name, type, age, special needs). It provides a method to return default care requirements based on the pet's type.

3. **CareTask**: Represents individual pet care tasks, responsible for storing task details (name, duration, priority, type, frequency, dependencies). It includes methods to check if the task is due on a given date and calculate a priority score for scheduling.

4. **Scheduler**: The central logic class, responsible for managing the scheduling process. It holds references to the owner, pet, task list, and constraints, and provides methods to generate daily plans, optimize task schedules, and explain the reasoning behind plans.

5. **DailyPlan**: Represents the generated daily care schedule, responsible for storing the date, list of scheduled tasks with times, total time, and reasoning. It provides methods to display the plan, add tasks to it, and validate the plan's feasibility.

Based on brainstorming the main objects needed for the PawPal+ system, the following classes were identified:

1. **Owner**
   - **Attributes**: name (string), available_time (int, daily hours available), preferences (dict, e.g., preferred walk times, dietary restrictions)
   - **Methods**: update_preferences(preferences), get_available_time() -> int

2. **Pet**
   - **Attributes**: name (string), type (string, e.g., 'dog', 'cat'), age (int), special_needs (list of strings)
   - **Methods**: get_care_requirements() -> list (returns default tasks based on pet type)

3. **CareTask**
   - **Attributes**: name (string), duration (int, minutes), priority (string/enum: 'high', 'medium', 'low'), task_type (string, e.g., 'walk', 'feeding'), frequency (string, e.g., 'daily'), dependencies (list of task names)
   - **Methods**: is_due_today(date) -> bool, calculate_priority_score() -> int

4. **Scheduler**
   - **Attributes**: owner (Owner instance), pet (Pet instance), tasks_list (list of CareTask), constraints (dict, e.g., max_daily_time)
   - **Methods**: generate_daily_plan(date) -> DailyPlan, optimize_schedule(tasks) -> list, explain_plan(plan) -> string

5. **DailyPlan**
   - **Attributes**: date (date), scheduled_tasks (list of dicts with task and time), total_time (int, minutes), reasoning (string)
   - **Methods**: display_plan() -> string, add_task_to_plan(task, time), validate_plan() -> bool

**UML Class Diagram**

See [uml_final.png](uml_final.png) for the final diagram.

**b. Design changes**

Yes, the design evolved during the initial implementation phase when creating the Python class skeletons. Several refinements were made to address missing relationships and improve type safety:

1. **Added Owner-Pet relationship**: The initial UML showed Owner has Pet, but the skeleton code didn't reflect this. Added a `pet` attribute to the `Owner` class and removed the redundant separate `pet` parameter from `Scheduler` to properly model the ownership relationship.

2. **Introduced enums for better type safety**: Replaced string-based `priority` and `frequency` attributes in `CareTask` with `Enum` classes (`Priority` and `Frequency`) to prevent invalid values and provide better validation at runtime.

3. **Structured scheduled tasks**: Created a `ScheduledTask` dataclass to replace the vague `List[Dict[str, Any]]` in `DailyPlan`, providing clearer structure and type safety for representing scheduled tasks with their start times.

4. **Improved method return types**: Changed `Pet.get_care_requirements()` to return `List[CareTask]` instead of `List[str]` for more useful and type-safe data that can be directly used in scheduling logic.

These changes were made to make the code more robust, maintainable, and aligned with the UML design, preventing potential runtime errors and improving the overall system architecture before implementing the scheduling logic.

**c. Core Actions**

Based on the README.md, the three core actions a user should be able to perform are:

1. Enter basic owner and pet information.
2. Add or edit pet care tasks (including duration and priority).
3. Generate and view a daily care schedule/plan based on constraints and priorities.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two main constraints:

1. **Available time** — the owner's `available_time` (in hours) is converted to minutes and used as a hard cap. Tasks are skipped if adding them would exceed this limit. This was treated as the most important constraint because a schedule that overruns the owner's day is useless regardless of how well the tasks are ordered.

2. **Task recurrence and due date** — only tasks where `check_date >= next_due_date` are included in a given day's plan. This prevents tasks from appearing every day when they are weekly or monthly.

Priority as a field (`high`/`medium`/`low`) was planned in the initial UML but was dropped during implementation. The greedy sort by duration (longest first) acts as an implicit proxy for priority — longer tasks like grooming or vet visits naturally get scheduled before quick ones like feeding — but there is no explicit priority ranking. This was a deliberate simplification to keep the MVP deliverable and testable within the project scope.

**b. Tradeoffs**

**Sequential Greedy Scheduling vs. Optimal Multi-Constraint Optimization**

The scheduler uses a simple greedy algorithm that sorts tasks by duration (longest first) and schedules them sequentially starting at 8:00 AM, only skipping tasks that would exceed the owner's available time. This approach prioritizes simplicity and predictability over finding the mathematically optimal schedule.

**Why this tradeoff is reasonable:**

- **Performance**: For typical pet care scenarios (5-15 daily tasks), the greedy approach is computationally efficient and runs in O(n log n) time due to sorting, making it suitable for real-time scheduling without noticeable delays.
- **Predictability**: Pet owners prefer consistent, understandable schedules over complex optimizations they can't easily predict or explain.
- **Maintainability**: Simple algorithms are easier to debug, test, and modify as pet care needs evolve.
- **Sufficiency**: For most pet care routines, scheduling longer tasks first (like walks or grooming) followed by shorter tasks (like feeding or medication) creates naturally logical daily flows that work well in practice.

While more sophisticated algorithms could optimize for factors like task priority, pet energy levels, or owner preferences, the current approach provides reliable, human-readable schedules that pet owners can easily understand and adjust manually when needed.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used at every stage of the project:

- **Design review** — asked the AI to analyze the final `pawpal_system.py` and identify what had changed from the initial UML, producing a concrete diff of renamed classes, dropped attributes, and new methods.
- **Test generation** — described the edge cases (pet with no tasks, two tasks at the same time, `available_time = 0`) and asked the AI to draft pytest functions covering happy paths and boundary conditions.
- **UI wiring** — asked the AI to update `app.py` to call `sort_by_time()`, `sort_scheduled_by_time()`, and `detect_conflicts()` directly, and to surface conflict warnings as individual `st.warning` cards rather than a buried string.
- **Debugging** — used the AI to diagnose why `python app.py` crashed (session state requires `streamlit run`) and to identify the duplicate `elif st.button()` pattern causing widget errors.

The most useful prompt pattern was being specific about *what the code should do* rather than *how*: for example, "surface each conflict as a separate warning card so the owner can act on them one at a time" produced better UI code than "add conflict warnings to the app."

**b. Judgment and verification**

One moment where the AI suggestion was not accepted as-is: when the AI generated the UML final diagram, it initially kept `CareTask` as the class name and included `priority` and `dependencies` attributes that were never implemented. Before accepting, the actual `pawpal_system.py` was checked line by line to confirm the real class name (`Task`), the real attributes (`description`, `time`, `frequency`, `completion_status`, `next_due_date`), and the real methods. The diagram was corrected to match the implementation rather than the original design intent.

Similarly, the AI flagged the duplicate `filter_tasks()` method as a known gap — this was verified by searching the file and confirming that Python silently uses the second definition, making the first dead code.

---

## 4. Testing and Verification

**a. What you tested**

Thirteen pytest functions were written across four areas:

1. **Sorting correctness** — verified that `sort_scheduled_by_time()` returns tasks in chronological order and that `organize_tasks()` always puts the longest task first, including with a single-item list.
2. **Recurrence logic** — confirmed that `mark_complete()` advances `next_due_date` by the correct interval for daily (1 day), weekly (7 days), and monthly (30 days) frequencies, that calling it twice compounds correctly, and that `is_due_today()` returns the right boolean on and before the due date.
3. **Conflict detection** — verified that two tasks sharing a start time produce exactly one conflict warning containing "CONFLICT", that non-overlapping tasks produce an empty list, and that a single task never conflicts with itself.
4. **Edge cases** — confirmed that a pet with no tasks returns an empty plan without raising an exception, that tasks exceeding `available_time` are skipped and noted in `reasoning`, and that a full happy-path plan schedules all tasks and sets reasoning to "All due tasks scheduled."

These tests mattered because the scheduler's core value — producing a reliable daily plan — depends on all four behaviors working correctly together. A bug in sorting would produce the wrong task order; a bug in recurrence would flood the schedule with tasks that aren't due; a missed conflict would leave the owner with an impossible plan.

**b. Confidence**

**3 / 5** — the core logic is correct and tested, but three known gaps limit confidence:

- The duplicate `filter_tasks()` method means only the second definition is active; the first is silently dead code.
- Monthly recurrence uses a fixed 30-day approximation, which drifts over real calendar months (e.g., February completions will schedule the next occurrence too late).
- `available_time` is stored in hours but task durations are in minutes; the conversion (`* 60`) happens in `generate_daily_plan()` — any caller that passes minutes directly would silently schedule the wrong amount of work.

Next tests to write: multi-pet conflict detection (tasks from two different pets overlapping), `available_time = 0` (no tasks should be scheduled), and marking a monthly task complete in January (due date should land in February, not overflow).

---

## 5. Reflection

**a. What went well**

The part of the project most satisfying is the conflict detection and how it surfaces in the UI. `detect_conflicts()` performs a clean pairwise comparison and returns structured warning strings that include both task names, their time windows, and whether the conflict is same-pet or cross-pet. In the Streamlit app, each conflict becomes its own `st.warning` card — the owner sees exactly which two tasks clash and when, rather than a generic error message. The backend logic and the UI presentation ended up well matched.

The recurrence engine also worked cleanly: a single `mark_complete()` call advances the due date correctly across all three frequencies, and `is_due_today()` acts as a simple gate that keeps the daily plan lean without needing any additional filtering logic.

**b. What you would improve**

Two things stand out for a next iteration:

1. **Add explicit task priority** — the initial UML planned for `high`/`medium`/`low` priority but it was dropped. The greedy sort by duration is a rough substitute, but a short high-priority task (e.g., medication) can get buried behind long low-priority ones. A two-key sort (priority first, then duration) would produce more clinically correct schedules.

2. **Fix the hours/minutes unit boundary** — `available_time` is stored in hours but compared against task durations in minutes. The conversion is done in one place (`generate_daily_plan`), but this is a fragile contract. A cleaner design would store `available_time` in minutes throughout, or use a dedicated type/wrapper so the unit is enforced at the boundary rather than assumed.

**c. Key takeaway**

The most important thing learned is that **UML diagrams should describe what was built, not what was planned**. The initial diagram included `priority`, `task_type`, and `dependencies` on `CareTask` — none of which were implemented. Keeping a stale diagram creates a false picture of the system for anyone reading it later. Updating the diagram at the end of the project (renaming `CareTask` to `Task`, removing unused attributes, adding `ScheduledTask` and `Frequency`) turned it from a design sketch into an accurate reference. Treating the UML as a living document rather than a one-time deliverable makes it genuinely useful.
