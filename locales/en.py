"""English strings for OurWay bot."""

STRINGS: dict[str, str] = {
    # ── Common ──────────────────────────────────────────────────────────────────
    "common.not_logged_in": "Please send /start first to log in.",
    "common.min_2_chars": "Please enter at least 2 characters.",
    "common.cancelled": "Cancelled.",

    # ── Auth ────────────────────────────────────────────────────────────────────
    "auth.link_invalid": (
        "❌ The link is invalid or has expired.\n"
        "Please generate a new one in the app: Settings → Connect Telegram."
    ),
    "auth.connected_welcome": (
        "✅ Your Telegram account is now connected!\n\n"
        "Welcome, {name}! Type /help to see what I can do."
    ),
    "auth.connected_start_again": "✅ Account connected! Send /start again to log in.",
    "auth.welcome_back": "👋 Welcome back, {name}!\n\nType /help to see available commands.",
    "auth.hello_new_user": (
        "👋 Hi {name}! You've just found OurWay — a family day planner for parents and kids.\n\n"
        "What's your name? (this is how you'll appear to your family)"
    ),
    "auth.registered": (
        "🎉 Welcome to OurWay, {name}!\n\n"
        "OurWay helps families plan their day together — schedules, events, and tasks in one place, "
        "built for parents and kids.\n\n"
        "What you can do here:\n"
        "• /today — your full day plan\n"
        "• /add — create a task\n"
        "• /my — your tasks\n"
        "• /help — all commands\n\n"
        "⚠️ One important step: open the app and set your timezone so your morning briefings "
        "arrive at the right time 👇"
    ),
    "auth.web_login_link": (
        "🌐 Open OurWay in your browser:\n{url}\n\n"
        "The link is valid for 15 minutes."
    ),
    "auth.error": "Something went wrong. Please try /start again.",

    # ── Tasks ───────────────────────────────────────────────────────────────────
    "task.title_prompt": "📝 What's the task title?",
    "task.no_spaces": "You don't have any spaces yet.\nCreate one first:",
    "task.create_space_btn": "➕ Create a space",
    "task.pick_space": "📝 <b>{title}</b>\n\nWhich space should this go to?",
    "task.created": "✅ Task added!\n<b>{title}</b> → {space}\nID: #{id}",
    "task.create_failed": "❌ Failed to create task. Please try again.",
    "task.load_failed": "❌ Failed to load tasks.",
    "task.no_active": "🎉 No active tasks! You're all caught up.",
    "task.list_header": "<b>Your tasks:</b>",
    "task.list_footer": "Use /done &lt;id&gt; to complete a task.",
    "task.done_usage": "Usage: /done &lt;task_id&gt;\nExample: /done 42",
    "task.done_success": "✅ Task #{id} marked as done!",
    "task.done_failed": "❌ Could not complete task #{id}. Check the ID and try again.",
    "task.overdue_label": "overdue {days}d",
    "task.due_today_label": "today",
    "task.progress_label": "{current}/{total}",
    "task.progress_btn": "📊 #{id} {title} — {current}/{total}",
    "task.progress_prompt": "Current progress: {current}/{total}\n\nHow much to add?",
    "task.progress_invalid": "❌ Enter a number from 1 to {max}.",
    "task.progress_saved": "✅ Progress updated: {current}/{total}",
    "task.progress_failed": "❌ Failed to update. Please try again.",
    "task.assign_prompt": "👤 Assign to whom?",
    "task.assign_me": "👤 Me",

    # ── Task scheduling (shared by /add and /plan) ──────────────────────────────
    "sched.pick_day": "📅 Schedule for which day?",
    "sched.today_btn": "Today",
    "sched.tomorrow_btn": "Tomorrow",
    "sched.no_date_btn": "No date",
    "sched.due_prompt": "⏰ Deadline?",
    "sched.due_same_btn": "Same day",
    "sched.due_plus3_btn": "+3 days",
    "sched.due_week_btn": "+1 week",
    "sched.due_none_btn": "No deadline",
    "sched.due_enter_btn": "Enter date",
    "sched.due_enter_hint": "Enter deadline date (e.g. 2026-04-15):",
    "sched.due_invalid": "Invalid date format. Use YYYY-MM-DD (e.g. 2026-04-15):",
    "sched.plan_header": "<b>Unscheduled tasks:</b>",
    "sched.plan_empty": "All tasks already have a date, or no tasks yet.",
    "sched.plan_pick": "Which task to schedule?",
    "sched.plan_updated": "📅 Scheduled: <b>{title}</b> → {date}",
    "sched.plan_usage": "Usage: /plan or /plan &lt;task_id&gt;",
    "sched.task_not_found": "❌ Task not found or you don't have access to it.",

    # ── Spaces ──────────────────────────────────────────────────────────────────
    "space.load_failed": "❌ Failed to load spaces.",
    "space.list_header": "<b>Your spaces:</b>",
    "space.no_spaces": "You don't have any spaces yet.\n\nCreate your first one:",
    "space.create_new_btn": "➕ Create new space",
    "space.name_prompt": "📁 What's the name for your new space?\n(e.g. Family, Home, Work)",
    "space.emoji_prompt": "Got it: <b>{name}</b>\n\nSend an emoji for this space (or skip):",
    "space.skip_btn": "Skip",
    "space.created": "✅ Space created: {emoji} <b>{name}</b>\n\nNow you can add tasks with /add",
    "space.create_failed": "❌ Failed to create space. Please try again.",

    # ── Kids ────────────────────────────────────────────────────────────────────
    "kids.load_failed": "❌ Could not load family members.",
    "kids.no_children": "No children in your family yet.\n\nUse /add_child to add one.",
    "kids.header": "<b>Kids' tasks:</b>",
    "kids.managed_tag": " (managed)",
    "kids.tasks_load_failed": "  ❌ Failed to load tasks",
    "kids.no_active_tasks": "  ✅ No active tasks",
    "kids.footer": "Use /done &lt;id&gt; to complete a task.",

    # ── Add child ────────────────────────────────────────────────────────────────
    "add_child.name_prompt": "👶 What is the child's name?",
    "add_child.invalid_name": "Please enter a valid name.",
    "add_child.autonomy_prompt": "Got it — <b>{name}</b>.\n\nChoose the autonomy level:",
    "add_child.autonomy_supervised": "1 — Supervised (≤12)",
    "add_child.autonomy_semi": "2 — Semi (12–14)",
    "add_child.autonomy_autonomous": "3 — Autonomous (14+)",
    "add_child.cancel_btn": "❌ Cancel",
    "add_child.has_tg_prompt": "Does the child have a Telegram account?",
    "add_child.has_tg_yes": "✅ Yes — send invite link",
    "add_child.has_tg_no": "🚫 No — I manage for them",
    "add_child.create_failed": "❌ Failed to create child profile. Please try again.",
    "add_child.managed_created": (
        "✅ <b>{name}</b>'s profile created (managed).\n\n"
        "You can see their tasks in /kids and mark tasks done on their behalf."
    ),
    "add_child.tg_created": (
        "✅ <b>{name}</b>'s account created.\n\n"
        "Forward the button below to your child so they can connect their Telegram.\n"
        "The link is valid for 24 hours."
    ),
    "add_child.tg_connect_btn": "📱 Connect Telegram ({name})",

    # ── Daily ───────────────────────────────────────────────────────────────────
    "daily.load_today_failed": "❌ Could not load today's plan.",
    "daily.load_tomorrow_failed": "❌ Could not load tomorrow's plan.",
    "daily.nothing_planned": "Nothing planned yet.",
    "daily.plan_confirmed": "✅ Plan confirmed",
    "daily.already_confirmed": "✅ Already confirmed!",
    "daily.confirm_btn": "✅ Confirm plan",
    "daily.add_task_btn": "➕ Add task",
    "daily.plan_confirmed_msg": "✅ Plan confirmed! Sleep well 🌙",
    "daily.confirm_failed": "❌ Could not confirm. Try again.",
    "daily.add_task_hint": (
        "Use /add &lt;task title&gt; to add a task.\n"
        "Then come back and confirm the plan."
    ),
    "daily.today_title": "☀️ Today — {date}",
    "daily.tomorrow_title": "🌙 Tomorrow — {date}",

    # ── Schedule management (/schedule command) ─────────────────────────────────
    "sch.for_whom_prompt": "👤 For whom?",
    "sch.for_self_btn": "For me",
    "sch.list_header": "<b>Your schedule:</b>",
    "sch.child_list_header": "<b>{name}'s schedule:</b>",
    "sch.child_list_empty": "  No schedule yet.",
    "sch.list_empty": "No recurring schedule yet.\n\nUse ➕ to add one.",
    "sch.add_btn": "➕ Add",
    "sch.delete_btn": "🗑 Delete",
    "sch.name_prompt": "📋 Title? (e.g. School, Football, Work)",
    "sch.days_prompt": "🗓 Select weekdays (tap to toggle, then ✅ Done):",
    "sch.days_done_btn": "✅ Done",
    "sch.days_none_selected": "Select at least one day.",
    "sch.time_start_prompt": "🕐 Start time? (e.g. 08:00)",
    "sch.time_end_prompt": "🕑 End time? (e.g. 14:00) or skip:",
    "sch.time_skip_btn": "Skip",
    "sch.time_invalid": "Invalid time format. Use HH:MM (e.g. 08:00):",
    "sch.valid_from_prompt": "📅 Valid from? (e.g. 2026-09-01) or:",
    "sch.valid_from_today_btn": "From today",
    "sch.valid_until_prompt": "📅 Valid until? (e.g. 2027-05-31) or:",
    "sch.valid_until_none_btn": "No end date",
    "sch.date_invalid": "Invalid date format. Use YYYY-MM-DD (e.g. 2026-09-01):",
    "sch.created": "✅ Schedule added: <b>{title}</b>\n{days}, {time_start}–{time_end}",
    "sch.created_no_end": "✅ Schedule added: <b>{title}</b>\n{days}, from {time_start}",
    "sch.create_failed": "❌ Failed to create schedule. Please try again.",
    "sch.pick_to_delete": "Which schedule to delete?",
    "sch.deleted": "🗑 Deleted: <b>{title}</b>",
    "sch.delete_failed": "❌ Failed to delete. Please try again.",
    "sch.days_mon": "Mon",
    "sch.days_tue": "Tue",
    "sch.days_wed": "Wed",
    "sch.days_thu": "Thu",
    "sch.days_fri": "Fri",
    "sch.days_sat": "Sat",
    "sch.days_sun": "Sun",

    # ── Timezone ────────────────────────────────────────────────────────────────
    "tz.current": "🕐 Your current timezone: <b>{tz}</b>\n\nSelect a new one:",
    "tz.saved": "✅ Timezone set to <b>{tz}</b>.\n\nMorning briefing and evening ritual will use this time.",
    "tz.save_failed": "❌ Failed to save timezone. Please try again.",
    "tz.cancel_btn": "❌ Cancel",

    # ── Set time ─────────────────────────────────────────────────────────────────
    "settime.current": (
        "⏰ <b>Notification times</b>\n\n"
        "🌅 Morning briefing: <b>{morning}</b>\n"
        "🌙 Evening ritual: <b>{evening}</b>\n\n"
        "What would you like to change?"
    ),
    "settime.morning_btn": "🌅 Morning",
    "settime.evening_btn": "🌙 Evening",
    "settime.cancel_btn": "❌ Cancel",
    "settime.enter_time": "Enter new time for {which} (format: HH:MM, e.g. 08:00):",
    "settime.invalid_format": "❌ Invalid format. Please use HH:MM, for example: 07:30",
    "settime.saved": "✅ {which} time set to <b>{time}</b>.",
    "settime.save_failed": "❌ Failed to save. Please try again.",

    # ── Invite ──────────────────────────────────────────────────────────────────
    "invite.link_invalid": "❌ This invitation link is invalid or has expired.\nAsk the sender to create a new one with /invite.",
    "invite.register_prompt": (
        "👋 You've been invited to join <b>{space}</b> by {inviter}!\n\n"
        "Let's create your OurWay account. What's your name?"
    ),
    "invite.joined": "🎉 You've joined <b>{space}</b>!\n\nType /help to see what you can do.",
    "invite.registered_joined": (
        "🎉 Welcome to OurWay, {name}!\n\n"
        "You've joined <b>{space}</b>. Type /help to get started."
    ),
    "invite.accept_failed": "⚠️ Account created, but couldn't join the space. The link may have already been used.\nAsk the sender for a new invite.",
    "invite.create_failed": "❌ Failed to create invitation. Please try again.",
    "invite.created": (
        "✅ Invitation link ready!\n\n"
        "Forward the buttons below to the person you want to invite.\n"
        "They'll join your family organisation.\n\n"
        "The link expires in 7 days."
    ),
    "invite.open_tg_btn": "📱 Join via Telegram",
    "invite.open_web_btn": "🌐 Open in browser",

    # ── Events ──────────────────────────────────────────────────────────────────
    "event.load_failed": "❌ Could not load events.",
    "event.no_events": "📅 No upcoming events.",
    "event.list_header": "<b>Upcoming events:</b>",
    "event.delete_btn": "🗑 Delete",
    "event.deleted": "🗑 Deleted: <b>{title}</b>",
    "event.delete_failed": "❌ Could not delete event. Please try again.",
    "event.pick_to_delete": "Which event do you want to delete?",
    "event.title_prompt": "📅 Event title?",
    "event.date_prompt": "📅 <b>{title}</b>\n\nWhat date?",
    "event.date_today_btn": "Today",
    "event.date_tomorrow_btn": "Tomorrow",
    "event.date_skip_btn": "No fixed date",
    "event.date_invalid": "Invalid date format. Use YYYY-MM-DD (e.g. 2026-05-20):",
    "event.time_prompt": "🕐 Start time? (e.g. 14:00)",
    "event.time_skip_btn": "Skip",
    "event.time_invalid": "Invalid time format. Use HH:MM (e.g. 14:00):",
    "event.participants_prompt": "👥 Who's participating? (tap to toggle)",
    "event.participants_me_btn": "Me",
    "event.participants_done_btn": "✅ Done",
    "event.created": "✅ Event added: <b>{title}</b>\n{date}{time}",
    "event.create_failed": "❌ Could not create event. Please try again.",
    "event.cancel_btn": "❌ Cancel",

    # ── Help ────────────────────────────────────────────────────────────────────
    "help.text": (
        "<b>OurWay Bot — Commands</b>\n\n"
        "📅 <b>Day</b>\n"
        "/today — your plan for today\n"
        "/tonight — plan tomorrow (evening ritual)\n\n"
        "📋 <b>Tasks</b>\n"
        "/add &lt;title&gt; — add a new task\n"
        "/my — your active tasks\n"
        "/done &lt;id&gt; — mark task as done\n"
        "/plan — schedule a task from backlog\n\n"
        "🗓 <b>Schedule &amp; Events</b>\n"
        "/schedule — recurring schedule (school, clubs, work)\n"
        "/events — upcoming events\n"
        "/add_event — add a new event\n\n"
        "👨‍👩‍👧 <b>Family</b>\n"
        "/kids — children's tasks\n"
        "/add_child — add a child account\n"
        "/invite — invite an adult member to a space\n\n"
        "📁 <b>Spaces</b>\n"
        "/spaces — list and create spaces\n\n"
        "⚙️ <b>Settings</b>\n"
        "/timezone — view or change your timezone\n"
        "/settime — change morning briefing or evening ritual time\n"
        "/web — open OurWay web app\n\n"
        "ℹ️ /help — show this message"
    ),
    "auth.keyboard_hint": "Quick commands 👇",
}
