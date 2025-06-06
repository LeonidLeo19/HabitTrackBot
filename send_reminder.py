from bot_instance import bot
from bd import AsyncSessionLocal, select, Habit, Habit_progress, User


async def send_reminder():
    async with AsyncSessionLocal() as session:
        users = await session.execute(select(User))
        users = users.scalars().all()

        for user in users:
            try:
                await bot.send_message(chat_id=user.tg_id, text="Don't forget about your habits! ✅")
            except Exception as e:
                print(f"Ошибка отправки напоминания пользователю {user.tg_id}: {e}")


async def check_strick():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Habit_progress).order_by(Habit_progress.date.desc()))
        habits_progress = result.scalars().all()
        
        users = await session.execute(select(User))
        users = users.scalars().all()

        streaks = {} 

        for habit_progress in habits_progress:
            habit_id = habit_progress.habit_id
            user_id = habit_progress.habit.user_id  

            if habit_progress.is_done:
                if habit_id not in streaks:
                    streaks[habit_id] = 1
                else:
                    streaks[habit_id] += 1
            else:
                streaks[habit_id] = 0
            if streaks[habit_id] >= 7:
                user = next((u for u in users if u.id == user_id), None)
                if user:
                    await bot.send_message(chat_id=user.tg_id, text="You have reached a 1-week streak!!!")

        return streaks

