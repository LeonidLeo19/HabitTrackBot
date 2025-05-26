# HabitTrackBot

Telegram bot для отслеживания привычек.

---

## Описание

Этот бот помогает пользователям ставить цели по привычкам, отслеживать прогресс и получать напоминания.  
Реализован с использованием Python, aiogram и асинхронного SQLAlchemy с PostgreSQL.

---

## Технологии

- Python 3.9 и выше  
- aiogram — библиотека для создания Telegram ботов  
- SQLAlchemy (asyncio) — ORM для работы с базой данных  
- PostgreSQL — система управления базами данных  
- Asyncpg — асинхронный драйвер PostgreSQL  
- APScheduler — планировщик задач  

---

## Возможности

- Регистрация пользователей по Telegram ID  
- Добавление, удаление и отслеживание привычек  
- Ежедневное обновление прогресса привычек  
- Напоминания о привычках в удобное время  
- Отслеживание стриков (продолжительных серий выполнения привычек)  

---

## Установка и запуск

1. Клонировать репозиторий:

    ```bash
    git clone https://github.com/LeonidLeo19/HabitTrackBot.git&&
    cd HabitTrackBot
    ```

2. Установить зависимости:

    ```bash
    pip install -r requirements.txt
    ```

3. Настроить переменные окружения или заменить в коде заглушки для подключения к базе данных и Telegram боту.

4. Создать и инициализировать базу данных (если нужно):

    ```bash
    python bd.py
    ```

5. Запустить бота:

    ```bash
    python main.py
    ```

---

## Структура проекта

- `bd.py` — модели базы данных и функции для работы с данными  
- `send_reminder.py` — функции отправки напоминаний и проверки стриков  
- `scheduler.py` — настройка планировщика заданий  
- `bot_instance.py` — инициализация бота  
- `main.py` — точка входа для запуска бота  

---

# HabitTrackBot

Telegram bot for habit tracking.

---

## Description

This bot helps users set habit goals, track progress, and receive reminders.  
Built with Python, aiogram, and asynchronous SQLAlchemy with PostgreSQL.

---

## Technologies

- Python 3.9 and higher  
- aiogram — Telegram bot framework  
- SQLAlchemy (asyncio) — ORM for database interaction  
- PostgreSQL — database management system  
- Asyncpg — asynchronous PostgreSQL driver  
- APScheduler — task scheduler  

---

## Features

- User registration by Telegram ID  
- Adding, deleting, and tracking habits  
- Daily progress updates for habits  
- Reminders sent at convenient times  
- Streak tracking (long consecutive habit completions)  

---

## Installation and Running

1. Clone the repository:

    ```bash
    git clone https://github.com/LeonidLeo19/HabitTrackBot.git
    cd HabitTrackBot
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure environment variables or replace placeholders in the code for database connection and Telegram bot token.

4. Create and initialize the database (if needed):

    ```bash
    python bd.py
    ```

5. Run the bot:

    ```bash
    python main.py
    ```

---

## Project Structure

- `bd.py` — database models and data handling functions  
- `send_reminder.py` — functions for sending reminders and checking streaks  
- `scheduler.py` — task scheduler setup  
- `bot_instance.py` — bot initialization  
- `main.py` — entry point to run the bot  
