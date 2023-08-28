"""
модуль для извлечения аудиодорожки при поступлении ссылки
на видеоролик на YouTube
"""
import re

from datetime import datetime
from gdrive.gdrive import get_from_gdrive
from youtube.youtube import get_from_youtube


def get_audio_from_url(url: str, temp_dir: str, name: str) -> None:
    """
    Функция принимает на вход сслыку на файл
    путь к папке для созранения
    имя файла
    """
    # сделаем словарь, в котором сохраним регулярные выражения
    # для ссылок различных сервисов и файлообменников, а также
    # соответствующие им функции
    services = {
        'youtube': 
        (
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})',
        get_from_youtube
        ),
        'google drive':
        (
        r'https:\/\/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)\/',
        get_from_gdrive
        )
    }

    for service, (regex, func) in services.items():
        match = re.search(regex, url)
        if match:
            print(f'Ресурс: {service}')
            # вызов функции для сохранения аудиодорожки
            func(url=url, temp_dir=temp_dir, name=name)
            # выход из цикла
            break
    else:
        # сюда мы попали в случае, если переданная ссылка не подходит
        # по формату ни к одному сервису
        print('Полученная ссылка не соответствует ни одному доступному сервису')
        return None

    return None


if __name__ == '__main__':
    import os
    import tempfile

    # создадим временную папку для работы приложения в TEMP
    tmp_dir = os.path.join(tempfile.gettempdir(), 'Video Conspect')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    get_audio_from_url(
      url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      temp_dir=tmp_dir,
      name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    )
    get_audio_from_url(
      url='https://drive.google.com/file/d/1CwfESzBf_v5ffG_1BNLYE93COuwIRsuB/view?usp=sharing',
      temp_dir=tmp_dir,
      name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    )
    get_audio_from_url(
      url='https://drive.google.com/file/d/13onW7WOt-m0o1fDxjzK5Q1XvAYVjgbPK/view?usp=drivesdk',
      temp_dir=tmp_dir,
      name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    )
