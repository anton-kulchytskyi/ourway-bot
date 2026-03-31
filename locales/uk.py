"""Ukrainian strings for OurWay bot."""

STRINGS: dict[str, str] = {
    # ── Common ──────────────────────────────────────────────────────────────────
    "common.not_logged_in": "Будь ласка, надішли /start щоб увійти.",
    "common.min_2_chars": "Будь ласка, введи мінімум 2 символи.",
    "common.cancelled": "Скасовано.",

    # ── Auth ────────────────────────────────────────────────────────────────────
    "auth.link_invalid": (
        "❌ Посилання недійсне або прострочене.\n"
        "Згенеруй нове в додатку: Налаштування → Підключити Telegram."
    ),
    "auth.connected_welcome": (
        "✅ Твій акаунт Telegram підключено!\n\n"
        "Привіт, {name}! Напиши /help щоб дізнатись що я вмію."
    ),
    "auth.connected_start_again": "✅ Акаунт підключено! Надішли /start ще раз щоб увійти.",
    "auth.welcome_back": "👋 З поверненням, {name}!\n\nНапиши /help щоб побачити доступні команди.",
    "auth.hello_new_user": (
        "👋 Привіт, {name}! Ласкаво просимо до OurWay — сімейного планувальника.\n\n"
        "Давай налаштуємо твій акаунт. Як тебе звати?"
    ),
    "auth.registered": (
        "🎉 Ласкаво просимо до OurWay, {name}!\n\n"
        "Акаунт готовий. Напиши /help щоб почати."
    ),
    "auth.error": "Щось пішло не так. Спробуй /start знову.",

    # ── Tasks ───────────────────────────────────────────────────────────────────
    "task.title_prompt": "📝 Яка назва задачі?",
    "task.no_spaces": "У тебе ще немає просторів.\nСпочатку створи один:",
    "task.create_space_btn": "➕ Створити простір",
    "task.pick_space": "📝 <b>{title}</b>\n\nДо якого простору додати?",
    "task.created": "✅ Задачу додано!\n<b>{title}</b> → {space}\nID: #{id}",
    "task.create_failed": "❌ Не вдалось створити задачу. Спробуй ще раз.",
    "task.load_failed": "❌ Не вдалось завантажити задачі.",
    "task.no_active": "🎉 Активних задач немає! Все зроблено.",
    "task.list_header": "<b>Твої задачі:</b>",
    "task.list_footer": "Використай /done &lt;id&gt; щоб завершити задачу.",
    "task.done_usage": "Використання: /done &lt;id_задачі&gt;\nПриклад: /done 42",
    "task.done_success": "✅ Задачу #{id} виконано!",
    "task.done_failed": "❌ Не вдалось завершити задачу #{id}. Перевір ID і спробуй знову.",

    # ── Task scheduling (shared by /add and /plan) ──────────────────────────────
    "sched.pick_day": "📅 На який день запланувати?",
    "sched.today_btn": "Сьогодні",
    "sched.tomorrow_btn": "Завтра",
    "sched.no_date_btn": "Без дати",
    "sched.due_prompt": "⏰ Дедлайн?",
    "sched.due_same_btn": "Той самий день",
    "sched.due_plus3_btn": "+3 дні",
    "sched.due_week_btn": "+1 тиждень",
    "sched.due_none_btn": "Без дедлайну",
    "sched.due_enter_btn": "Ввести дату",
    "sched.due_enter_hint": "Введи дату дедлайну (напр. 2026-04-15):",
    "sched.due_invalid": "Невірний формат дати. Використовуй РРРР-ММ-ДД (напр. 2026-04-15):",
    "sched.plan_header": "<b>Задачі без дати:</b>",
    "sched.plan_empty": "Всі задачі вже мають дату, або задач немає.",
    "sched.plan_pick": "Яку задачу запланувати?",
    "sched.plan_updated": "📅 Заплановано: <b>{title}</b> → {date}",
    "sched.plan_usage": "Використання: /plan або /plan &lt;id_задачі&gt;",
    "sched.task_not_found": "❌ Задачу не знайдено або немає доступу.",

    # ── Spaces ──────────────────────────────────────────────────────────────────
    "space.load_failed": "❌ Не вдалось завантажити простори.",
    "space.list_header": "<b>Твої простори:</b>",
    "space.no_spaces": "У тебе ще немає просторів.\n\nСтвори перший:",
    "space.create_new_btn": "➕ Створити новий простір",
    "space.name_prompt": "📁 Яка назва нового простору?\n(наприклад: Сім'я, Дім, Робота)",
    "space.emoji_prompt": "Чудово: <b>{name}</b>\n\nНадішли емодзі для цього простору (або пропусти):",
    "space.skip_btn": "Пропустити",
    "space.created": "✅ Простір створено: {emoji} <b>{name}</b>\n\nТепер можна додавати задачі через /add",
    "space.create_failed": "❌ Не вдалось створити простір. Спробуй ще раз.",

    # ── Kids ────────────────────────────────────────────────────────────────────
    "kids.load_failed": "❌ Не вдалось завантажити членів сім'ї.",
    "kids.no_children": "В твоїй сім'ї ще немає дітей.\n\nВикористай /add_child щоб додати.",
    "kids.header": "<b>Задачі дітей:</b>",
    "kids.managed_tag": " (керований)",
    "kids.tasks_load_failed": "  ❌ Не вдалось завантажити задачі",
    "kids.no_active_tasks": "  ✅ Немає активних задач",
    "kids.footer": "Використай /done &lt;id&gt; щоб завершити задачу.",

    # ── Add child ────────────────────────────────────────────────────────────────
    "add_child.name_prompt": "👶 Як звати дитину?",
    "add_child.invalid_name": "Будь ласка, введи коректне ім'я.",
    "add_child.autonomy_prompt": "Зрозуміло — <b>{name}</b>.\n\nОберіть рівень автономії:",
    "add_child.autonomy_supervised": "1 — Під наглядом (≤12)",
    "add_child.autonomy_semi": "2 — Напівавтономний (12–14)",
    "add_child.autonomy_autonomous": "3 — Автономний (14+)",
    "add_child.cancel_btn": "❌ Скасувати",
    "add_child.has_tg_prompt": "У дитини є акаунт Telegram?",
    "add_child.has_tg_yes": "✅ Так — надіслати посилання",
    "add_child.has_tg_no": "🚫 Ні — керую сам",
    "add_child.create_failed": "❌ Не вдалось створити профіль дитини. Спробуй ще раз.",
    "add_child.managed_created": (
        "✅ Профіль <b>{name}</b> створено (керований).\n\n"
        "Ти можеш бачити задачі у /kids і відмічати виконання за дитину."
    ),
    "add_child.tg_created": (
        "✅ Акаунт <b>{name}</b> створено.\n\n"
        "Поділись цим посиланням з дитиною щоб вона підключила свій Telegram:\n\n"
        "<code>{link}</code>\n\n"
        "Посилання дійсне 24 години."
    ),

    # ── Daily ───────────────────────────────────────────────────────────────────
    "daily.load_today_failed": "❌ Не вдалось завантажити план на сьогодні.",
    "daily.load_tomorrow_failed": "❌ Не вдалось завантажити план на завтра.",
    "daily.nothing_planned": "Нічого не заплановано.",
    "daily.plan_confirmed": "✅ План підтверджено",
    "daily.already_confirmed": "✅ Вже підтверджено!",
    "daily.confirm_btn": "✅ Підтвердити план",
    "daily.add_task_btn": "➕ Додати задачу",
    "daily.plan_confirmed_msg": "✅ План підтверджено! Солодких снів 🌙",
    "daily.confirm_failed": "❌ Не вдалось підтвердити. Спробуй знову.",
    "daily.add_task_hint": (
        "Використай /add &lt;назва задачі&gt; щоб додати задачу.\n"
        "Потім повернись і підтверди план."
    ),
    "daily.today_title": "☀️ Сьогодні — {date}",
    "daily.tomorrow_title": "🌙 Завтра — {date}",

    # ── Schedule management (/schedule command) ─────────────────────────────────
    "sch.list_header": "<b>Твій розклад:</b>",
    "sch.list_empty": "Постійного розкладу ще немає.\n\nНатисни ➕ щоб додати.",
    "sch.add_btn": "➕ Додати",
    "sch.delete_btn": "🗑 Видалити",
    "sch.name_prompt": "📋 Назва? (напр. Школа, Футбол, Робота)",
    "sch.days_prompt": "🗓 Вибери дні тижня (тапай щоб вмикати/вимикати, потім ✅ Готово):",
    "sch.days_done_btn": "✅ Готово",
    "sch.days_none_selected": "Вибери хоча б один день.",
    "sch.time_start_prompt": "🕐 Час початку? (напр. 08:00)",
    "sch.time_end_prompt": "🕑 Час кінця? (напр. 14:00) або пропустити:",
    "sch.time_skip_btn": "Пропустити",
    "sch.time_invalid": "Невірний формат часу. Використовуй ГГ:ХХ (напр. 08:00):",
    "sch.valid_from_prompt": "📅 Діє з? (напр. 2026-09-01) або:",
    "sch.valid_from_today_btn": "З сьогодні",
    "sch.valid_until_prompt": "📅 Діє до? (напр. 2027-05-31) або:",
    "sch.valid_until_none_btn": "Без обмежень",
    "sch.date_invalid": "Невірний формат дати. Використовуй РРРР-ММ-ДД (напр. 2026-09-01):",
    "sch.created": "✅ Розклад додано: <b>{title}</b>\n{days}, {time_start}–{time_end}",
    "sch.created_no_end": "✅ Розклад додано: <b>{title}</b>\n{days}, з {time_start}",
    "sch.create_failed": "❌ Не вдалось створити розклад. Спробуй ще раз.",
    "sch.pick_to_delete": "Який розклад видалити?",
    "sch.deleted": "🗑 Видалено: <b>{title}</b>",
    "sch.delete_failed": "❌ Не вдалось видалити. Спробуй ще раз.",
    "sch.days_mon": "Пн",
    "sch.days_tue": "Вт",
    "sch.days_wed": "Ср",
    "sch.days_thu": "Чт",
    "sch.days_fri": "Пт",
    "sch.days_sat": "Сб",
    "sch.days_sun": "Нд",

    # ── Help ────────────────────────────────────────────────────────────────────
    "help.text": (
        "<b>OurWay Бот — Команди</b>\n\n"
        "📋 <b>Задачі</b>\n"
        "/add &lt;назва&gt; — додати нову задачу\n"
        "/my — показати активні задачі\n"
        "/done &lt;id&gt; — відмітити задачу виконаною\n"
        "/plan — запланувати задачу без дати\n"
        "/plan &lt;id&gt; — запланувати конкретну задачу\n\n"
        "📅 <b>День</b>\n"
        "/today — план на сьогодні\n"
        "/tonight — планувати завтра (вечірній ритуал)\n\n"
        "🗓 <b>Розклад</b>\n"
        "/schedule — керування постійним розкладом (школа, секції, робота)\n\n"
        "👨‍👩‍👧 <b>Сім'я</b>\n"
        "/kids — задачі дітей (керовані + автономія 1-2)\n"
        "/add_child — додати дитину (керовану або із запрошенням)\n\n"
        "📁 <b>Простори</b>\n"
        "/spaces — список і створення просторів\n\n"
        "ℹ️ <b>Інше</b>\n"
        "/start — увійти або зареєструватись\n"
        "/help — показати це повідомлення"
    ),
}
