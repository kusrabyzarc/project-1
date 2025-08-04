# 🧩 TaskTracker CLI

CLI-интерфейс для управления пользователями и задачами с PostgreSQL-бэкендом.  
Поддерживает безопасную авторизацию, битовые флаги доступа и расширяемый REPL-интерфейс на базе `prompt_toolkit`.

---

# 🚀 Возможности

- 👤 Управление пользователями (создание, удаление, проверка существования, валидация пароля)
- 🔐 Хеширование паролей (SHA256 + ГОСТ Р 34.11-2012)
- 🧠 Битовые флаги прав доступа (`UserFlags`)
- 🧵 Контекстный режим работы с пользователями (`ctx`)
- 🖥️ Интерактивный CLI на базе `prompt_toolkit` с автодополнением и историей команд
- ⚙️ Расширяемость: поддержка подкоманд, модульная архитектура

---

# 🏗️ Стек

- Python 3.10+
- PostgreSQL 14+
- `psycopg2`
- `prompt_toolkit`
- `pygost`

---

# 📦 Установка

```bash
git clone https://github.com/crazybarsuk/project-1.git
cd project-1
git clone https://github.com/mosquito/pygost.git pygost_repo
cp -r ./pygost_repo/pygost/* ./pygost/
rm -rf pygost_repo
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows
pip install -r requirements.txt
```

---

# 🛠️ Конфигурация

Не реализована адекватная система конфигурации.

---

# 🚦 Быстрый старт

```bash
python REPL.py
```

> Используй TAB для автодополнения команд.

# 📌 Примеры команд:

```bash
user create alice
user validate alice
user delete alice
ctx alice
validate
delete
exit
```

---

# 🧪 Нагрузочное тестирование

Скрипт `NT.py` проверяет систему на устойчивость при параллельной работе с пользователями:

```bash
python NT.py
```

---

# 🧼 Чистая архитектура

- `core.py` — бизнес-логика (работа с БД, хеширование, флаги)
- `REPL.py` — интерактивная CLI-оболочка
- `NT.py` — нагрузочное тестирование

---

# 📈 Вектора развития

- [ ] CRUD-задачи (`task add/delete/update/list`)
- [ ] RBAC с использованием `UserFlags`
- [ ] Отчёты по времени выполнения задач
- [ ] JSON/CSV экспорт данных
- [ ] REST API (FastAPI)
- [ ] Асинхронная версия с `asyncpg`

---

# 🙏 Благодарности

- Библиотека `pygost` от [@mosquito](https://github.com/mosquito/pygost) — реализация ГОСТ-хеширования (ГОСТ Р 34.11-2012), используемая для безопасного хранения паролей.

---

# ⚖️ Лицензия

MIT © 2025 CrazYBarsuK
