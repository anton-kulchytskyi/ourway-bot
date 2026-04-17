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
        "👋 Привіт {name}! Ти знайшов OurWay — сімейний планувальник для батьків і дітей.\n\n"
        "Як тебе звати? (так ти будеш відображатись у своїй сім'ї)"
    ),
    "auth.registered": (
        "🎉 Ласкаво просимо до OurWay, {name}!\n\n"
        "OurWay допомагає сім'ям планувати день разом — розклад, події і задачі в одному місці, "
        "для батьків і дітей.\n\n"
        "Що можна робити тут:\n"
        "• /today — твій план на сьогодні\n"
        "• /add — створити задачу\n"
        "• /my — твої задачі\n"
        "• /help — всі команди\n\n"
        "⚠️ Важливий крок: відкрий додаток і встанови свій часовий пояс, "
        "щоб ранковий briefing приходив вчасно 👇"
    ),
    "auth.web_login_link": (
        "🌐 Відкрий OurWay у браузері:\n{url}\n\n"
        "Посилання дійсне 15 хвилин."
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
    "task.overdue_label": "прострочено {days}д",
    "task.due_today_label": "сьогодні",
    "task.progress_label": "{current}/{total}",
    "task.progress_btn": "📊 #{id} {title} — {current}/{total}",
    "task.progress_prompt": "Скільки зараз виконано? (число від 0 до {total})",
    "task.progress_invalid": "❌ Введи число від 0 до {total}.",
    "task.progress_saved": "✅ Прогрес оновлено: {current}/{total}",
    "task.progress_failed": "❌ Не вдалось оновити. Спробуй ще раз.",

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
        "Перешли кнопку нижче дитині щоб вона підключила свій Telegram.\n"
        "Посилання дійсне 24 години."
    ),
    "add_child.tg_connect_btn": "📱 Підключити Telegram ({name})",

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
    "sch.for_whom_prompt": "👤 Для кого?",
    "sch.for_self_btn": "Для себе",
    "sch.list_header": "<b>Твій розклад:</b>",
    "sch.child_list_header": "<b>Розклад {name}:</b>",
    "sch.child_list_empty": "  Розкладу ще немає.",
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

    # ── Timezone ────────────────────────────────────────────────────────────────
    "tz.current": "🕐 Твій поточний часовий пояс: <b>{tz}</b>\n\nОбери новий:",
    "tz.saved": "✅ Часовий пояс встановлено: <b>{tz}</b>.\n\nРанковий briefing і вечірній ритуал будуть за цим часом.",
    "tz.save_failed": "❌ Не вдалось зберегти. Спробуй ще раз.",
    "tz.cancel_btn": "❌ Скасувати",

    # ── Set time ─────────────────────────────────────────────────────────────────
    "settime.current": (
        "⏰ <b>Час сповіщень</b>\n\n"
        "🌅 Ранковий briefing: <b>{morning}</b>\n"
        "🌙 Вечірній ритуал: <b>{evening}</b>\n\n"
        "Що хочеш змінити?"
    ),
    "settime.morning_btn": "🌅 Ранок",
    "settime.evening_btn": "🌙 Вечір",
    "settime.cancel_btn": "❌ Скасувати",
    "settime.enter_time": "Введи новий час для {which} (формат: HH:MM, наприклад 08:00):",
    "settime.invalid_format": "❌ Невірний формат. Використовуй HH:MM, наприклад: 07:30",
    "settime.saved": "✅ Час {which} встановлено: <b>{time}</b>.",
    "settime.save_failed": "❌ Не вдалось зберегти. Спробуй ще раз.",

    # ── Invite ──────────────────────────────────────────────────────────────────
    "invite.link_invalid": "❌ Це запрошення недійсне або прострочене.\nПопроси відправника створити нове через /invite.",
    "invite.register_prompt": (
        "👋 Тебе запросили до <b>{space}</b> від {inviter}!\n\n"
        "Давай створимо твій акаунт OurWay. Як тебе звати?"
    ),
    "invite.joined": "🎉 Ти приєднався до <b>{space}</b>!\n\nНапиши /help щоб дізнатись що можна робити.",
    "invite.registered_joined": (
        "🎉 Ласкаво просимо до OurWay, {name}!\n\n"
        "Ти приєднався до <b>{space}</b>. Напиши /help щоб почати."
    ),
    "invite.accept_failed": "⚠️ Акаунт створено, але не вдалось приєднатись до простору. Посилання вже могло бути використано.\nПопроси нове запрошення.",
    "invite.create_failed": "❌ Не вдалось створити запрошення. Спробуй ще раз.",
    "invite.created": (
        "✅ Посилання для запрошення готове!\n\n"
        "Перешли кнопки нижче тому, кого хочеш запросити.\n"
        "Людина потрапить до твоєї сімейної організації.\n\n"
        "Посилання дійсне 7 днів."
    ),
    "invite.open_tg_btn": "📱 Приєднатись через Telegram",
    "invite.open_web_btn": "🌐 Відкрити у браузері",

    # ── Events ──────────────────────────────────────────────────────────────────
    "event.load_failed": "❌ Не вдалось завантажити події.",
    "event.no_events": "📅 Майбутніх подій немає.",
    "event.list_header": "<b>Майбутні події:</b>",
    "event.delete_btn": "🗑 Видалити",
    "event.deleted": "🗑 Видалено: <b>{title}</b>",
    "event.delete_failed": "❌ Не вдалось видалити подію. Спробуй ще раз.",
    "event.pick_to_delete": "Яку подію видалити?",
    "event.title_prompt": "📅 Назва події?",
    "event.date_prompt": "📅 <b>{title}</b>\n\nЯка дата?",
    "event.date_today_btn": "Сьогодні",
    "event.date_tomorrow_btn": "Завтра",
    "event.date_skip_btn": "Без фіксованої дати",
    "event.date_invalid": "Невірний формат дати. Використовуй РРРР-ММ-ДД (напр. 2026-05-20):",
    "event.time_prompt": "🕐 Час початку? (напр. 14:00)",
    "event.time_skip_btn": "Пропустити",
    "event.time_invalid": "Невірний формат часу. Використовуй ГГ:ХХ (напр. 14:00):",
    "event.participants_prompt": "👥 Хто бере участь? (тапай щоб вмикати/вимикати)",
    "event.participants_me_btn": "Я",
    "event.participants_done_btn": "✅ Готово",
    "event.created": "✅ Подію додано: <b>{title}</b>\n{date}{time}",
    "event.create_failed": "❌ Не вдалось створити подію. Спробуй ще раз.",
    "event.cancel_btn": "❌ Скасувати",

    # ── Help ────────────────────────────────────────────────────────────────────
    "help.text": (
        "<b>OurWay Бот — Команди</b>\n\n"
        "📅 <b>День</b>\n"
        "/today — план на сьогодні\n"
        "/tonight — планувати завтра (вечірній ритуал)\n\n"
        "📋 <b>Задачі</b>\n"
        "/add &lt;назва&gt; — додати нову задачу\n"
        "/my — активні задачі\n"
        "/done &lt;id&gt; — відмітити задачу виконаною\n"
        "/plan — запланувати задачу з беклогу\n\n"
        "🗓 <b>Розклад і події</b>\n"
        "/schedule — постійний розклад (школа, секції, робота)\n"
        "/events — майбутні події\n"
        "/add_event — додати нову подію\n\n"
        "👨‍👩‍👧 <b>Сім'я</b>\n"
        "/kids — задачі дітей\n"
        "/add_child — додати дитячий акаунт\n"
        "/invite — запросити дорослого члена до простору\n\n"
        "📁 <b>Простори</b>\n"
        "/spaces — список і створення просторів\n\n"
        "⚙️ <b>Налаштування</b>\n"
        "/timezone — переглянути або змінити часовий пояс\n"
        "/settime — змінити час ранкового briefing або вечірнього ритуалу\n"
        "/web — відкрити OurWay у браузері\n\n"
        "ℹ️ /help — показати це повідомлення"
    ),
    "auth.keyboard_hint": "Швидкі команди 👇",
}
