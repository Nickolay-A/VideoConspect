"""
модуль для подготовки обекта с языками для общения бота с пользователем
"""
lang_obj = {
    'ru': {
        'button_restart': 'Перезапустить бота',
        'button_start': 'Начало работы',
        'button_help': 'Помощь',
        'button_about': 'О проекте',
        'message_hello': 'Привет! Я бот-помошник! Я делаю короткие конспекты длинных лекций. Давай помогу! Больше информации доступно по команде /help',
        'button_URL': 'Ссылка',
        'button_File': 'Файл',
        'button_speech': 'Пообщаться с ботом',
        'message_upload_method': 'Выберите способ загрузки файла',
        'message_help': """Для взаимодействия с ботом предусмотрены команды:
        /start   - активировать бота (используйте эту команду для перезапуска)
        /begin  - начать работу
        /help    - список доступных команд
        /about - о проекте
Для начала работы нажмите соответствующую кнопку на панели или напишите /begin и следуйте инструкциям. В любой другой непонятной ситуации воспользуйтесь возможностью перезапустить бота. """,
        'message_about': 'Бот предназначен для конспетирования лекций, вебинаров и документальных фильмов. Для работы достаточно отправить ему аудиофайл, либо передать ссылку на YouTube или Google Drive и следовать дальнейшим инструкциям.\n\nПроект сделан в рамках группового дипломного проекта\nУдовольствие от создания проекта получили: \nНиколай Бруцкий-Стемпковский \nПавел Коледа \nСергей Скороходов ',
        'message_speech': 'Давай поговорим)',
        'message_wait_url': 'Введите ссылку на видео в YouTube, либо ссылку на видеофайл или аудиофайл формата .mp3 на GDrive (не забудьте открыть доступ на него всем пользователям, у кого есть данная ссылка)',
        'message_wait_file': 'Прикрепите аудиофайл формата .mp3 (его размер не должен превышать 20 МБ)',
        'message_get_url': 'Принял ссылку:',
        'message_get_file': 'Принял файл:',
        'message_get_url_error': 'Полученную ссылку нельзя обработать ни одним сервисом, извините.',
        'message_get_file_error': 'Полученный файл нельзя обработать, извините.',
        'message_wait_lang': 'Выберите язык оригинала',
        'message_get_lang': 'Файлы приняты, начинаю работу, дождитесь ответного сообщения.',
        'message_work_done': 'Конспект готов! Теперь вы можете пообщаться с ботом и задать дополнительные вопросы по полученному конспекту. Нажмите для этого соответствующую кнопку.',
        'message_work_fail': 'Что-то пошло не так. Приносим свои извинения. Попробуйте повторить попытку позже.',
        # 'promt': 'Передаю тебе текст, который был получен с помощью другой нейросети. Она обработала аудиожорожку и выдала данный текст. Он может содержать ошибки. Опиши кратко ключевые моменты. Свой ответ напиши на русском языке',
        'promt': 'Ты полезный помощник по теме текста в прикрепленном файле. Твоя задача сперва сделать краткое содержание текста с выделением ключевых моментов и тезисов в предоставленном тексте в объеме, необходиомо для отражения всего материала, а далее отвечать на последующие вопросы по тексту которые тебе пришлют максимально подробно. Если пользователь попросит иное, то не выходить за рамки исходной темы. Свои ответы пиши на русском языке.',
    },
    'en': {
        'button_restart': 'Restart the bot',
        'button_start': 'Start',
        'button_help': 'Help',
        'button_about': 'About',
        'message_hello': 'Hello! I am an assistant bot! I create concise summaries of long lectures. Let me help you! More information is available with the command /help',
        'button_URL': 'Link',
        'button_File': 'File',
        'button_speech': 'Chat with the bot',
        'message_upload_method': 'Choose a file upload method',
        'message_help': 'Commands for interacting with the bot:\n        /start   - activate the bot (use this command to restart)\n        /begin  - start working\n        /help    - list of available commands\n        /about - about the project\nTo begin, press the corresponding button on the panel or type /begin and follow the instructions. In any other incomprehensible situation, take the opportunity to restart the bot.',
        'message_about': 'The bot is designed for summarizing lectures, webinars, and documentaries. To use it, simply send an audio file or provide a link from YouTube or Google Drive, and follow the subsequent instructions.\n\nThe project was made as part of a group graduation project\nThe following people enjoyed creating the project: \nNikolay Brutsky-Stempkovsky \nPavel Koleda \nSergey Skorokhodov',
        'message_speech': 'Let\'s have a chat)',
        'message_wait_url': 'Enter a link to a video on YouTube, or a link to a video or audio file in .mp3 format on GDrive (remember to grant access to anyone with the link)',
        'message_wait_file': 'Attach an audio file in .mp3 format (its size should not exceed 20 MB)',
        'message_get_url': 'Received link:',
        'message_get_file': 'Received file:',
        'message_get_url_error': 'The received link cannot be processed by any service, sorry.',
        'message_get_file_error': 'The received file cannot be processed, sorry.',
        'message_wait_lang': 'Choose the original language',
        'message_get_lang': 'Files received, starting the process, please wait for a response.',
        'message_work_done': 'Summary is ready! Now you can chat with the bot and ask additional questions about the generated summary. Press the appropriate button to do so.',
        'message_work_fail': 'Something went wrong. We apologize. Please try again later.',
        # 'promt': 'I am passing on to you the text that was generated using another neural network. It processed the audio track and produced this text. It may contain errors. Briefly describe the key points. Write your response in English.'
        'promt': 'You are a useful assistant on the topic of the text in the attached file. Your task is to first make an outline of the text, highlighting the key points and theses in the provided text to the extent necessary to reflect the entire material, and then to answer in as much detail as possible the follow-up questions on the text that is sent to you. If the user asks about something else, do not go beyond the original topic. Write your answers in English.'
    },
}

lang_dicts = {
    'ru': {'Английский' : 'en',
           'Русский'    : 'ru',
           'Немецкий'   : 'de',
           'Испанский'  : 'es',
           'Итальянский': 'it',},
    'en': {'English'    : 'en',
           'Russian'    : 'ru',
           'German'     : 'de',
           'Spanish'    : 'es',
           'Italian'    : 'it',},}
