"""
модуль обрабатывает ссылку на файл на GoogleDrive и сохраняет
.mp3 файл
"""
import os
import re
import sys
import base64
import tempfile
from tempfile import NamedTemporaryFile

import googleapiclient
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

sys.path.insert(0, './')

from getaudio.fromfile import get_audio_from_file


# загрузим переменные окружения из .env файла
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
# загрузим содержимое json файла из переменной окружения
encoded_json = os.getenv('GDRIVE_TOKEN')

# декодируем json файл
decoded_json = base64.b64decode(encoded_json).decode('utf-8')

# создание временного файла и запись в него декодированного JSON
with NamedTemporaryFile(mode='w', delete=False) as temp_file:
    temp_file.write(decoded_json)
    temp_file_path = temp_file.name

def get_from_gdrive(url: str,
                    temp_dir: str,
                    name: str) -> None:
    """
    Функция скачивает файл по ссылке с Google Drive и вызывает
    функцию fromfile для получения аудиодорожки
    """
    # параметры аутентификации
    credentials = Credentials \
      .from_service_account_file(temp_file_path)

    # Создание объекта сервиса
    service = build('drive', 'v3', credentials=credentials)

    # получим id файла
    regex = r'https:\/\/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)\/'
    match = re.search(regex, url)
    file_id = match.group(1)

    # Получение метаданных файла
    try:
        file = service.files().get(fileId=file_id).execute()
    except HttpError:
        return None
    # Извлечение имени файла
    file_name = file['name']

    # Выполнение запроса для скачивания файла
    request = service.files().get_media(fileId=file_id)

    # Сохранение содержимого файла на локальный диск
    output_file = os.path.join(temp_dir, file_name)
    file_handle = open(output_file, 'wb')
    downloader = googleapiclient.http.MediaIoBaseDownload(file_handle, request)

    done = False
    while done is False:
        _, done = downloader.next_chunk()

    # Закрытие файла
    file_handle.close()

    # вызов функции для извлечения звука
    get_audio_from_file(path=output_file, temp_dir=temp_dir, name=name)

    return None


if __name__ == '__main__':
    from datetime import datetime


    with tempfile.TemporaryDirectory() as temp_dir_:
        get_from_gdrive(
            url= \
            'https://drive.google.com/file/d/1CwfESzBf_v5ffG_1BNLYE93COuwIRsuB/view?usp=sharing',
            temp_dir=temp_dir_,
            name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        )
        get_from_gdrive(
            url= \
            'https://drive.google.com/file/d/1tyIWVVw5DaHJL1ZBv6eGzpC8xU_JkZg1/view?usp=sharing',
            temp_dir=temp_dir_,
            name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        )
