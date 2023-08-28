"""
модуль, который который рабтает с Телеграмм-ботом
t.me/VideoConspectBot
"""
import os
import sys
import tempfile
import subprocess
from concurrent.futures import ThreadPoolExecutor

import telebot
from dotenv import load_dotenv
from telebot import types

sys.path.insert(0, './')
sys.path.insert(0, './getaudio')

from getaudio.fromfile import get_audio_from_file
from getaudio.fromurl import get_audio_from_url
from claude.claudeapi import request_without_attachment, request_with_attachment
from makelang import lang_obj, lang_dicts


# загрузим переменную окружения из .env файла
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# загрузим токен из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

# передаем токен для бота
bot = telebot.TeleBot(BOT_TOKEN)

# возможные состояния пользователя
USER_CHOOSE_LANG  = 0  # соответсвует перезапущенному состоянию бота
NOT_WORKING_STATE = 1
WAITING_FOR_URL   = 2
WAITING_FOR_FILE  = 3
WAITING_FOR_LANG  = 4
TALKING_WITH_BOT  = 5

# словарь для хранения состояний пользователей
user_states   = {}
# словарь для хранения языка, на котором общается пользователь
user_lang   = {}
# словарь для хранения запросов
# должен иметь структуру:
# id чата: [id сообщения, метод (url, file), объект(ссылка или file_id), язык]
user_requests = {}
# словарь состояния пользователя, посылал ли он файлы (bool)
user_send_requests = {}

# словарь доступных языков (для интерфейса)
bot_lang_dict = {'Англиский/English': 'en',
                 'Русский/Russian'  : 'ru',}
bot_langueges = bot_lang_dict.keys()

# развернем словарь общения с пользователем, чтобы получить перечень
# отображений одной и той же команды на разных языках
possible_messages = {}
FIRST_KEY = list(lang_obj.keys())[0]
for msg in lang_obj.get(FIRST_KEY).keys():
    possible_messages[msg] = []
    for key in lang_obj:
        possible_messages[msg].append(lang_obj.get(key).get(msg))

# создадим временную папку для работы приложения в TEMP
tmp_dir = os.path.join(tempfile.gettempdir(), 'Video Conspect')
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# словарь для хранения списка очереди
user_queue_positions = {}

# Создаем executor (очередь) с максимальным количеством потоков, равным 3 (временно 1)
executor = ThreadPoolExecutor(max_workers=1)

def get_state(user_id):
    """
    Функция для получения состояния пользователя
    """
    return user_states.get(user_id, 0)

def set_state(user_id, state):
    """
    Функция для установки состояния пользователя
    """
    user_states[user_id] = state

def get_lang(user_id):
    """
    Функция для получения языка пользователя
    """
    return user_lang.get(user_id)

def set_lang(user_id, lang):
    """
    Функция для установки языка пользователя
    """
    user_lang[user_id] = lang

@bot.message_handler(commands=['start'])
def _start(message):
    """
    Функция, предлагающая выбрать пользователю язык интерфейса
    Преварительный обработчик команды /start
    установливает состояние пользователя 'пользователь выбирает язык'
    """
    set_state(message.chat.id, USER_CHOOSE_LANG)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for bot_languege in bot_langueges:
        buttons.append(types.KeyboardButton(bot_languege))
    buttons.append(types.KeyboardButton('Перезапустить бота/Restart the bot'))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        'Выберите язык для общения и работы. Choose a language for communication and work.',
        reply_markup=markup)

def start(message):
    """
    Обработчик команды /start
    установливает состояние пользователя 'не в работе'
    """
    set_state(message.chat.id, NOT_WORKING_STATE)
    user_send_requests[message.chat.id] = False
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_about']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_hello'],
        reply_markup=markup)

@bot.message_handler(commands=['begin'])
def begin(message):
    """
    Обработчик команды /begin
    """
    set_state(message.chat.id, NOT_WORKING_STATE)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_URL']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_File']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_upload_method'],
        reply_markup=markup)

@bot.message_handler(commands=['help'])
def _help(message):
    """
    Обработчик команды /help
    """
    set_state(message.chat.id, NOT_WORKING_STATE)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_help'],
        reply_markup=markup)

@bot.message_handler(commands=['about'])
def about(message):
    """
    Обработчик команды /about
    """
    set_state(message.chat.id, NOT_WORKING_STATE)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_about'],
        reply_markup=markup)

@bot.message_handler(commands=['speech'])
def speech(message):
    """
    Обработчик команды /speech
    команда не должна быть известна пользователю
    доступна после отправки видео,
    должно о чем быть говорить
    """
    set_state(message.chat.id, TALKING_WITH_BOT)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_about']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_speech'],
        reply_markup=markup)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == USER_CHOOSE_LANG,
                     content_types=['text'])
def get_text_messages_choose_lang_state(message):
    """
    Обработчик текстовых сообщений в режиме 'Пользователь выбирает язык'
    """
    if message.text in bot_langueges:
        set_lang(message.chat.id, bot_lang_dict[message.text])
        start(message)
    elif message.text == 'Перезапустить бота/Restart the bot' \
        or message.text in possible_messages['button_restart']:
        _start(message)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == NOT_WORKING_STATE,
                     content_types=['text'])
def get_text_messages_free_state(message):
    """
    Обработчик текстовых сообщений в режиме 'Знакомства с ботом'
    """
    if message.text in possible_messages['button_start']:
        begin(message)
    elif message.text in possible_messages['button_restart']:
        _start(message)
    elif message.text in possible_messages['button_help']:
        _help(message)
    elif message.text in possible_messages['button_about']:
        about(message)
    elif message.text in possible_messages['button_URL']:
        wait_text_messages_not_working_state(message)
    elif message.text in possible_messages['button_File']:
        wait_document_messages_not_working_state(message)
    elif message.text in possible_messages['button_speech']:
        speech(message)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == WAITING_FOR_URL,
                     content_types=['text'])
def get_text_messages_wait_url_state(message):
    """
    Обработчик текстовых сообщений в режиме 'ожидания ссылки'
    """
    if message.text in possible_messages['button_start']:
        begin(message)
    elif message.text in possible_messages['button_restart']:
        _start(message)
    elif message.text in possible_messages['button_help']:
        _help(message)
    elif message.text in possible_messages['button_about']:
        about(message)
    elif message.text in possible_messages['button_speech']:
        speech(message)
    else:
        get_text_messages_wait_obj_state(message)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == WAITING_FOR_FILE)
def get_text_messages_wait_file_state(message):
    """
    Обработчик текстовых сообщений в режиме 'ожидания файла'
    """
    if message.text in possible_messages['button_start']:
        begin(message)
    elif message.text in possible_messages['button_restart']:
        _start(message)
    elif message.text in possible_messages['button_help']:
        _help(message)
    elif message.text in possible_messages['button_about']:
        about(message)
    elif message.text in possible_messages['button_speech']:
        speech(message)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == WAITING_FOR_LANG,
                     content_types=['text'])
def get_text_messages_wait_lang_state(message):
    """
    Обработчик текстовых сообщений в режиме 'ожидания языка'
    """
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')
    lang_dict = lang_dicts[cur_user_lang]

    if message.text in possible_messages['button_start']:
        begin(message)
    elif message.text in possible_messages['button_restart']:
        _start(message)
    elif message.text in possible_messages['button_help']:
        _help(message)
    elif message.text in possible_messages['button_about']:
        about(message)
    elif message.text in possible_messages['button_speech']:
        speech(message)
    elif message.text in lang_dict.keys():
        get_the_lang(message)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == TALKING_WITH_BOT,
                     content_types=['text'])
def get_text_messages_talking_with_bot(message):
    """
    Обработчик текстовых сообщений в режиме 'Поболтать с ботом'
    """
    if message.text in possible_messages['button_start']:
        begin(message)
    elif message.text in possible_messages['button_restart']:
        _start(message)
    elif message.text in possible_messages['button_help']:
        _help(message)
    elif message.text in possible_messages['button_about']:
        about(message)
    else:
        send_message_to_bot(message)

def wait_text_messages_not_working_state(message):
    """
    Функция предлагает ввести ссылку
    """
    set_state(message.chat.id, WAITING_FOR_URL)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_wait_url'],
        reply_markup=markup)

def wait_document_messages_not_working_state(message):
    """
    Функция предлагает загрузить файл
    """
    set_state(message.chat.id, WAITING_FOR_FILE)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_wait_file'],
        reply_markup=markup)

def get_text_messages_wait_obj_state(message):
    """
    Обработчик полученной ссылки
    """
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    url = message.text

    bot.send_message(message.from_user.id, f"{lang_obj[cur_user_lang]['message_get_url']} {url}",)
    user_requests[message.chat.id] = [message.message_id, 'url', url]

    waiting_for_lang(message)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == WAITING_FOR_FILE,
                     content_types=['audio'])
def get_file_messages_wait_obj_state(message):
    """
    Обработчик полученного файла
    """
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    file_id = None

    # скачивание аудио файла
    if message.content_type == 'audio':
        file = message.audio
        file_id = file.file_id

    if file_id and file.file_size <= 20 * 1024 * 1024:
        file_name = file.file_name
        bot.send_message(message.from_user.id,
                         f"{lang_obj[cur_user_lang]['message_get_file']} {file_name}",)

        user_requests[message.chat.id] = [message.message_id, 'file', file]

        waiting_for_lang(message)
    else:
        bot.send_message(
            message.from_user.id,
            lang_obj[cur_user_lang]['message_get_file_error'],)

def waiting_for_lang(message):
    """
    Функция, предлагающая выбрать язык после отправки файла
    """
    set_state(message.chat.id, WAITING_FOR_LANG)
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')
    lang_dict = lang_dicts[cur_user_lang]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    for languege in lang_dict.keys():
        buttons.append(types.KeyboardButton(languege))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_wait_lang'],
        reply_markup=markup)

def get_the_lang(message):
    """
    Функция, обрабатывающая полученный язык
    запускает обработку файла
    """
    set_state(message.chat.id, NOT_WORKING_STATE)
    user_send_requests[message.chat.id] = True  # теперь пользователь может общаться с ботом
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')
    lang_dict = lang_dicts[cur_user_lang]

    user_requests[message.chat.id].append(lang_dict[message.text])

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_about']))
    if user_send_requests.get(message.chat.id, False):
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
    markup.add(*buttons)
    bot.send_message(
        message.from_user.id,
        lang_obj[cur_user_lang]['message_get_lang'],
        reply_markup=markup)
    # при работе без очереди
    # work_with_requests(message)
    call_swork_with_requests_func(message)
    message_id = user_requests[message.chat.id][0]
    queue_id = f'{message.from_user.id}_{message_id}'
    if queue_id in user_queue_positions:
        bot.send_message(
        message.from_user.id,
        f'Ваше место в очереди: {user_queue_positions[queue_id]}')

def call_swork_with_requests_func(message):
    """
    Функция, с реализацией очереди
    """
    message_id = user_requests[message.chat.id][0]
    # запускаем функцию work_with_requests в отдельном потоке
    future = executor.submit(work_with_requests, message, *user_requests[message.chat.id])
    if executor._work_queue.qsize() > 0:
        user_queue_positions[f'{message.from_user.id}_{message_id}'] = executor._work_queue.qsize()

    future.add_done_callback(lambda _: update_queue_positions()
                                    if any(user_queue_positions.values())
                                    else None)
    return future  # возвращает объект Future, которым можно управлять

def update_queue_positions():
    """
    Функция, обновления очереди
    """
    # перебираем всех пользователей
    for user_id in user_queue_positions:
        # уменьшаем номер позиции на 1
        user_queue_positions[user_id] -= 1

    queue_copy = user_queue_positions.copy()

    for user_id, position in queue_copy.items():
        if position <= 0:
            del user_queue_positions[user_id]
        else:
            notify_queue_position(user_id, position)
    for user_id, position in queue_copy.items():
        if position == 1:
            del user_queue_positions[user_id]

def notify_queue_position(user_id, position):
    """
    Функция извещения пользователя о месте в очереди
    """
    if user_id in user_queue_positions and position > 1:
        bot.send_message(user_id.split('_')[0],
                         f'Ваше место в очереди: {position}')

def work_with_requests(message, message_id, method, obj, lang):
    """
    Функция обрабатывает файл, пришедший от пользователя
    """
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    chat_id = message.chat.id

    # определим имена и пути, под которыми будут сохранены файлы
    name_for_files = f'{chat_id}_{message_id}_{lang}'
    # пути к файлам
    audio_path = os.path.join(tmp_dir, name_for_files + '.mp3')
    row_text_path = os.path.join(tmp_dir, name_for_files + '.txt')
    summ_text_path = os.path.join(tmp_dir, name_for_files + '_summ.txt')

    # получение аудио
    if method == 'url':
        get_audio_from_url(
            url=obj,
            temp_dir=tmp_dir,
            name=name_for_files)
    elif method == 'file':
        # Загрузка файла
        file_info = bot.get_file(obj.file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)
        # Сохранение файла
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = os.path.join(temp_dir, obj.file_name)
            with open(destination, 'wb') as temp_file:
                temp_file.write(downloaded_file)
            get_audio_from_file(
                path=destination,
                temp_dir=tmp_dir,
                name=name_for_files)

    # получение текста
    if os.path.exists(audio_path):
        # блок кода, если работать через subprocess
        current_file_path = os.path.dirname(__file__)
        current_file_path = current_file_path.replace('\\', '/')
        script_path = os.path.join(current_file_path,
                                   './gettranscribe_fast_whisper/fromaudio_fast_whisper.py')

        # формируем команду с передачей аргумента как одной строки
        command = ['python', script_path, '--path', audio_path]

        # запускаем процесс и захватываем вывод
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        # получаем стандартный вывод и стандартный поток ошибок
        output = result.stdout
        error = result.stderr

        # обрабатываем вывод и ошибки по необходимости
        print(f"Стандартный вывод: {output}")
        print(f"Стандартный поток ошибок: {error}")

        # код, если вызываем в этом же процессе
        # get_text(audio_path)

    # получение конспекта
    if os.path.exists(row_text_path):
        request_with_attachment(chat_id, row_text_path, cur_user_lang)

    # последовательная отправка файлов
    # сырой текст
    if os.path.exists(row_text_path):
        with open(row_text_path, 'rb') as text_file:
            bot.send_document(chat_id, text_file)

    # конспект
    if os.path.exists(summ_text_path):
        with open(summ_text_path, 'rb') as text_file:
            bot.send_document(chat_id, text_file)
        with open(summ_text_path, 'r', encoding='utf-8') as text_file:
            summ_text = text_file.read() + '\n\n'
            summ_text_escort = lang_obj[cur_user_lang]['message_work_done']
    else:
        summ_text = ''
        summ_text_escort = lang_obj[cur_user_lang]['message_work_fail']

    # Проверяем, есть ли у пользователя открытая клавиатура
    if message.reply_markup and isinstance(message.reply_markup, types.ReplyKeyboardMarkup):
        # Если есть, сохраняем текущую клавиатуру
        markup = message.reply_markup
    else:
        # Иначе создаем новую клавиатуру
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
        buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_about']))
        if user_send_requests.get(message.chat.id, False):
            buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_speech']))
        markup.add(*buttons)
    bot.send_message(message.chat.id,
                    summ_text + summ_text_escort,
                    reply_markup=markup)

    # удалим аудиодорожку и текстовые файлы
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f'Файл {audio_path} удален')
    if os.path.exists(row_text_path):
        os.remove(row_text_path)
        print(f'Файл {row_text_path} удален')
    if os.path.exists(summ_text_path):
        os.remove(summ_text_path)
        print(f'Файл {summ_text_path} удален')

def send_message_to_bot(message):
    """
    Функция, которая позволяет поговорить с ботом
    вызывает функцию request_withot_attachment
    """
    # получим язык пользователя для данной сессии
    # если язык не выбран, будет назначен русский
    cur_user_lang = user_lang.setdefault(message.chat.id, 'ru')

    # получаем ответ от LLM
    reply = request_without_attachment(message.chat.id, message.text)
    if reply is None:
        reply = lang_obj[cur_user_lang]['message_work_fail']

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_restart']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_start']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_help']))
    buttons.append(types.KeyboardButton(lang_obj[cur_user_lang]['button_about']))
    markup.add(*buttons)
    bot.send_message(message.from_user.id,
                     reply,
                     reply_markup=markup)


bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть
