# Импорт из библиотеки aiogram
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart

# Импорт конопок из другого фвйла
import app.keyboard as kb
# Импорт классов с состоянием из другого файла
from app.statecom import AcceptCom, ReadCom

# Импорт БД
import sqlite3 as sql
# Подключение к диспетчеру
router = Router()


# Если введена команда старт, то сработает start()
@router.callback_query(F.data == 'home')
@router.message(CommandStart())
async def start(message: Message | CallbackQuery, state: FSMContext):
    # Подключение картинки
    photo = FSInputFile(r'./image/img_start.png')
    # Отправка ответа(Изображение с подписью) reply_markup - привязка кнопок к сообщению
    if isinstance(message, Message):
        # Если мы сюда пришли по сообщению
        await message.answer_photo(photo,
                        f'Привет, {message.chat.first_name}!\nС помощью этого бота ты сможешь оставить отзыв о '
                            f'своём вузе.\nА также ты сможешь прочитать отзывы других людей о конкретном институте и '
                            f'сделать правильный выбор при поступлении 👨‍🎓', reply_markup=kb.options_start)
    else: # Если сюда пришли из кнопки
        await message.message.answer_photo(photo,
                        f'Привет, {message.message.chat.first_name}!\nС помощью этого бота ты сможешь оставить отзыв о '
                        f'своём вузе.\nА также ты сможешь прочитать отзывы других людей о конкретном институте и '
                        f'сделать правильный выбор при поступлении 👨‍🎓',
                                           reply_markup=kb.options_start)
    await state.clear() # Очищаем состояние


@router.callback_query(F.data == 'accept_com')
async def comment(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await callback.message.answer('Пожалуйста, оставляйте честный отзыв о своём вузе.\n'
                          'Сохранение отзывов происходит анонимно')
    # Готовимся к сохранению состояния
    await state.set_state(AcceptCom.university)
    # Отправка сообщения
    await callback.message.answer('Введите название вашего университета')


# Если до этого приготовились сохранять нужное состояние (Название вуза)
@router.message(AcceptCom.university)
async def comment_university(message: Message, state: FSMContext):
    # Сохраняем название вуза
    await state.update_data(university=message.text)
    # Готовимся ловить конкретное подразделение в вузе
    await state.set_state(AcceptCom.university_sub)
    # Отправка сообщения пользователю
    await message.answer('Пожалуйста, введите название своего подразделения внутри вуза')


@router.message(AcceptCom.university_sub)
async def comment_university_sub(message: Message, state: FSMContext):
    # Сохраняем название подразделения
    await state.update_data(university_sub=message.text)
    # Готовимся ловить сам отзыв на вуз
    await state.set_state(AcceptCom.text)
    # Отправка пользователю просьбы скинуть конкретный отзыв
    await message.answer('Пожалуйста, введите ваш отзыв')


@router.message(AcceptCom.text)
async def comment_text(message: Message, state: FSMContext):
    # Сохраняем отзыв
    await state.update_data(text=message.text)
    # Готовимся ловить оценку
    await state.set_state(AcceptCom.grade)
    await message.answer('Пожалуйста, введите вашу итоговую оценку(по 10-ой шкале)')


@router.message(AcceptCom.grade)
async def comment_grade(message: Message, state: FSMContext):
    # Проверка оценки
    if str(message.text).isdigit() and 1 <= int(message.text) <= 10:
        # Сохраняем оценку
        await state.update_data(grade=message.text)
        await state.set_state(AcceptCom.correct)
        # Получаем информацию
        data = await state.get_data()
        await message.answer(f"Название вуза: {data['university']}\n"
                             f"Название подразделения: {data['university_sub']}\n"
                             f"Ваш отзыв: {data['text']}\n"
                             f"Ваша итоговая оценка: {data['grade']}")
        await message.answer('Вы подтверждаете корректность данных?(Да/Нет)')
    else:
        await message.answer('Вы ввели некорректную оценку. Она должна быть от 1 до 10.\n'
                             'Повторите ввод')


@router.message(AcceptCom.correct)
async def comment_correct(message: Message, state: FSMContext):
    # Ловим ответ пользователя
    mes = str(message.text).lower().strip()
    if mes not in ['да', 'нет']: # сли он некорректен
        await message.answer('Введите Да или Нет')
    elif mes == 'да': # Если да, то сохраняем отзыв
        await message.answer('Спасибо за отзыв')
        # Подключение к бд
        conn = sql.connect('database_comment.db')
        # Создание курсора, с помощью которого будут вводиться команды для работы с бд
        cursor = conn.cursor()
        # Если нет общей таблицы с универами, то создаём её
        cursor.execute('create table if not exists university (id integer primary key, name text)')
        # Получаем данные из состояния
        data = await state.get_data()
        # Обнуляем состояние
        await state.clear()
        # Получаем название вуза
        university = data['university'].lower()
        # Если вуз есть в бд
        if university in cursor.execute('select name from university').fetchall():
            # Добавляем подразделение, отзыв, оценку в таблицу вуза
            cursor.execute(f'insert into {university} (sub, comment, grade) values(?, ?, ?)',
                           (data['university_sub'].lower(), data['text'], int(data['grade'])))
            # Сохраняем изменения
            conn.commit()
        else: # Если вуза не было в общем списке
            # Добавляем вуз в таблицу с вузами
            cursor.execute('insert into university(name) values(?)', (university,))
            conn.commit() # Сохраняем изменения
            # Создаём таблицу вуза и сохраняем в неё отзыв
            cursor.execute(f'create table if not exists {university} (sub text, comment text, '
                           f'grade integer)')
            cursor.execute(f'insert into {university} (sub, comment, grade) values(?, ?, ?)',
                           (data['university_sub'].lower(), data['text'], int(data['grade'])))

            conn.commit()
        # Закрываем бд
        conn.close()
    else: # Даём пользователю переписать отзыв
        await message.answer('Вы можете переписать отзыв')
        await state.clear()
        await message.answer('Введите название своего университета')
        await state.set_state(AcceptCom.university)


@router.callback_query(F.data == 'read_com') # чтение отзывов
async def read_com(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await callback.message.answer('Введите название интересующего вас вуза')
    await state.set_state(ReadCom.university)


@router.message(ReadCom.university)
async def university_read(message: Message, state: FSMContext):
    # Получаем название вуза
    university = str(message.text).lower()
    # Подключаемся к бд и создаём курсор
    conn = sql.connect('database_comment.db')
    cursor = conn.cursor()
    # Если универ есть в таблице
    if (university,) in cursor.execute('select name from university').fetchall():
        # Выводим статистику: Средняя оценка, направления, на которые есть отзывы
        photo = FSInputFile(r'./image/img.png')
        grade = str(cursor.execute(f'select avg(grade) from {university}').fetchone()[0])
        sub = cursor.execute(f'select distinct(sub) from {university}').fetchall()
        sub_string = 'Подразделения, на которые есть отзывы:\n'
        for k, subb in enumerate(sub):
            sub_string += f'{k + 1}) {subb[0].upper()}\n'
        await message.answer_photo(photo, f'{university.upper()}\n'
                                          f'Средняя оценка: {grade}\n{sub_string}')
        conn.close()
        await message.answer('Выберите подразделение и выпишите его')
        await state.update_data(university=university)
        await state.set_state(ReadCom.university_sub)
    else:
        conn.close()
        await message.answer('По вашему вузу нет информации 😢😢😢😢😥', reply_markup=kb.return_mark)
        await state.clear()

@router.message(ReadCom.university_sub)
async def university_sub(message: Message, state: FSMContext):
    await state.update_data(university_sub=str(message.text).lower())
    # Вывод комментариев
    data = await state.get_data()
    #Подключение к бд
    conn = sql.connect('database_comment.db')
    cursor = conn.cursor()
    # ЕСЛИ ПОЛЬЗОВАТЕЛЬ НЕПРАВИЛЬНО ВВЁЛ НАЗВАНИЕ ПОДРАЗДЕЛЕНИЯ
    if (data['university_sub'],) not in cursor.execute(f'select distinct(sub) from {data["university"]}').fetchall():
        await message.answer('По запрашиваемому подразделению не было найдено отзывов.\nВыберите подразделение из '
                             'списка, указанного выше')
        conn.close()
    else: # Иначе выводим комментарии
        comments = ''
        for comm in cursor.execute(f'select * from {data["university"]}').fetchall():
            comments += f'Итоговая оценка: {comm[-1]}\nОтзыв: {comm[-2]}\n\n'
        await message.answer(f'Отзывы:\n{comments}', reply_markup=kb.return_mark)
        #   Очищаем состояние
        await state.clear()
        conn.close()









