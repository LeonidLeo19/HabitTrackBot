from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from bd import AsyncSessionLocal, select, Habit, Habit_progress, User
from send_reminder import send_reminder,check_strick


# Функция для создания записи о прогрессе привычек
async def create_new_habit_progress():
    today = datetime.date.today()
    try:
        async with AsyncSessionLocal() as session:
            habits = await session.execute(select(Habit))
            habits = habits.scalars().all()

            for habit in habits:
                new_progress = Habit_progress(
                    habit_id=habit.id,
                    date=today,
                    current_count=0
                )
                session.add(new_progress)
            
            await session.commit()
            print(f"[{today}] ✅ New progress records created successfully.")

    except Exception as e:
        print(f"[{today}] ❌ Error while creating progress records:", str(e))


# Функция для запуска планировщика
def start_scheduler():
    scheduler = AsyncIOScheduler()

    # Запуск каждый день в 00:00
    scheduler.add_job(create_new_habit_progress, CronTrigger(hour=0, minute=0))

    scheduler.add_job(send_reminder, CronTrigger(hour=22, minute=0))

    scheduler.add_job(check_strick, CronTrigger(hour=0,minute=0))

    scheduler.start()
