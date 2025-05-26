from aiogram import Dispatcher, Router, Bot
from aiogram.filters import StateFilter, callback_data, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from bd import add_user, add_habit, delete_habit, get_user_with_habits,get_user_habits,make_mark,del_mark, get_progress
from update import start_scheduler

Token='YourBotToken'
bot=Bot(token=Token)
Storage = MemoryStorage()
dp=Dispatcher(storage=Storage)
router=Router()

class Form(StatesGroup):
    habbit=State()
    times=State()


help_button=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='main', callback_data='help')]
    ]
)


kb_help=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='see all habbits', callback_data='all_habbits')],
        [InlineKeyboardButton(text='add new habbit', callback_data='add_habbit')],
        [InlineKeyboardButton(text='delete a habbit', callback_data='del_habbit')],
        [InlineKeyboardButton(text='mark as done', callback_data='marks')],
        [InlineKeyboardButton(text='delete mark', callback_data='delite_mark')],
        [InlineKeyboardButton(text='check progress', callback_data='check')]
    ]
)
async def make_kb_del_habbits(user_id):
    user_habits= await get_user_habits(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='return', callback_data='help')],
            [InlineKeyboardButton(text=i.habit, callback_data=f'hab_{i.habit}') for i in user_habits]
        ]
    )
async def make_kb_mark_habbits(user_id):
    user_habits= await get_user_habits(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='return', callback_data='help')],
            [InlineKeyboardButton(text=i.habit, callback_data=f'habb_{i.habit}') for i in user_habits]
        ]
    )

async def make_kb_del_mark_habbits(user_id):
    user_habits= await get_user_habits(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='return', callback_data='help')],
            [InlineKeyboardButton(text=i.habit, callback_data=f'habbi_{i.habit}') for i in user_habits]
        ]
    )

@router.message(Command('start'))
async def Start(message: Message):
    user_id = int(message.from_user.id)
    try:
        user = await get_user_with_habits(user_id)
    except Exception as e:
        await message.answer("Sorry, the service is currently unavailable. Please try again later.")
        print(f"Error fetching user data: {e}")
        return
    
    if user:
        await message.answer(f'Hello {user.name}', reply_markup=help_button)
    else:
        await message.answer('Hello! I am your assistant. Click main to see all commands available', reply_markup=help_button)
        name = message.from_user.first_name
        try:
            await add_user(user_id, name)
        except Exception as e:
            await message.answer("Sorry, the service is currently unavailable. Please try again later.")
            print(f"Error adding user: {e}")


@router.callback_query(lambda c: c.data=='add_habbit')
async def cmd_add_habbit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Write a new habit in the chat:')
    await state.set_state(Form.habbit)
    
@router.message(StateFilter(Form.habbit))
async def add_habbit(message: Message, state: FSMContext):
    new_habbit = message.text
    if not new_habbit.strip():
        await message.answer("Message is incorrect. Try again!", reply_markup=help_button)
        return
    else:
        await state.update_data(habbit=new_habbit)
        await message.answer(f'Your new habit is {new_habbit}')
        await message.answer('How many times per day you need to do this habit?')
        await state.set_state(Form.times)

@router.message(StateFilter(Form.times))
async def habit_times(message: Message, state: FSMContext):
    if message.text.isdigit():
        habit_data = await state.get_data()
        habit_name = str(habit_data['habbit'])
        habit_time = int(message.text)
        user = await get_user_with_habits(message.from_user.id)
        if user:
            # user_id = user.id
            try:
                await add_habit(user.tg_id, habit_name, habit_time)
                await message.answer('Habit added successfully!', reply_markup=help_button)
            except:
                await message.answer('Sorry, the service is currently unavailable. Please try again later.')
        else:
            await message.answer('User not found in database.', reply_markup=help_button)
        await state.clear()

@router.callback_query(lambda c: c.data=='help')
async def btn_help(callback:CallbackQuery):
    await callback.message.edit_text('You can choose one of this actions',reply_markup=kb_help)

@router.callback_query(lambda c: c.data=='del_habbit')
async def btn_del(callback:CallbackQuery):
    user_id=await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)
    if user_habits:
        await callback.message.edit_text('choose a habbit that you want to delete',reply_markup=await make_kb_del_habbits(user_id.id))
    else:
        await callback.answer("You don't have any habbits yet")

@router.callback_query(lambda c: c.data.startswith('hab_'))
async def delite_hab(callback:CallbackQuery):
    habbit= callback.data.split('_')[1]
    try:
        await delete_habit(habbit)
    except:
        await callback.message.edit_text('Sorry, the service is currently unavailable. Please try again later.')
        return
    await callback.message.edit_text(f'You deleted {habbit}', reply_markup=help_button)

@router.callback_query(lambda c: c.data == 'all_habbits')
async def all_habbits(callback: CallbackQuery):
    user_id = await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)
    if user_habits:
        habit_names = [habit.habit for habit in user_habits]
        await callback.message.edit_text(f'These are all your habits:\n' + "\n".join(habit_names), reply_markup=help_button)
    else:
        await callback.answer("You don't have any habits yet")


@router.callback_query(lambda c: c.data=='marks')
async def marks(callback: CallbackQuery):
    user_id=await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)
    if user_habits:
        await callback.message.edit_text('Choose a habbit to mark as done', reply_markup=await make_kb_mark_habbits(user_id.id))
    else:
        await callback.answer("You don't have any habbits yet")

@router.callback_query(lambda c: c.data.startswith('habb_'))
async def mark_habb(callback:CallbackQuery):
    habbit=callback.data.split('_')[1]
    user_id=await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)
    for habits in user_habits:
        if habbit==habits.habit:
            await make_mark(habits.id)
            count= await get_progress(habits.id)
            if count.current_count==habits.target_count:
                await callback.message.edit_text(f'You achived your goal you have already done this habbit {count.current_count} times🥳🥳🥳',reply_markup=help_button)
            return

@router.callback_query(lambda c: c.data=='delite_mark')
async def delites(callback:CallbackQuery):
    user_id=await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)
    if user_habits:
        await callback.message.edit_text('Choose mark that you want to delete', reply_markup=await make_kb_del_mark_habbits(user_id.id))
    else:
        await callback.answer("You don't have any habbits yet")

@router.callback_query(lambda c: c.data.startswith('habbi_'))
async def delite_mark(callback: CallbackQuery):
    habbit = callback.data.split('_')[1]
    user_id=await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)
    for habits in user_habits:
        if habbit==habits.habit:
            a= await del_mark(habits.id)
            if a==0:
                await callback.message.edit_text("You haven't any progress in this habbit",reply_markup=help_button)
    return


@router.callback_query(lambda c: c.data == 'check')
async def check(callback: CallbackQuery):
    user_id = await get_user_with_habits(callback.from_user.id)
    user_habits = await get_user_habits(user_id.id)

    text = 'Here is your progress:\n\n'
    for habit in user_habits:
        progress_value = await get_progress(habit.id)
        text += f" {habit.habit}: {progress_value.current_count}\n"

    await callback.message.edit_text(text,reply_markup=help_button)


async def main():
    start_scheduler()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__=="__main__":
    asyncio.run(main())