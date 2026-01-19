from aiogram.fsm.state import State, StatesGroup


# Сохраняем состояние, когда человек оставляет отзыв о каком-то вузе
class AcceptCom(StatesGroup):
    university = State()
    university_sub = State()
    text = State()
    grade = State()
    correct = State()

class ReadCom(StatesGroup):
    university = State()
    university_sub = State()
