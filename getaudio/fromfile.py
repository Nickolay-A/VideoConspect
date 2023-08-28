"""
модуль для извлечения аудидорожки при поступлении файла
"""
import shutil
import tempfile
import os

from moviepy.editor import AudioFileClip


def get_audio_from_file(path: str, temp_dir: str, name: str) -> None:
    """
    Функция принимает на вход путь к текущему расположению файла
    """
    old_name = os.path.basename(path)
    file_extension = old_name.split('.')[-1]
    name += '.mp3'

    if file_extension.lower() == 'mp3':
        source_file = path
        destination_file = os.path.join(temp_dir, name)
        shutil.copy2(source_file, destination_file)
    elif file_extension.lower() in ('mp4', 'avi', 'mkv', 'mov', 'mpeg', 'mpg', 'flv', 'wmv'):
        audioclip = AudioFileClip(path)
        audioclip.write_audiofile(os.path.join(temp_dir, name))
    else:
        print('Формат данного файла не поддерживается')
    return None


if __name__ == '__main__':
    import time
    from datetime import datetime

    # создадим временную папку для работы приложения в TEMP
    tmp_dir = os.path.join(tempfile.gettempdir(), 'Video Conspect')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    get_audio_from_file(path=r'test\IMG_1998.MOV',
                        temp_dir=tmp_dir,
                        name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    time.sleep(1)
    get_audio_from_file(path=r'test\Never Gonna Give You Up.mp4',
                        temp_dir=tmp_dir,
                        name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    time.sleep(1)
    get_audio_from_file(path=r'test\Never Gonna Give You Up.mp3',
                        temp_dir=tmp_dir,
                        name=datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
