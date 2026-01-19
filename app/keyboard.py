from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создание поля внешних кнопок
# inline_keyboard - список рядов кнопок, каждый ряд - список кнопок. text - текст кнопки
# callback_data - калбак вызов действия
options_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оставить отзыв', callback_data='accept_com')],
     [InlineKeyboardButton(text='Просмортеть отзывы', callback_data='read_com')]
])
comment_mark = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Просмотреть отзывы', callback_data='watch_com')],
    [InlineKeyboardButton(text='Вернуться назад', callback_data='home')]
])

return_mark = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Вернуться назад',
                                                                          callback_data='home')]])