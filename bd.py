from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload, relationship
from sqlalchemy.orm import declarative_base
import asyncio
from sqlalchemy import Column, Integer, String, create_engine, text, TIMESTAMP, Boolean
from sqlalchemy.future import select
from sqlalchemy import ForeignKey, desc

DATABASE_URL = "postgresql+asyncpg://username:password@localhost/databasename"
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer,nullable=False,unique=True)
    name = Column(String, nullable=False)
    created_at=Column(TIMESTAMP,nullable=False,server_default=text('CURRENT_TIMESTAMP'))
    habits = relationship("Habit", backref="user", cascade="all, delete-orphan")


class Habit(Base):
    __tablename__="habits"
    id= Column(Integer, primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    habit=Column(String,nullable=False)
    target_count=Column(Integer,nullable=False)
    created_at=Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

class Habit_progress(Base):
    __tablename__="habits_progress"
    id=Column(Integer,primary_key=True,nullable=False)
    habit_id=Column(Integer,ForeignKey('habits.id',ondelete='CASCADE'),nullable=False)
    current_count=Column(Integer)
    date=Column(TIMESTAMP,nullable=False,server_default=text('CURRENT_TIMESTAMP'))
    is_done=Column(Boolean,nullable=False)

async def add_user(tg_id: int, name: str):
    try:
        async with AsyncSessionLocal() as db:
            async with db.begin():
                new_user = User(tg_id=tg_id, name=name)
                db.add(new_user)
                await db.flush()
                await db.refresh(new_user)
    except Exception as e:
        # Логируем ошибку и сообщаем о проблеме
        print(f"Error during add_user: {e}")
        raise  # Перебрасываем ошибку для дальнейшей обработки

async def add_habit(tg_id: int, habit_name: str, target_count: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar()

        if not user:
            raise ValueError(f"User with tg_id {tg_id} not found")


        new_habit = Habit(
            user_id=user.id,
            habit=habit_name,
            target_count=target_count
        )
        session.add(new_habit)
        await session.flush()
        await session.refresh(new_habit)
        
        new_habit_progress=Habit_progress(
            habit_id=new_habit.id,
            current_count=0
        )
        session.add(new_habit_progress)
        await session.commit()


async def get_user_with_habits(tg_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar()
        return user


async def delete_habit(habit_name:str):
    async with AsyncSessionLocal() as session:
        habit= await session.execute(
            select(Habit).where(Habit.habit==habit_name)
        )
        del_habit=habit.scalar()
        if del_habit:
            await session.delete(del_habit)
            await session.commit()

async def get_user_habits(user_id):
    async with AsyncSessionLocal() as session:
        result= await session.execute(
            select(Habit).where(Habit.user_id==user_id)
        )
    user_habits=result.scalars().all()
    return user_habits


async def make_mark(habit_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Habit_progress).where(Habit_progress.habit_id == habit_id)
        )
        habit_progress = result.scalar_one_or_none()

        if habit_progress:
            habit_progress.current_count += 1

            # Проверяем, достигли ли мы целевого значения
            habit = await session.execute(select(Habit).where(Habit.id == habit_id))
            habit = habit.scalar_one_or_none()
            
            if habit and habit_progress.current_count >= habit.target_count:
                habit_progress.is_done = True 

            await session.commit()



async def del_mark(habit_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Habit_progress)
            .where(Habit_progress.habit_id == habit_id)
            .order_by(desc(Habit_progress.date))
            .limit(1)
        )
        habit_progress = result.scalar_one_or_none()
        if habit_progress:
            if habit_progress.current_count > 0:
                habit_progress.current_count -= 1
                
                # Если current_count меньше target_count, сбрасываем is_done
                habit = await session.execute(select(Habit).where(Habit.id == habit_id))
                habit = habit.scalar_one_or_none()

                if habit_progress.current_count < habit.target_count:
                    habit_progress.is_done = False
                
                await session.commit()
            else:
                return 0

            


async def get_progress(habit_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Habit_progress)
            .where(Habit_progress.habit_id == habit_id)
            .order_by(desc(Habit_progress.date))  # сортируем по дате создания
            .limit(1)  # берём только одну запись
        )
        habit_progress = result.scalar_one_or_none()
        if habit_progress:
            return habit_progress


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
